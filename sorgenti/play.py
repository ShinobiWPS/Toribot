import os
import sys
import csv
import json
import logging
import websocket
from utilita.log import passa_output_al_log_file
from operazioni import Gestore_B as Gestore
from utilita.apriFile import Portafoglio, Commercialista
from costanti.dati_forgiati import DATI_FORGIATI_CARTELLA_PERCORSO

CRIPTOVALUTA = "Ripple"
CRIPTOMONETA = "XRP"
VALUTA = "Euro"
MONETA = "€"

# ______________________________________roba che serve all'avvio____________________


def avvio(argv):
	if len(argv) > 0:
		if 'log' in argv:
			passa_output_al_log_file()

	cripto, soldi = Portafoglio()
	if soldi:
		logging.info("Inizio con " + str(round(soldi, 2)) + " " + str(MONETA))
	if cripto:
		logging.info("Inizio con " + str(round(cripto, 3)) + " " +
		             str(CRIPTOMONETA))

	if os.environ.get('ISDEVELOPMENT') == 'true' or "statico" in argv:
		dati_statici()
	else:
		dati_da_Bitstamp_websocket()

	cripto, soldi = Portafoglio()
	if soldi:
		logging.info("Finisco con " + str(round(soldi, 2)) + " " + str(MONETA))
	if cripto:
		ultimo_valore, valore_acquisto = Commercialista()
		logging.info("Finisco con " + str(round(cripto, 3)) + " " +
		             str(CRIPTOMONETA))
		#logging.info("Finisco con " + str(round(cripto * (ultimo_valore if ultimo_valore > valore_acquisto else valore_acquisto), 2)) + " " + str(MONETA))
		logging.info("Finisco con " + str(round(cripto * ultimo_valore, 2)) +
		             " " + str(MONETA))


def processaNuovoPrezzo(attuale):
	# logging.info(attuale)
	Gestore(attuale)


# _____________________________________elabora i dati inseriti da noi__________________-
def dati_statici():
	with open(f'{DATI_FORGIATI_CARTELLA_PERCORSO}/da_bitstamp.csv') as csvFile:
		datiStatici = csv.reader(csvFile)
		for riga in datiStatici:
			if riga and riga[0]:
				processaNuovoPrezzo(float(riga[0]))


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
		processaNuovoPrezzo(attuale)
	"""
		esito = seComprareOVendere(datiDaMessage) -> {azione: compra, quantiXRP: 24} || {}
		if esito != {}
			compra(esito)
		"""


def on_error(ws, error: str):
	print(error)
	print('❌')


def on_close(ws):
	print("### WebSocketclosed 🔴🔴🔴 ###")


avvio(sys.argv[1:])
