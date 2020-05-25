import csv
import importlib
import json
import logging
import os
import sys
import time
from datetime import datetime

import websocket

import utilita.GestoreRapporti as GestoreRapporti
from _datetime import timedelta
from costanti.dataset import DATASET_CARTELLA_PERCORSO
from costanti.dataset_nome_da_usare import DATASET_NOME_DA_USARE
from costanti.log_cartella_percorso import TRADING_REPORT_FILENAME
from piattaforme.bitstamp.bitstampRequests import buy, getBalance, sell
from utilita.apriFile import commercialista, portafoglio, ultimo_id_ordine
from utilita.log import passa_output_al_log_file

CRIPTOVALUTA = "Ripple"
CRIPTOMONETA = "XRP"
VALUTA = "Euro"
MONETA = VALUTA[0:3] # diego pigro a scrivere Eur,tagliando la O

# ______________________________________roba che serve all'avvio____________________
strategiaSigla=sys.argv[1]
# no error handling on purpose,
# we want to crash the bot if a correct strategy name it's not provided
path=f'strategie.{strategiaSigla}'
strategiaModulo= importlib.import_module(path)

# argv:  gli argomenti tranne il primo perche e' il nome del file
def avvio(argv):
	if len(argv) > 0:
		if 'log' in argv:
			passa_output_al_log_file()

	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

	# pulisco il report prime di scriverci sopra
	GestoreRapporti.FileWrite(TRADING_REPORT_FILENAME,"")

	if "dev" in argv:
		cripto, soldi = portafoglio("cripto", 0)
		cripto, soldi = portafoglio("soldi", 100)
		ultimo_valore, valore_acquisto = commercialista("ultimo_valore", 0)
		ultimo_valore, valore_acquisto = commercialista("valore_acquisto", 0)
	cripto, soldi = portafoglio()
	if soldi:
		print("Inizio con " + str(round(soldi, 2)) + " " + str(MONETA))
		GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Inizio con " + str(round(soldi, 2)) + " " + str(MONETA))
	if cripto:
		GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,
		    dt_string+" Inizio con " + str(round(cripto, 3)) + " " + str(CRIPTOMONETA)
		)
		print("Inizio con " + str(round(cripto, 3)) + " " + str(CRIPTOMONETA))
	sys.stdout.flush()

	if "dev" in argv:
		dati_statici()
	else:
		dati_da_Bitstamp_websocket()

	cripto, soldi = portafoglio()
	if soldi:
		GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Finisco con " + str(round(soldi, 2)) + " " + str(MONETA))
		print("Finisco con " + str(round(soldi, 2)) + " " + str(MONETA))
	if cripto:
		ultimo_valore, valore_acquisto = commercialista()
		print(
		    "Finisco con " + str(round(cripto * ultimo_valore, 2)) + " " +
		    str(MONETA)
		)
		GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,
		    dt_string+" Finisco con " + str(round(cripto, 3)) + " " + str(CRIPTOMONETA)
		)
		#GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Finisco con " + str(round(cripto * (ultimo_valore if ultimo_valore > valore_acquisto else valore_acquisto), 2)) + " " + str(MONETA))
		GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,
		    dt_string+" Finisco con " + str(round(cripto * ultimo_valore, 2)) + " " +
		    str(MONETA)
		)
	sys.stdout.flush()


def processaNuovoPrezzo(attuale):
	# logging.info(attuale)
	strategiaModulo.gestore(attuale)


# _____________________________________elabora i dati inseriti da noi__________________-
def dati_statici():
	with open(f'{DATASET_CARTELLA_PERCORSO}/{DATASET_NOME_DA_USARE}.csv') as csvFile:
		datiStatici = csv.reader(csvFile)
		lastReferenceTime= False
		frequency=timedelta(minutes=120)
		for riga in datiStatici:
			if riga and riga[0]:
				tradeTime = datetime.strptime(riga[1], '%d-%m-%Y %H:%M:%S')
				if lastReferenceTime is False : #for first-run-only
					lastReferenceTime = tradeTime
					processaNuovoPrezzo(float(riga[0]))
				time_difference = tradeTime - lastReferenceTime
				pre_time_difference_in_minutes = time_difference / timedelta(minutes=1)
				time_difference_in_minutes = timedelta(minutes=pre_time_difference_in_minutes)
				if time_difference_in_minutes >= frequency:
					lastReferenceTime = datetime.strptime(riga[1], '%d-%m-%Y %H:%M:%S')
					# GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,"" + str(riga[1]) + " : " + str(riga[0]))
					processaNuovoPrezzo(float(riga[0]))


# ______________________________________parte con dati websocket______________________________________
def dati_da_Bitstamp_websocket():
	try:
		ultimo_id_ordine(0)

		# balance
		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
		cripto, soldi = portafoglio()
		GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Sincronizzo bilancio")
		balance = json.loads(getBalance())
		GestoreRapporti.JsonWrites("log/buy_balance.json","w+",balance)
		cripto_balance = float(balance["xrp_available"]) if "xrp_available" in balance else None
		soldi_balance = float(balance["eur_available"]) if "eur_available" in balance else None
		portafoglio("soldi", soldi_balance)
		if soldi_balance!=soldi:
			GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Rilevata discrepanza: "+str(round(soldi_balance-soldi,5))+" "+str(MONETA))
		portafoglio("cripto", cripto_balance)
		if cripto_balance!=cripto:
			GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Rilevata discrepanza: "+str(round(cripto_balance-cripto,8))+" "+str(CRIPTOMONETA))


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
	print('Luce verde')


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


def on_close(ws):
	print("### WebSocketclosed ###")


avvio(sys.argv[1:])
