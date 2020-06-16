import json
import logging
import math
import os
import sched
import sys
import time
from datetime import datetime

import utilita.gestoreRapporti as report
from costanti.api import API_TOKEN_HASH, TELEGRAM_ID
from costanti.costanti_unico import *
from piattaforme.bitstamp import bitstampRequests as bitstamp
# from utilita.apriFile import commercialista, portafoglio, ultimo_id_ordine
from utilita import apriFile as managerJson
from utilita.calcoli import (firstOrderAmount, firstOrderPrice, prezzoInPrimaFila)
from utilita.infoAboutError import getErrorInfo
from utilita.Statistics import Statistics
from utilita.telegramBot import TelegramBot

Fattore_Perdita = 0

force_buy = False
force_sell = False
closing = False

GOOD_PRICE_BID, GOOD_PRICE_ASK = 0, 0


def core(
	orderbook: dict,
	orderbook_history=managerJson.commercialista()[0],
	MyStat=Statistics(),
	tg_bot=TelegramBot(False),
):
	global Fattore_Perdita, force_sell, force_buy, closing

	#todo- check if Order is pending? we use IOC/FOK so it shouldn't exist (credo ignori le flag!)
	try:
		# todo -SE NON USI IOC/FOK calcola con un criterio se necessario riassestare il prezzo del 'attuale ordine e quindi magari cancellarlo

		# Ottengo gli ordini dal mio json
		orders = managerJson.getOrders()
		orders_buy = []
		orders_sell = []
		# Divido gli ordini in
		for order in orders:
			# ordini d'acquisto
			if order['bos'] == "buy":
				orders_buy.append(order)
			# e ordini di vendita
			if order['bos'] == "sell":
				orders_sell.append(order)

		# Se ci sono ordini
		if orders:
			# Per ogni ordine
			for index, order in enumerate(orders):
				# Se l'ordine ha un ID
				if order['order_id']:
					# Chiedo lo stato dell'ordine alla piattaforma
					order_status = json.loads(bitstamp.checkOrder(order['order_id']))
					# Se nella risposta c'è lo stato dell'ordine
					if 'status' in order_status:
						# Aggiorno lo stato dell'ordine nel mio json
						managerJson.gestoreValoriJson([ 'orders', index, 'order_status'],
							order_status['status'])
						# Salvo la risposta del checkOrder in un json per Debug
						report.JsonWrites(
							LOG_CARTELLA_PERCORSO + "/check" + str(order['bos']) + "_" +
							str(order['order_id']) + ".json", "w+", order_status
						)
						# Se lo stato è finished
						if order_status['status'].lower() == "finished":
							# Cancello l'ID dell'ordine in quanto già easudito
							managerJson.gestoreValoriJson([ 'orders', index, 'order_id'], 0)

							try:
								if tg_bot:
									tg_bot.sendMessage(
										tg_bot.Admins_ID, "" + order['bos'].lower() + " success"
									)
							except Exception as ex:
								# In caso di eccezioni printo e loggo tutti i dati disponibili
								exc_type, unused_exc_obj, exc_tb = sys.exc_info()
								fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
								print(ex, exc_type, fname, exc_tb.tb_lineno)
								logging.error(ex)

							# Ottengo il timestamp attuale
							now = datetime.now()
							# Converto il timestamp attuale in un datetime in formato umano
							dt_string = now.strftime(FORMATO_DATA_ORA)

							# Aggiungo al report la chiusura dell'ordine
							report.FileAppend(
								TRADING_REPORT_FILENAME, dt_string + " CLOSE " +
								str(order['bos']).upper() + " " + str(order['order_id']) + " [" +
								str(order['price']) + "] " + str(order['amount']) + " " + (
								VALUTA_SOLDI.upper()
								if order['bos'].lower() == "sell" else VALUTA_CRIPTO.upper()
								)
							)
							# Se è un ordine di vendita
							if order['bos'] == "sell":
								# Posso scegliere se i soldi spesi per l'ordine sottrarli calcolando la spesa
								# o chiedendo direttamente il balance alla piattaforma
								# _________________________ CALCULATED _________________________
								# soldi = managerJson.portafoglio()[-1]
								# managerJson.portafoglio(
								# 	"soldi", soldi + (order['amount'] * order['price'])
								# )
								# _________________________ ASKED _________________________
								# Chiedo il balance
								balance = json.loads(bitstamp.getBalance())
								# Se la richiesta è andata a buon fine
								if balance and f"{VALUTA_SOLDI}_balance" in balance:
									# Salvo la risposta in un file per debug
									report.JsonWrites(
										LOG_CARTELLA_PERCORSO + "/check" + str(order['bos']) + "_" +
										str(order['order_id']) + "_balance.json", "w+", balance
									)
									#cripto_balance = float(balance[f"{VALUTA_CRIPTO}_balance"]) if f"{VALUTA_CRIPTO}_balance" in balance else None
									# fee = float( balance[ f"{COPPIA_DA_USARE_NOME}_fee" ] ) if f"{COPPIA_DA_USARE_NOME}_fee" in balance else None
									# Estraggo il valore dei soldi dalla risposta: soldi_balance
									soldi_balance = float(
										balance[f"{VALUTA_SOLDI}_balance"]
									) if f"{VALUTA_SOLDI}_balance" in balance else None
									# Aggiorno le statistiche
									MyStat.strategy_soldi_update(soldi_balance)
									# Aggiorno il valore dei soldi nel mio json
									managerJson.portafoglio("soldi", soldi_balance)
								else:
									# Se non c'è quello che mi aspetto nella risposta,
									# c'è stato un errore e quindi lo loggo
									logging.error("Balance error: " + order['order_id'])
								# Cancello l'ordine dal mio json
								managerJson.gestoreValoriJson([ 'orders', index ], '')

					else:
						# Se è un ordine non finished e failato
						if order['order_status'].lower(
						) != "finished" and 'error' in order_status and order_status[
							'error'] == "Order not found":
							# Aggiorno le statistiche
							MyStat.strategy_soldi_update(order['amount'] * order['price'])
							# Aggiorno il valore dei soldi nel mio json
							managerJson.portafoglio("soldi", order['amount'] * order['price'])
							# Cancello l'ordine
							managerJson.gestoreValoriJson([ 'orders', index ], '')
						# Se nella risposta del checkOrder non c'è lo status dell'ordine,
						# ma c'è il motivo dell'errore
						if 'error' in order_status:
							# Loggo il motivo dell'errore
							logging.error(order_status['error'])
						else:
							# Se l'errore è sconosciuto loggo tutta la risposta
							logging.error(json.dumps(order_status))

		# todo- Check se ultimo ultimo_id_ordine() e' stato completato
		# if YES LOGGA: Ordine [buy|sell] completo al prezzo di N VALUTA_SOLDI per N VALUTA_CRIPTO di N VALUTA_CRIPTO
		unused_cripto, soldi = managerJson.portafoglio()

		#primo index:identifica il ORDER
		#secondo index: identifica se Prezzo o Amount

		# Estraggo i valori dall'orderbook
		# dal primo bids (proposta d'acquisto)
		# il primo valore è il price (prezzo)
		bids_price = firstOrderPrice(orderbook['bids'])
		# il secondo valore è l'amount (quantità)
		bids_amount = firstOrderAmount(orderbook['bids'])

		# dal primo asks (proposta di vendita)
		# il primo valore è il price (prezzo)
		asks_price = firstOrderPrice(orderbook['asks'])
		# il secondo valore è l'amount (quantità)
		asks_amount = firstOrderAmount(orderbook['asks'])

		asks_history = getAsksMemory(orderbook_history)
		bids_history = getBidsMemory(orderbook_history)

		asks_percentage = getAsksPercentage(asks_history, asks_price)
		bids_percentage = getBidsPercentage(bids_history, bids_price)

		# Aggiorno le statistiche
		MyStat.strategy_spread_duration_update(asks_price - bids_price)

		#todo- necessario? set minimum cripto of ? (c'e un minimo ma non ricordo quale sia)

		# Debug
		# print("A" + str(asks_percentage) + str('%'))
		# print("B" + str(bids_percentage) + str('%'))

		# Se ho abbastanza soldi per fare un'ordine minimo (minimo per la piattaforma)
		if (soldi > MINIMUM_ORDER_VALUE and asks_percentage[0] > 70
			and asks_percentage[1] > 10) or (soldi > MINIMUM_ORDER_VALUE and force_buy):
			# Resetto l'acquisto forzato (al momento non utilizzato)
			force_buy = False
			## Compro
			# Calcolo quanta cripto posso comprare coi miei soldi a questo prezzo (asks price)
			my_amount = truncate(soldi / asks_price, 8)
			# Se la cripto che potrei comprare è maggiore di quella che potrei ottenere da quell'ordine,
			# gli compro tutta quella che mi offre
			if float(my_amount) > float(asks_amount):
				my_amount = truncate(float(asks_amount), 8)

			# Faccio l'ordine
			order_result = json.loads(bitstamp.buyLimit(my_amount, asks_price))
			# Se l'ordine è andato bene, perchè ha una delle chiavi corrette
			if 'id' in order_result:
				# Salvo la risposta dell'ordine di acquisto in un file per debug
				# Ottengo il timestamp attuale
				now = datetime.now()
				# Converto il timestamp in un datetime in formato umano
				dt_string = now.strftime(FORMATO_DATA_ORA)
				report.JsonWrites(
					LOG_CARTELLA_PERCORSO + "/buy_" + str(order_result['id']) + ".json", "w+",
					order_result
				)
				report.FileAppend(
					TRADING_REPORT_FILENAME, dt_string + " OPEN BUY " + str(order_result['id']) +
					" [" + str(order_result['price']) + "] " + str(soldi) + " -> " +
					str(my_amount) + "==" + str(order_result['amount'])
				)
				# Aggiungo l'apertura dell'ordine al mio json
				managerJson.addOrder(
					amount=float(order_result['amount']),
					price=float(order_result['price']),
					order_id=order_result['id'],
					bos="buy"
				)
				# Aggiorno le statistiche
				MyStat.strategy_buy_duration_update()
				# Posso scegliere se i soldi spesi per l'ordine sottrarli calcolando la spesa
				# o chiedendo direttamente il balance alla piattaforma
				# _________________________ CALCULATED _________________________
				# managerJson.portafoglio(
				# 	"soldi", soldi - (order_result['amount'] * order_result['price'])
				# )
				# _________________________ ASKED _________________________
				# Chiedo il balance
				balance = json.loads(bitstamp.getBalance())
				# Se la richiesta è andata a buon fine
				if balance and f"{VALUTA_SOLDI}_balance" in balance:
					# Salvo la risposta in un file per debug
					report.JsonWrites(
						LOG_CARTELLA_PERCORSO + "/buy_" + str(order_result['id']) + "_balance.json",
						"w+", balance
					)
					# cripto_balance = float(balance[f"{VALUTA_SOLDI}_balance"]) if f"{VALUTA_CRIPTO}_balance" in balance else None
					# fee = float( balance[ f"{COPPIA_DA_USARE_NOME}_fee" ] ) if f"{COPPIA_DA_USARE_NOME}_fee" in balance else None
					# Estraggo il valore dei soldi dalla risposta: soldi_balance
					soldi_balance = float(
						balance[f"{VALUTA_SOLDI}_balance"]
					) if f"{VALUTA_SOLDI}_balance" in balance else None
					# Aggiorno il valore dei soldi nel mio json
					managerJson.portafoglio("soldi", soldi_balance)
				else:
					# Se non c'è quello che mi aspetto nella risposta,
					# c'è stato un errore e quindi lo loggo
					logging.error("Balance error: " + order_result['id'])

				# Cancello la variabile con la risposta dell'ordine di acquisto
				# per evitare problemi
			# Se c'è un errore con l'ordine
			elif 'reason' in order_result:
				# Loggo
				logging.error("Buy error: " + json.dumps(order_result['reason']))
				print("Buy error: ", json.dumps(order_result))
			else:
				# Loggo
				logging.error("Buy error")
				print("Buy error: ", json.dumps(order_result))
			del order_result

		# Se ci sono ordini di acquisto nel mio json
		if orders_buy:
			# Per ogni ordine
			for order in orders_buy:

				# Se (l'ordine in causa è stato esaudito o è senza ID perchè è stato finito)
				# e (il prezzo d'acquisto è minore del prezzo con cui venderei o sto forzando la vendita)
				# e le cripto che mi comprerebbero sono maggiori di quelle che ho [quindi me le comprano tutte])
				if (order['order_status'].lower() == "finished" or not order['order_id']) and ((
					float(order['price']) < float(bids_price) and bids_percentage[0] >= 10
					and bids_percentage[1] >= 70
				) or force_sell or closing) and float(bids_amount) >= float(order['amount']):
					# Resetto la vendita forzata
					force_sell = False
					## Vendo
					# Faccio l'ordine
					order_result = json.loads(
						bitstamp.sellLimit(
						truncate(float(order['amount']), 8), bids_price, fok=True
						)
					)
					# Se l'ordine è andato bene, perchè ha una delle chiavi corrette
					if 'id' in order_result:
						# Aggiungo l'apertura dell'ordine al mio json
						managerJson.removeOrder(chiave='timestamp', valore=order['timestamp'])
						managerJson.addOrder(
							amount=float(order_result['amount']),
							price=float(order_result['price']),
							order_id=order_result['id'],
							bos="sell"
						)
						# Salvo la risposta dell'ordine di acquisto in un file per debug
						# Ottengo il timestamp attuale
						now = datetime.now()
						# Converto il timestamp in un datetime in formato umano
						dt_string = now.strftime(FORMATO_DATA_ORA)
						report.JsonWrites(
							LOG_CARTELLA_PERCORSO + "/sell_" + str(order_result['id']) + ".json",
							"w+", order_result
						)
						report.FileAppend(
							TRADING_REPORT_FILENAME, dt_string + " OPEN SELL " +
							str(order_result['id']) + " [" + str(order_result['price']) + "] " +
							str(soldi) + " -> " + str(order_result['amount'])
						)
						# Aggiorno le statistiche
						MyStat.strategy_sell_duration_update()
					elif 'reason' in order_result:
						# Loggo
						logging.error("Sell error: " + json.dumps(order_result['reason']))
						print("Sell error: ", json.dumps(order_result))
					else:
						# Loggo
						logging.error("Sell generic error")
						print("Sell generic error: ", json.dumps(order_result))
					# Cancello la variabile con la risposta dell'ordine di acquisto
					# per ordine e evitare problemi
					del order_result
		print("Doing stuff...")
		s.enter(TIMER, 1, core, ( sc, ))
	except Exception as ex:
		# In caso di eccezioni printo e loggo tutti i dati disponibili
		getErrorInfo(ex)


