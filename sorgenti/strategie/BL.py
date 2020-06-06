import json
import logging
import os
import sys
from datetime import datetime

import utilita.gestoreRapporti as report
from costanti.api import API_TOKEN_HASH, TELEGRAM_ID
from costanti.costanti_unico import *
from piattaforme.bitstamp import bitstampRequestsRefactored as bitstamp
# from utilita.apriFile import commercialista, portafoglio, ultimo_id_ordine
from utilita import apriFileRefactored as managerJson
from utilita.telegramBot import TelegramBot

Fattore_Perdita = 0


def gestore(orderbook: dict):
	global Fattore_Perdita

	#todo- check if Order is pending? we use IOC/FOK so it shouldn't exist (credo ignori le flag!)
	try:
		# todo -SE NON USI IOC/FOK calcola con un criterio se necessario riassestare il prezzo del 'attuale ordine e quindi magari cancellarlo

		orders = managerJson.getOrders()
		orders_buy = []
		orders_sell = []
		for order in orders:
			if order['bos'] == "buy":
				orders_buy.append(order)
			if order['bos'] == "sell":
				orders_sell.append(order)

		if orders:
			for index, order in enumerate(orders):
				if order['order_id']:
					order_status = bitstamp.checkOrder(order['order_id'])
					if 'status' in order_status:
						managerJson.gestoreValoriJson([ 'orders', index, 'order_status'],
							order_status['status'])
						if order_status['status'] == "finished":
							managerJson.gestoreValoriJson([ 'orders', index, 'order_id'], 0)

							now = datetime.now()
							dt_string = now.strftime(FORMATO_DATA_ORA)
							report.JsonWrites(
								LOG_CARTELLA_PERCORSO + "/" + str(order['bos']) + "_" +
								str(order['order_id']) + ".json", "w+",
								dt_string + " order completed"
							)
							report.JsonWrites(
								LOG_CARTELLA_PERCORSO + "/check" + str(order['bos']) + "_" +
								str(order['order_id']) + ".json", "w+", dt_string + " CLOSE " +
								str(order['bos']).upper() + " " + str(order['order_id']) + " [" +
								str(order['price']) + "] " + str(order['amount']) + (
								VALUTA_SOLDI.upper()
								if order['bos'].lower() == "sell" else VALUTA_CRIPTO.upper()
								)
							)
							if order['bos'] == "sell":
								# _________________________ CALCULATED _________________________
								# soldi = managerJson.portafoglio()[-1]
								# managerJson.portafoglio(
								# 	"soldi", soldi + (order['amount'] * order['price'])
								# )
								# _________________________ ASKED _________________________
								balance = json.loads(bitstamp.getBalance())
								if balance and f"{VALUTA_SOLDI}_balance" in balance:
									report.JsonWrites(
										LOG_CARTELLA_PERCORSO + "/check" + str(order['bos']) + "_" +
										str(order['order_id']) + "_balance.json", "w+", balance
									)
									#cripto_balance = float(balance[f"{VALUTA_SOLDI}_balance"]) if f"{VALUTA_CRIPTO}_balance" in balance else None
									# fee = float( balance[ f"{COPPIA_DA_USARE_NOME}_fee" ] ) if f"{COPPIA_DA_USARE_NOME}_fee" in balance else None
									soldi_balance = float(
										balance[f"{VALUTA_SOLDI}_balance"]
									) if f"{VALUTA_SOLDI}_balance" in balance else None
									managerJson.portafoglio("soldi", soldi_balance)
								else:
									logging.error("Balance error: " + order['order_id'])
								managerJson.gestoreValoriJson([ 'orders', index ], '')

					else:
						if 'error' in order_status:
							logging.error(order_status['error'])
						else:
							logging.error(json.dumps(order_status))

		# todo- Check se ultimo ultimo_id_ordine() e' stato completato
		# if YES LOGGA: Ordine [buy|sell] completo al prezzo di N VALUTA_SOLDI per N VALUTA_CRIPTO di N VALUTA_CRIPTO
		cripto, soldi = managerJson.portafoglio()

		#primo index:identifica il ORDER
		#secondo index: identifica se Prezzo o Amount
		bids_price = orderbook['bids'][0][0]
		bids_amount = orderbook['bids'][0][1]

		asks_price = orderbook['asks'][0][0]
		asks_amount = orderbook['asks'][0][1]

		#todo- set minimum soldi of 25
		#todo- necessario? set minimum cripto of ? (c'e un minimo ma non ricordo quale sia)

		#controllo se mi permetto quell'order
		if asks_amount * asks_price >= soldi:
			# Compro
			my_amount = soldi / asks_price
			order_result = bitstamp.buyLimit(my_amount, asks_price, fok=True)
			managerJson.addOrder(
				amount=order_result['amount'],
				price=order_result['price'],
				order_id=order_result['id'],
				bos="buy"
			)
			# _________________________ CALCULATED _________________________
			# managerJson.portafoglio(
			# 	"soldi", soldi - (order_result['amount'] * order_result['price'])
			# )
			# _________________________ ASKED _________________________
			balance = json.loads(bitstamp.getBalance())
			if balance and f"{VALUTA_SOLDI}_balance" in balance:
				report.JsonWrites(
					LOG_CARTELLA_PERCORSO + "/buy_" + str(order_result['id']) + "_balance.json",
					"w+", balance
				)
				#cripto_balance = float(balance[f"{VALUTA_SOLDI}_balance"]) if f"{VALUTA_CRIPTO}_balance" in balance else None
				# fee = float( balance[ f"{COPPIA_DA_USARE_NOME}_fee" ] ) if f"{COPPIA_DA_USARE_NOME}_fee" in balance else None
				soldi_balance = float(
					balance[f"{VALUTA_SOLDI}_balance"]
				) if f"{VALUTA_SOLDI}_balance" in balance else None
				managerJson.portafoglio("soldi", soldi_balance)
			else:
				logging.error("Balance error: " + order_result['id'])

			report.JsonWrites(
				LOG_CARTELLA_PERCORSO + "/buy_" + str(order_result['id']) + ".json", "w+",
				dt_string + " OPEN BUY " + str(order_result['id']) + " [" +
				str(order_result['price']) + "] " + str(soldi) + " -> " + str(my_amount) + "==" +
				str(order_result['amount'])
			)
			del order_result

		if orders_buy:
			for order in orders_buy:

				if order['order_status'] == "finished" and order[
					'price'] < bids_price and bids_amount >= order['amount']:
					# Vendo
					order_result = bitstamp.sellLimit(order['amount'], bids_price, fok=True)
					managerJson.addOrder(
						amount=order_result['amount'],
						price=order_result['price'],
						order_id=order_result['id'],
						bos="sell"
					)
					report.JsonWrites(
						LOG_CARTELLA_PERCORSO + "/sell_" + str(order_result['id']) + ".json", "w+",
						dt_string + " OPEN SELL " + str(order_result['id']) + " [" +
						str(order_result['price']) + "] " + str(soldi) + " -> " + str(my_amount) +
						"==" + str(order_result['amount'])
					)
					del order_result

	except Exception as e:
		raise e
	finally:
		# Aggiorno l'ultimo valore
		managerJson.commercialista("ultimo_valore", orderbook)


def forOrderCheck(data):
	buy_order_id = data['buy_order_id']
	sell_order_id = data['sell_order_id']
	amount = data['amount']

	#todo- if ultimo_id_ordine() NOT presente entrambi gli ID,allora non e' stato completato
	#else:
	# aggiorna valori.json togliendo l ID
	# synca l amount per creare la frazione di order
	pass


#if tg_bot:
#todo- printa tutti i reason

#	tg_bot.sendMessage(TELEGRAM_ID, result['reason']['__all__'][0])
