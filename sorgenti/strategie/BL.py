import json
import logging
import os
import sys
from datetime import datetime

import utilita.gestoreRapporti as report
from costanti.api import API_TOKEN_HASH, TELEGRAM_ID
from costanti.costanti_unico import *
from piattaforme.bitstamp import bitstampRequests as bitstamp
# from utilita.apriFile import commercialista, portafoglio, ultimo_id_ordine
from utilita import apriFile as managerJson
from utilita.telegramBot import TelegramBot

Fattore_Perdita = 0

force_buy = False
force_sell = False


def gestore(orderbook: dict):
	global Fattore_Perdita, force_sell, force_buy

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
					order_status = bitstamp.checkOrder(order['order_id'])
					# Se nella risposta c'è lo stato dell'ordine
					if 'status' in order_status:
						# Aggiorno lo stato dell'ordine nel mio json
						managerJson.gestoreValoriJson([ 'orders', index, 'order_status'],
							order_status['status'])
						# Se lo stato è finished
						if order_status['status'] == "finished":
							# Cancello l'ID dell'ordine in quanto già easudito
							managerJson.gestoreValoriJson([ 'orders', index, 'order_id'], 0)

							# Ottengo il timestamp attuale
							now = datetime.now()
							# Converto il timestamp attuale in un datetime in formato umano
							dt_string = now.strftime(FORMATO_DATA_ORA)

							# Salvo la risposta del checkOrder in un json per Debug
							report.JsonWrites(
								LOG_CARTELLA_PERCORSO + "/check" + str(order['bos']) + "_" +
								str(order['order_id']) + ".json", "w+", dt_string + " CLOSE " +
								str(order['bos']).upper() + " " + str(order['order_id']) + " [" +
								str(order['price']) + "] " + str(order['amount']) + (
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
									# Aggiorno il valore dei soldi nel mio json
									managerJson.portafoglio("soldi", soldi_balance)
								else:
									# Se non c'è quello che mi aspetto nella risposta,
									# c'è stato un errore e quindi lo loggo
									logging.error("Balance error: " + order['order_id'])
								# Cancello l'ordine dal mio json
								managerJson.gestoreValoriJson([ 'orders', index ], '')

					else:
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
		cripto, soldi = managerJson.portafoglio()

		#primo index:identifica il ORDER
		#secondo index: identifica se Prezzo o Amount

		# Estraggo i valori dall'orderbook
		# dal primo bids (proposta d'acquisto)
		# il primo valore è il price (prezzo)
		bids_price = float(orderbook['bids'][0][0])
		# il secondo valore è l'amount (quantità)
		bids_amount = float(orderbook['bids'][0][1])

		# dal primo asks (proposta di vendita)
		# il primo valore è il price (prezzo)
		asks_price = float(orderbook['asks'][0][0])
		# il secondo valore è l'amount (quantità)
		asks_amount = float(orderbook['asks'][0][1])

		#todo- set minimum soldi of 25
		#todo- necessario? set minimum cripto of ? (c'e un minimo ma non ricordo quale sia)

		# Se ho abbastanza soldi per fare un'ordine minimo (minimo per la piattaforma)
		if soldi > MINIMUM_ORDER:
			# Resetto l'acquisto forzato (al momento non utilizzato)
			force_buy = False
			## Compro
			# Calcolo quanta cripto posso comprare coi miei soldi a questo prezzo (asks price)
			my_amount = soldi / asks_price
			# Se la cripto che potrei comprare è maggiore di quella che potrei ottenere da quell'ordine,
			# gli compro tutta quella che mi offre
			if my_amount > asks_amount:
				my_amount = asks_amount

			# Faccio l'ordine
			order_result = bitstamp.buyLimit(my_amount, asks_price, fok=True)
			# Aggiungo l'apertura dell'ordine al mio json
			managerJson.addOrder(
				amount=order_result['amount'],
				price=order_result['price'],
				order_id=order_result['id'],
				bos="buy"
			)
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

			# Salvo la risposta dell'ordine di acquisto in un file per debug
			report.JsonWrites(
				LOG_CARTELLA_PERCORSO + "/buy_" + str(order_result['id']) + ".json", "w+",
				dt_string + " OPEN BUY " + str(order_result['id']) + " [" +
				str(order_result['price']) + "] " + str(soldi) + " -> " + str(my_amount) + "==" +
				str(order_result['amount'])
			)
			# Cancello la variabile con la risposta dell'ordine di acquisto
			# per evitare problemi
			del order_result

		# Se ci sono ordini di acquisto nel mio json
		if orders_buy:
			# Per ogni ordine
			for order in orders_buy:

				# Se (l'ordine in causa è stato esaudito o è senza ID perchè è stato finito)
				# e (il prezzo d'acquisto è minore del prezzo con cui venderei o sto forzando la vendita)
				# e le cripto che mi comprerebbero sono maggiori di quelle che ho [quindi me le comprano tutte])
				if (order['order_status'] == "finished" or not order['order_id']
					) and (order['price'] < bids_price) and bids_amount >= order['amount']:
					# Resetto la vendita forzata
					force_sell = False
					## Vendo
					# Faccio l'ordine
					order_result = bitstamp.sellLimit(order['amount'], bids_price, fok=True)
					# Aggiungo l'apertura dell'ordine al mio json
					managerJson.addOrder(
						amount=order_result['amount'],
						price=order_result['price'],
						order_id=order_result['id'],
						bos="sell"
					)
					# Salvo la risposta dell'ordine di acquisto in un file per debug
					report.JsonWrites(
						LOG_CARTELLA_PERCORSO + "/sell_" + str(order_result['id']) + ".json", "w+",
						dt_string + " OPEN SELL " + str(order_result['id']) + " [" +
						str(order_result['price']) + "] " + str(soldi) + " -> " + str(my_amount) +
						"==" + str(order_result['amount'])
					)
					# Cancello la variabile con la risposta dell'ordine di acquisto
					# per ordine e evitare problemi
					del order_result

	except Exception as ex:
		# In caso di eccezioni printo e loggo tutti i dati disponibili
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(ex, exc_type, fname, exc_tb.tb_lineno)
		logging.error(ex)
	finally:
		# Aggiorno l'ultimo valore
		managerJson.commercialista("ultimo_valore", orderbook)


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
