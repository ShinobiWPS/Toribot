import json
import logging
import os
import sys

import websocket

COPPIA_DA_USARE_NOME = 'btcgbp'
ws_ob_open = None

CALLBACK_EXTERNAL = None


def startWebSocketOrderBook(callback):
	global CALLBACK_EXTERNAL
	CALLBACK_EXTERNAL = callback
	try:
		# Debug: questo mostra piu informazioni se True
		websocket.enableTrace(False)
		# Inizializzo il websocket
		ws_ob = websocket.WebSocketApp(
			"wss://ws.bitstamp.net",
			on_message=WSOB_on_message,
			on_error=WSOB_on_error,
			on_close=WSOB_on_close
		)
		# Imposto la funzione on_open, eseguita all'aggancio del websocket
		ws_ob.on_open = WSOB_on_open
		# Eseguo il websocket come demone (~ in background)
		ws_ob.run_forever()
	except KeyboardInterrupt:
		# in caso di eccezioni chiudo il websocket
		ws_ob.close()
	except Exception as ex:
		# In caso di eccezioni printo e loggo tutti i dati disponibili
		exc_type, unused_exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(ex, exc_type, fname, exc_tb.tb_lineno)
		logging.error(ex)


# Funzione all'aggancio del WebSocket per i orderbook
def WSOB_on_open(ws):
	"""Funzione all'aggancio del WebSocket"""
	global ws_ob_open
	# Imposto la variabile per sapere che il websocket è aperto
	ws_ob_open = True
	# Imposto il json della richiesta d'iscrizione al canale di eventi
	jsonString = json.dumps({
		"event": "bts:subscribe",
		"data": {
		"channel": f"order_book_{COPPIA_DA_USARE_NOME}"
		}
	})
	# Invio la richiesta d'iscrizione alla piattaforma
	ws.send(jsonString)


# Funzione alla ricezione di dati dal websocket per l'orderbook
def WSOB_on_message(ws, message: str):
	# Decodifico i dati ricevuti come json, convertendoli in un oggetto
	messageDict = json.loads(message)
	# Verifico che nel messaggio ricevuto ci siano i dati che mi aspetto
	if 'data' in messageDict and messageDict['data']:
		CALLBACK_EXTERNAL(messageDict['data'])


# Funzione in caso di errori col websocket per il orderbook
def WSOB_on_error(ws, error: str):
	global ws_ob_open
	# Imposto la variabile per sapere che il websocket è chiuso
	ws_ob_open = False
	# Printo l'errore che ha chiuso il websocket
	print(error)
	# Loggo come errore l'errore che ha chiuso il websocket
	logging.error(error)


# Funzione alla chiusura del websocket per il orderbook
def WSOB_on_close(ws):
	global ws_ob_open
	# Printo un messaggio per avvertire della chiusura del websocket per il orderbook
	print("### WebSocket Orderbook closed ###")
