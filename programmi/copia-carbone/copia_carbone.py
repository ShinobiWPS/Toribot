import os
import sys
import json

import websocket

# ______________________________________roba che serve all'avvio____________________


def avvio(argv):
	dati_da_Bitstamp_websocket()


# ______________________________________parte con dati websoket______________________________________
def dati_da_Bitstamp_websocket():
	try:
		# questo mostra piu informazioni se True
		websocket.enableTrace(False)
		ws = websocket.WebSocketApp("wss://ws.bitstamp.net",
		                            on_message=on_message,
		                            on_error=on_error,
		                            on_close=on_close)
		ws.on_open = on_open
		ws.run_forever()
	except KeyboardInterrupt:
		ws.close()


def on_open(ws):
	"""Funzione all'aggancio del WebSocket

	Arguments:
									ws {tipo_boh} -- sono dei caratteri apparentemente inutili
																	"""
	jsonString = json.dumps({
	    "event": "bts:subscribe",
	    "data": {
	        "channel": "live_trades_xrpeur"
	    }
	})
	# manda a bitstamp la richiesta di iscriversi al canale di eventi 'live_trades_xrpeur'
	ws.send(jsonString)
	print('Luce verde 🟢🟢🟢')


def on_message(ws, message: str):
	# la stringa message ha la stesso formato di un json quindi possiamo passarlo come tale per ottenere il Dict
	messageDict = json.loads(message)
	# PARE che appena si aggancia il socket manda un messaggio vuoto che fa crashare il bot
	if messageDict['data'] != {}:
		# questo print serve solo a noi per lavorare
		attuale = messageDict['data']['price']
		with open('programmi/copia-carbone/da_bitstamp.csv', 'a') as jsonFile:
			json.dump(attuale, jsonFile)


def on_error(ws, error: str):
	print(error)
	print('❌')


def on_close(ws):
	print("### WebSocketclosed 🔴🔴🔴 ###")


avvio(sys.argv[1:])
