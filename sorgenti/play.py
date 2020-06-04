import csv
import hashlib
import importlib
import json
import logging
import os
import sys
import threading
import time
from datetime import datetime

import websocket
from flask import Flask, request
from flask_cors import CORS

import utilita.gestoreRapporti as gestoreRapporti
from _datetime import timedelta
from costanti.api import API_TOKEN_HASH, TELEGRAM_ID
from costanti.coppia_da_usare import (COPPIA_DA_USARE_NOME,
                                      VALUTA_DA_USARE_CRIPTO,
                                      VALUTA_DA_USARE_SOLDI)
from costanti.dataset import DATASET_CARTELLA_PERCORSO
from costanti.dataset_nome_da_usare import DATASET_NOME_DA_USARE
from costanti.formato_data_ora import FORMATO_DATA_ORA
from costanti.log_cartella_percorso import TRADING_REPORT_FILENAME
from piattaforme.bitstamp.bitstampRequests import getBalance
from utilita.apriFile import commercialista, portafoglio, ultimo_id_ordine
from utilita.log import passa_output_al_log_file
from utilita.telegramBot import TelegramBot

CRIPTOVALUTA = "Criptomoneta"
CRIPTOMONETA = VALUTA_DA_USARE_CRIPTO
VALUTA = "Soldi"
MONETA = VALUTA_DA_USARE_SOLDI


# Inizializzo API
app = Flask(__name__)
CORS(app)

# Inizializzo
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

# Variabile per fermare l'esecuzione
STOP = False


# ______________________________________roba che serve all'avvio____________________
ws = None
mybot = None
tg_bot = None
isOpenWS = False
strategiaSigla=sys.argv[1]
# no error handling on purpose,
# we want to crash the bot if a correct strategy name it's not provided
path=f'strategie.{strategiaSigla}'
strategiaModulo= importlib.import_module(path)

ULTIMI_VALORI = []
NUMERO_ULTIMI_VALORI = 5

def avvio():
	try:
		# argv:  gli argomenti tranne il primo perche e' il nome del file
		argv = sys.argv[1:]
		passa_output_al_log_file()

		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

		# pulisco il report prime di scriverci sopra
		gestoreRapporti.FileWrite(TRADING_REPORT_FILENAME,"")

		if "dev" in argv:
			portafoglio("cripto", 0)
			portafoglio("soldi", 100)
			commercialista("ultimo_valore", 0)
			commercialista("valore_acquisto", 0)
		cripto, soldi = portafoglio()
		if soldi:
			print("Inizio con " + str(round(soldi, 2)) + " " + str(MONETA))
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Inizio con " + str(round(soldi, 2)) + " " + str(MONETA))
		if cripto:
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,
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
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Finisco con " + str(round(soldi, 2)) + " " + str(MONETA))
			print("Finisco con " + str(round(soldi, 2)) + " " + str(MONETA))
		if cripto:
			ultimo_valore = commercialista()[0]
			print(
			    "Finisco con " + str(round(cripto * ultimo_valore, 2)) + " " +
			    str(MONETA)
			)
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,
			    dt_string+" Finisco con " + str(round(cripto, 3)) + " " + str(CRIPTOMONETA)
			)
			#gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Finisco con " + str(round(cripto * (ultimo_valore if ultimo_valore > valore_acquisto else valore_acquisto), 2)) + " " + str(MONETA))
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,
			    dt_string+" Finisco con " + str(round(cripto * ultimo_valore, 2)) + " " +
			    str(MONETA)
			)

	except Exception as ex:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(ex, exc_type, fname, exc_tb.tb_lineno)
		logging.error(ex)

	finally:
		if tg_bot and "dev" in argv:
			tg_bot.sendMessage(TELEGRAM_ID,"Ended")
		sys.stdout.flush()


def processaNuovoPrezzo(attuale):
	# logging.info(attuale)
	if not attuale in ULTIMI_VALORI:
		strategiaModulo.gestore(attuale)
		ULTIMI_VALORI.append(attuale)
		if len(ULTIMI_VALORI) > NUMERO_ULTIMI_VALORI:
			ULTIMI_VALORI.pop(0)


