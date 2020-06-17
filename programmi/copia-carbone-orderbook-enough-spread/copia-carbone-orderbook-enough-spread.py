import json
import logging
import os
import sys
from datetime import datetime

import websocket

# ________________roba che serve all'avvio________________
coppia = 'xrpeur'
FORMATO_DATA_ORA = "%d-%m-%Y %H:%M:%S"


def calcoloFeeOnPrice(price):
	fee = (price / 100) * 0.5
	return round(fee, 5)


def calculateMinPriceForFee(price):
	fee = calcoloFeeOnPrice(price)
	min_price = price + fee
	return round(min_price, 5)


def minProfitFeePrice(buy_price):
	min_sell_price_no_fee = calculateMinPriceForFee(buy_price)
	final_price_full_cycle = calculateMinPriceForFee(min_sell_price_no_fee)
	return final_price_full_cycle


def passa_output_al_log_file():
	logging.basicConfig(
		level=logging.INFO,
		filename=
		f"programmi/copia-carbone-orderbook-enough-spread/copia_da_bitstamp-orderbook-enough-spread_{coppia}.csv",
		filemode="a",
		format="%(asctime)s,%(message)s",
		datefmt=FORMATO_DATA_ORA
	)


def avvio(argv):
	passa_output_al_log_file()
	dati_da_Bitstamp_websocket()


# _______________parte con dati websocket___________________
def dati_da_Bitstamp_websocket():
	try:
		# questo mostra piu informazioni se True
		websocket.enableTrace(False)
		ws = websocket.WebSocketApp(
			"wss://ws.bitstamp.net", on_message=on_message, on_error=on_error, on_close=on_close
		)
		ws.on_open = on_open
		ws.run_forever()
	except KeyboardInterrupt:
		print("Closing...")
		sys.stdout.flush()
		ws.close()


def on_open(ws):
	"""Funzione all'aggancio del WebSocket

	Arguments:

		ws {boh} -- sono dei caratteri apparentemente inutili
		"""
	jsonString = json.dumps({
		"event": "bts:subscribe",
		"data": {
		"channel": f"order_book_{coppia}"
		}
	})
	# manda a bitstamp la richiesta di iscriversi al canale di eventi citato sopra
	ws.send(jsonString)
	print('Luce verde ')
	sys.stdout.flush()


def on_message(ws, message: str):
	try:
		if message:
			# la stringa message ha la stesso formato di un json quindi possiamo passarlo come tale per ottenere il Dict
			messageDict = json.loads(message)
			# PARE che appena si aggancia il socket manda un messaggio vuoto che fa crashare il bot
			if messageDict and messageDict['data']:
				sys.stdout.flush()

				#data = str(messageDict['data'])
				bids = messageDict['data']['bids'][:1]
				asks = messageDict['data']['asks'][:1]
				firstBid = float(bids[0][0])
				firstAsk = float(asks[0][0])
				spreadStr = str(round(firstAsk - firstBid, 5))
				minAskPrice = minProfitFeePrice(firstBid)
				if minAskPrice <= firstAsk:
					logging.info(spreadStr)
				#logging.info(f'{timestamp},{data}')
	except Exception as e:
		print(f'Exception:{e}')
		sys.stdout.flush()


def on_error(ws, error: str):
	print('Error:' + error)
	sys.stdout.flush()


def on_close(ws):
	print("### WebSocketclosed  ###")


avvio(sys.argv[1:])
