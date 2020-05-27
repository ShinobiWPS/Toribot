import json
import logging
import os
import sys
from datetime import datetime

import websocket

from costanti.formato_data_ora import FORMATO_DATA_ORA

# ________________roba che serve all'avvio________________


def passa_output_al_log_file():
	logging.basicConfig(
	    level=logging.INFO,
	    filename="programmi/copia-carbone-orderbook/copia_da_bitstamp-orderbook.csv",
	    filemode="a",
	    format="%(asctime)s,%(message)s",
	    datefmt=FORMATO_DATA_ORA
	)


def avvio(argv):
	print(os.getcwd())
	passa_output_al_log_file()
	dati_da_Bitstamp_websocket()


# _______________parte con dati websocket___________________
def dati_da_Bitstamp_websocket():
	try:
		# questo mostra piu informazioni se True
		websocket.enableTrace(False)
		ws = websocket.WebSocketApp(
		    "wss://ws.bitstamp.net",
		    on_message=on_message,
		    on_error=on_error,
		    on_close=on_close
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
	        "channel": "order_book_xrpeur"
	    }
	})
	# manda a bitstamp la richiesta di iscriversi al canale di eventi citato sopra
	ws.send(jsonString)
	print('Luce verde 🟢🟢🟢')
	sys.stdout.flush()


def on_message(ws, message: str):
	try:
		if message:
			# la stringa message ha la stesso formato di un json quindi possiamo passarlo come tale per ottenere il Dict
			messageDict = json.loads(message)
			# PARE che appena si aggancia il socket manda un messaggio vuoto che fa crashare il bot
			if messageDict and messageDict['data']:
				sys.stdout.flush()

				timestamp = str(messageDict['data']['timestamp'])
				data = str(messageDict['data'])
				logging.info(f'{timestamp},{data}')
	except Exception as e:
		print(f'Exception:{e}')
		sys.stdout.flush()


def on_error(ws, error: str):
	print(error)
	print('❌')
	sys.stdout.flush()


def on_close(ws):
	print("### WebSocketclosed 🔴🔴🔴 ###")


avvio(sys.argv[1:])