# _____________________________________elabora i dati inseriti da noi__________________-
def dati_statici():
	global STOP
	with open(f'{DATASET_CARTELLA_PERCORSO}/{DATASET_NOME_DA_USARE}.csv') as csvFile:
		datiStatici = csv.reader(csvFile)
		lastReferenceTime= False
		frequency=timedelta(minutes=0)
		for riga in datiStatici:
			# se hai ricevuto il comando di stoppare
			if STOP:
				# verifica di non avere cripto in saccocia prima di chiudere tutto
				cripto = portafoglio()[0]
				if not cripto:
					# esci dal for
					break
			if riga and riga[0]:
				tradeTime = datetime.strptime(riga[1], FORMATO_DATA_ORA)
				if lastReferenceTime is False : #for first-run-only
					lastReferenceTime = tradeTime
					processaNuovoPrezzo(float(riga[0]))
				time_difference = tradeTime - lastReferenceTime
				pre_time_difference_in_minutes = time_difference / timedelta(minutes=1)
				time_difference_in_minutes = timedelta(minutes=pre_time_difference_in_minutes)
				if time_difference_in_minutes >= frequency:
					lastReferenceTime = datetime.strptime(riga[1], FORMATO_DATA_ORA)
					# gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,"" + str(riga[1]) + " : " + str(riga[0]))
					processaNuovoPrezzo(float(riga[0]))


# ______________________________________parte con dati websocket______________________________________
def dati_da_Bitstamp_websocket():
	global ws
	try:
		ultimo_id_ordine(0)

		# balance
		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
		cripto, soldi = portafoglio()
		gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Sincronizzo bilancio")
		balance = json.loads(getBalance())
		gestoreRapporti.JsonWrites("log/sync_balance.json","w+",balance)
		cripto_balance = float(balance[f"{VALUTA_DA_USARE_CRIPTO}_balance"]) if f"{VALUTA_DA_USARE_CRIPTO}_balance" in balance else None
		soldi_balance = float(balance[f"{VALUTA_DA_USARE_SOLDI}_balance"]) if f"{VALUTA_DA_USARE_SOLDI}_balance" in balance else None
		portafoglio("soldi", soldi_balance)
		if soldi_balance!=soldi:
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Sync balance: "+str(round(soldi_balance-soldi,5))+" "+str(MONETA))
		portafoglio("cripto", cripto_balance)
		if cripto_balance!=cripto:
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Sync balance: "+str(round(cripto_balance-cripto,8))+" "+str(CRIPTOMONETA))


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
	except Exception as ex:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(ex, exc_type, fname, exc_tb.tb_lineno)
		logging.error(ex)


def on_open(_ws):
	global isOpenWS
	"""Funzione all'aggancio del WebSocket

	Arguments:

		ws {tipo_boh} -- sono dei caratteri apparentemente inutili
																	"""
	jsonString = json.dumps({
	    "event": "bts:subscribe",
	    "data": {
	        "channel": f"live_trades_{COPPIA_DA_USARE_NOME}"
	    }
	})
	# manda a bitstamp la richiesta di iscriversi al canale di eventi sopra citato
	_ws.send(jsonString)
	isOpenWS = True
	print('Luce verde')


def on_message(_ws, message: str):
	# la stringa message ha la stesso formato di un json quindi possiamo passarlo come tale per ottenere il Dict
	messageDict = json.loads(message)
	# PARE che appena si aggancia il socket manda un messaggio vuoto che fa crashare il bot
	if messageDict['data'] != {}:
		# questo print serve solo a noi per lavorare
		attuale = messageDict['data']['price']
		processaNuovoPrezzo(attuale)


def on_error(_ws, error: str):
	global isOpenWS
	isOpenWS = False
	print(error)


def on_close(_ws):
	global isOpenWS
	isOpenWS = False
	if tg_bot:
		tg_bot.sendMessage(TELEGRAM_ID,"WebSocket closed")
	print("### WebSocketclosed ###")



#______________________________________API______________________________________

# hashing
def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

@app.route('/ping', methods=['GET'])
def ping():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		return 'online', 200
	return '',404

@app.route('/ultimo_valore', methods=['GET'])
def ultimo_valore():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		ultimo_valore = commercialista()[0]
		return str(ultimo_valore), 200
	return '',404

@app.route('/imposta_ultimo_valore', methods=['GET'])
def imposta_ultimo_valore():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		if 'valore' in request.args:
			ultimo_valore = commercialista("ultimo_valore", float(request.args['valore']))[0]
			return str(ultimo_valore), 200
	return '',404

@app.route('/valore_acquisto', methods=['GET'])
def valore_acquisto():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		valore_acquisto = commercialista()[1]
		return str(valore_acquisto), 200
	return '',404

@app.route('/imposta_valore_acquisto', methods=['GET'])
def imposta_valore_acquisto():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		if 'valore' in request.args:
			valore_acquisto = commercialista("valore_acquisto", float(request.args['valore']))[1]
			return str(valore_acquisto), 200
	return '',404

