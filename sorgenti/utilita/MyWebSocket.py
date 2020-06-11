import json
import logging
import os
import sys

import websocket


class MyWebSocket(object):

	ws = None
	WS_URL = None  # "wss://ws.bitstamp.net"
	WS_EVENT = None  # "bts:subscribe"
	WS_CHANNEL = None  # f"live_trades_{COPPIA_DA_USARE_NOME}"
	trace = False
	isOpen = False

	def __init__(
		self,
		run=True,
		WS_URL=None,
		WS_EVENT=None,
		WS_CHANNEL=None,
		trace=False,
		callbackOnMessage=None,
		callbackOnClose=None,
		callbackOnError=None
	):
		if not WS_URL:
			raise Exception("Missing WS URL")
		if not WS_EVENT:
			raise Exception("Missing WS EVENT")
		if not WS_CHANNEL:
			raise Exception("Missing WS CHANNEL")

		self.WS_URL = WS_URL
		self.WS_EVENT = WS_EVENT
		self.WS_CHANNEL = WS_CHANNEL
		self.callbackOnMessage = callbackOnMessage
		self.callbackOnClose = callbackOnClose
		self.callbackOnError = callbackOnError
		self.ws = None
		self.trace = trace
		self.isOpen = False

		self.start(run)

	def __del__(self):
		if self.ws:
			self.ws.close()

	# Funzione d'inizializzazione del websocket per i valori del trading
	def start(self, run=False):
		try:
			# Debug: questo mostra piu informazioni se True
			websocket.enableTrace(self.trace)
			# Inizializzo il websocket
			self.ws = websocket.WebSocketApp(
				self.WS_URL,
				on_message=lambda ws, msg: self.on_message(ws, msg),
				on_error=lambda ws, msg: self.on_error(ws, msg),
				on_close=lambda ws: self.on_close(ws),
				on_open=lambda ws: self.on_open(ws)
			)
			if run:
				self.run_forever()

		except KeyboardInterrupt:
			# in caso di eccezioni chiudo il websocket
			self.ws.close()
		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			exc_type, unused_exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(ex, exc_type, fname, exc_tb.tb_lineno)
			logging.error(ex)

	def run_forever(self):
		# Eseguo il websocket come demone (~ in background)
		try:
			self.ws.run_forever()
		except Exception as ex:
			exc_type, unused_exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(ex, exc_type, fname, exc_tb.tb_lineno)
			logging.error(ex)

	def close(self):
		self.ws.close()

	# Funzione all'aggancio del WebSocket per i trade
	def on_open(self, ws):
		try:
			# Imposto la variabile per sapere che il websocket è aperto
			self.isOpen = True
			# Imposto il json della richiesta d'iscrizione al canale di eventi
			jsonString = json.dumps({
				"event": self.WS_EVENT,
				"data": {
				"channel": self.WS_CHANNEL
				}
			})
			# Invio la richiesta d'iscrizione alla piattaforma
			ws.send(jsonString)
		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			exc_type, unused_exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(ex, exc_type, fname, exc_tb.tb_lineno)
			logging.error(ex)

	# Funzione alla ricezione di dati dal websocket per il trade
	def on_message(self, ws, message: str):
		try:
			# Decodifico i dati ricevuti come json, convertendoli in un oggetto
			messageDict = json.loads(message)
			self.callbackOnMessage(messageDict)
		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			exc_type, unused_exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(ex, exc_type, fname, exc_tb.tb_lineno)
			logging.error(ex)

	# Funzione in caso di errori col websocket per il trade
	def on_error(self, ws, error: str):
		try:
			# Imposto la variabile per sapere che il websocket è chiuso
			self.isOpen = False
			# Printo l'errore che ha chiuso il websocket
			print(error)
			# Loggo come errore l'errore che ha chiuso il websocket
			logging.error(error)
			self.callbackOnError(error)
		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			exc_type, unused_exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(ex, exc_type, fname, exc_tb.tb_lineno)
			logging.error(ex)

	# Funzione alla chiusura del websocket per il trade
	def on_close(self, ws):
		try:
			# Imposto la variabile per sapere che il websocket è chiuso
			self.isOpen = False
			# Printo un messaggio per avvertire della chiusura del websocket per il trade
			print("### WebSocket Trade closed ###")
			self.callbackOnClose()
		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			exc_type, unused_exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(ex, exc_type, fname, exc_tb.tb_lineno)
			logging.error(ex)
