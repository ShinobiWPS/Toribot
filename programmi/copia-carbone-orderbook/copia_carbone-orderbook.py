import json
import logging
import sys
import time

import websocket

from costanti.costanti_unico import (
	FORMATO_DATA_ORA, WEBSOCKET_AUTORECONNECT, WEBSOCKET_AUTORECONNECT_RETRIES
)
from utilita.infoAboutError import getErrorInfo
from utilita.MyWebSocket import MyWebSocket

# ________________roba che serve all'avvio________________
coppia = 'btcgbp'
BITSTAMP_WEBSOCKET_URL = "wss://ws.bitstamp.net"
BITSTAMP_WEBSOCKET_EVENT = "bts:subscribe"
BITSTAMP_WEBSOCKET_CHANNEL_TRADE = f"live_trades_{coppia}"
BITSTAMP_WEBSOCKET_CHANNEL_ORDERBOOK = f"order_book_{coppia}"
_counterAutoReconnect = 0


def onWSOBMessage(messageDict):
	if _counterAutoReconnect:
		AutoReconnect(None, resetCounter=True)
	try:
		# Verifico che nel messaggio ricevuto ci siano i dati che mi aspetto
		if messageDict and 'data' in messageDict and messageDict['data']:
			pass
			# Aggiorno le statistiche

	except Exception as ex:
		# In caso di eccezioni printo e loggo tutti i dati disponibili
		getErrorInfo(ex)


def onWSOBClose():
	global ws_ob
	AutoReconnect(ws_ob)


ws_ob = MyWebSocket(
	run=False,
	WS_URL=BITSTAMP_WEBSOCKET_URL,
	WS_EVENT=BITSTAMP_WEBSOCKET_EVENT,
	WS_CHANNEL=BITSTAMP_WEBSOCKET_CHANNEL_ORDERBOOK,
	callbackOnMessage=onWSOBMessage,
	callbackOnClose=onWSOBClose
)


def passa_output_al_log_file():
	logging.basicConfig(
		level=logging.INFO,
		filename=f"programmi/copia-carbone-orderbook/copia_da_bitstamp-orderbook-{coppia}.csv",
		filemode="a",
		format="%(asctime)s,%(message)s",
		datefmt=FORMATO_DATA_ORA
	)


def avvio(argv):
	passa_output_al_log_file()
	#dati_da_Bitstamp_websocket()
	ws_ob.run_forever()


def AutoReconnect(ws, resetCounter=False):
	global _counterAutoReconnect

	if resetCounter:
		_counterAutoReconnect = 0
	if WEBSOCKET_AUTORECONNECT and ws:
		_counterAutoReconnect += 1
		time.sleep(1)
		if _counterAutoReconnect <= WEBSOCKET_AUTORECONNECT_RETRIES and not ws.isOpen:
			print("riconnetto", _counterAutoReconnect)
			try:
				ws.close()
				ws.run_forever()
			except websocket._exceptions.WebSocketException:
				pass


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

				timestamp = str(messageDict['data']['timestamp'])
				data = str(messageDict['data'])
				logging.info(f'{timestamp},{data}')
	except Exception as e:
		print(f'Exception:{e}')
		sys.stdout.flush()


def on_error(ws, error: str):
	print('Error:' + error)
	sys.stdout.flush()


def on_close(ws):
	print("### WebSocketclosed  ###")


avvio(sys.argv[1:])