@app.route('/forza_bilancio', methods=['GET'])
def forza_bilancio():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# balance
		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
		cripto, soldi = portafoglio()
		gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Sincronizzo bilancio")
		balance = json.loads(getBalance())
		gestoreRapporti.JsonWrites("log/sync_balance.json","w+",balance)
		cripto_balance = float(balance[f"{VALUTA_DA_USARE_CRIPTO}_balance"]) if f"{VALUTA_DA_USARE_CRIPTO}_balance" in balance else None
		soldi_balance = float(balance[f"{VALUTA_DA_USARE_SOLDI}_balance"]) if f"{VALUTA_DA_USARE_SOLDI}_balance" in balance else None
		portafoglio("soldi", soldi_balance)
		if soldi_balance!=soldi:
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Sync balance: "+str(round(soldi_balance-soldi,5))+" "+str(MONETA))
		portafoglio("cripto", cripto_balance)
		if cripto_balance!=cripto:
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Sync balance: "+str(round(cripto_balance-cripto,8))+" "+str(CRIPTOMONETA))
		return str(str(soldi_balance)+" "+MONETA if soldi_balance else str(cripto_balance)+" "+CRIPTOMONETA), 200
	return '',404

@app.route('/bilancio', methods=['GET'])
def bilancio():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		cripto, soldi = portafoglio()
		if 'soldi' in request.args:
			return str(soldi)+" "+MONETA, 200
		if 'cripto' in request.args:
			return str(cripto)+" "+CRIPTOMONETA, 200
		return str(str(soldi)+" "+MONETA if soldi else str(cripto)+" "+CRIPTOMONETA), 200
	return '',404

@app.route('/bilancio_stimato', methods=['GET'])
def bilancio_stimato():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		cripto, soldi = portafoglio()
		ultimo_valore = commercialista()[0]
		return str(str(soldi)+" "+MONETA if soldi else str(cripto*ultimo_valore)+" "+CRIPTOMONETA), 200
	return '',404

@app.route('/imposta_bilancio', methods=['GET'])
def imposta_bilancio():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		if 'soldi' in request.args:
			cripto, soldi = portafoglio("soldi", float(request.args['soldi']))
			return str(soldi)+MONETA, 200
		if 'cripto' in request.args:
			cripto, soldi = portafoglio("cripto", float(request.args['cripto']))
			return str(cripto)+CRIPTOMONETA, 200
	return '',404

@app.route('/status', methods=['GET'])
def status():
	global isOpenWS
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		global mybot
		if mybot:
			return str(mybot.is_alive() or isOpenWS), 200
		return None, 200
	return '',404

@app.route('/stop', methods=['GET'])
def send_stop():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		global STOP
		STOP = True
		# comunica alla strategie di tirare i remi in barca
		strategiaModulo.closing = True
		return 'Stopping', 200
	return '',404

@app.route('/ask_buy', methods=['GET'])
def send_buy():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# comunica alla strategie di comprare
		strategiaModulo.force_buy = True
		return 'Buying', 200
	return '',404

@app.route('/ask_sell', methods=['GET'])
def send_sell():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# comunica alla strategie di comprare
		strategiaModulo.force_sell = True
		return 'Selling', 200
	return '',404

@app.route('/force_buy', methods=['GET'])
def force_buy():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		cripto, soldi = portafoglio()
		ultimo_valore = commercialista()[0]
		strategiaModulo.compro(soldi, ultimo_valore)
		return 'Buying', 200
	return '',404

@app.route('/force_sell', methods=['GET'])
def force_sell():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		cripto, soldi = portafoglio()
		ultimo_valore = commercialista()[0]
		strategiaModulo.vendi(cripto, ultimo_valore)
		return 'Selling', 200
	return '',404

@app.route('/start', methods=['GET'])
def start_as_daemon():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		global STOP, mybot
		# resetta i vari stop
		STOP = False
		strategiaModulo.closing = False
		mybot = threading.Thread(target=avvio, daemon=True)
		mybot.start()
		return 'Started', 200
	return '',404

@app.route('/shutdown', methods=['GET'])
def shutdown():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# stop running process
		send_stop()
		# close api app
		func = request.environ.get('werkzeug.server.shutdown')
		func()
		return 'API Server going down', 200
	return '',404


if __name__ == "__main__":
	try:
		# avvio()
		mybot = threading.Thread(target=avvio, daemon=True)
		mybot.start()

		tg_bot = TelegramBot(False)

		app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)

	except Exception as ex:
		logging.error(ex)
		if tg_bot:
			tg_bot.sendMessage(TELEGRAM_ID,"Error, closing")
	finally:
		STOP = True
		strategiaModulo.closing = True

		if ws:
			ws.close()