s = sched.scheduler(time.time, time.sleep)
s.enter(TIMER, 1, core, ( s, ))


def gestore(
	orderbook: dict,
	orderbook_history=managerJson.commercialista()[0],
	MyStat=Statistics(),
	tg_bot=TelegramBot(False)
):
	if CORE_IS_NOT_RUNNING:
		s.run()
	rivalutaPrezzi(orderbook)


def rivalutaPrezzi(orderbook: dict):
	global GOOD_PRICE_ASK
	global GOOD_PRICE_BID
	GOOD_PRICE_BID, GOOD_PRICE_ASK = prezzoInPrimaFila(
		orderbook['bids'],
		orderbook['asks'],
	)

	#todo- place buy order open

	#todo- on buy-order done,
	# take buy_price, amount and pass to calcoloPrezziByDelta()


def getAsksMemory(orderbook_history=managerJson.commercialista()[0]):
	all_asks = []
	if orderbook_history:
		for mem_row in orderbook_history:
			for asks in range(len(mem_row['asks'])):
				all_asks.append(mem_row['asks'][asks][0])
		return all_asks
	return None


def getBidsMemory(orderbook_history=managerJson.commercialista()[0]):
	all_bids = []
	if orderbook_history:
		for mem_row in orderbook_history:
			for bids in range(len(mem_row['bids'])):
				all_bids.append(mem_row['bids'][bids][0])
		return all_bids
	return None


def getAsksPercentage(asks=getAsksMemory(managerJson.commercialista()[0]), my_value=0):
	if asks:
		up_len = len([ v for v in asks if float(my_value) < float(v) ])
		dw_len = len([ v for v in asks if float(my_value) > float(v) ])
		return [up_len / len(asks) * 100, dw_len / len(asks) * 100]
	return None


def getBidsPercentage(bids=getBidsMemory(managerJson.commercialista()[0]), my_value=0):
	if bids:
		up_len = len([ v for v in bids if float(my_value) < float(v) ])
		dw_len = len([ v for v in bids if float(my_value) > float(v) ])
		return [up_len / len(bids) * 100, dw_len / len(bids) * 100]
	return None


# def forOrderCheck(data):
# 	buy_order_id = data['buy_order_id']
# 	sell_order_id = data['sell_order_id']
# 	amount = data['amount']
#
# 	#todo- if ultimo_id_ordine() NOT presente entrambi gli ID,allora non e' stato completato
# 	#else:
# 	# aggiorna valori.json togliendo l ID
# 	# synca l amount per creare la frazione di order
# 	pass

#if tg_bot:
#todo- printa tutti i reason

#	tg_bot.sendMessage(TELEGRAM_ID, result['reason']['__all__'][0])


def truncate(number, digits) -> float:
	stepper = 10.0**digits
	return math.trunc(stepper * number) / stepper
