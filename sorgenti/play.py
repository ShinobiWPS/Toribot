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
from pathlib import Path

import websocket
from flask import Flask, request
from flask_cors import CORS

from costanti.api import API_TOKEN_HASH, TELEGRAM_ID
from costanti.costanti_unico import (
	COPPIA_DA_USARE_NOME, FORMATO_DATA_ORA, LOG_CARTELLA_PERCORSO, TRADING_REPORT_FILENAME,
	VALUTA_CRIPTO, VALUTA_SOLDI
)
from piattaforme.bitstamp import bitstampRequests as bitstamp
from utilita import apriFile as managerJson
from utilita import gestoreRapporti as report
from utilita import log
from utilita.telegramBot import TelegramBot

# Inizializzo API
app = Flask(__name__)
CORS(app)

# Inizializzo i log
log.inizializza_log()

# Importo libreria in base all'argomento passato
strategiaSigla = sys.argv[1]
path = f'strategie.{strategiaSigla}'
strategiaModulo = importlib.import_module(path)

# Inizializzo variabili per il funzionamento dello script
mybot = None
tg_bot = None
ws_trade = None
ws_ob = None
ws_trade_open = False
ws_ob_open = False


def avvio():
	try:
		# argv:  gli argomenti tranne il primo perche e' il nome del file
		# argv = sys.argv[1:]
		#todo- crea cartella log se non esiste

		# Ottengo il timestamp attuale
		now = datetime.now()
		# Converto il timestamp in un datetime in formato umano
		dt_string = now.strftime(FORMATO_DATA_ORA)

		# Creo tutte le cartelle necessarie
		Path(TRADING_REPORT_FILENAME).parent.mkdir(parents=True, exist_ok=True)
		# Scrivo sul report
		report.FileWrite(TRADING_REPORT_FILENAME, ('*' * 5) + "STARTED" + ('*' * 5) + "\n")
		logging.info(('*' * 5) + "STARTED" + ('*' * 5) + "\n")

		# Chiedo alla piattaforma il bilancio
		balance = json.loads(bitstamp.getBalance())
		# Scrivo la risposta del bilancio su file json per Debug
		report.JsonWrites(LOG_CARTELLA_PERCORSO + "/sync_balance.json", "w+", balance)
		# Estraggo dalla risposta il valore dei soldi
		soldi_balance = float(
			balance[f"{VALUTA_SOLDI}_balance"]
		) if f"{VALUTA_SOLDI}_balance" in balance else None
		# Aggiorno il valore dei soldi sul mio json
		cripto, soldi = managerJson.portafoglio("soldi", soldi_balance)

		# Se ci sono soldi
		if soldi:
			# Scrivo nel logging con livello "info"
			logging.info(dt_string + " Starting")
			# Printo su console il valore di soldi
			print("Inizio con " + str(round(soldi, 2)) + " " + str(VALUTA_SOLDI.upper()))
			# Scrivo sul report il valore dei soldi
			report.FileAppend(
				TRADING_REPORT_FILENAME,
				dt_string + " Inizio con " + str(round(soldi, 2)) + " " + str(VALUTA_SOLDI.upper())
			)
		# Forzo il print a console
		sys.stdout.flush()

		# Starto il websocket dell'orderbook
		startWebSocketOrderBook()

	except Exception as ex:
		# In caso di eccezioni printo e loggo tutti i dati disponibili
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(ex, exc_type, fname, exc_tb.tb_lineno)
		logging.error(ex)

	finally:
		# Comunque sia andata
		# Forzo il print a console
		sys.stdout.flush()


def nuovoTrade(valore):
	# Funzione non implementata
	# Prevista per la verifica dell'esecuzione degli ordini senza l'uso di checkOrder
	pass


# ______________________________________ WEBSOCKET ______________________________________


# ___________________ TRADE __________________________
# Funzione d'inizializzazione del websocket per i valori del trading
def startWebSocketTrade():
	global ws_trade
	try:
		# Debug: questo mostra piu informazioni se True
		websocket.enableTrace(False)
		# Inizializzo il websocket
		ws_trade = websocket.WebSocketApp(
			"wss://ws.bitstamp.net",
			on_message=WST_on_message,
			on_error=WST_on_error,
			on_close=WST_on_close
		)
		# Imposto la funzione on_open, eseguita all'aggancio del websocket
		ws_trade.on_open = WST_on_open
		# Eseguo il websocket come demone (~ in background)
		ws_trade.run_forever()
	except KeyboardInterrupt:
		# in caso di eccezioni chiudo il websocket
		ws_trade.close()
	except Exception as ex:
		# In caso di eccezioni printo e loggo tutti i dati disponibili
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(ex, exc_type, fname, exc_tb.tb_lineno)
		logging.error(ex)


# Funzione all'aggancio del WebSocket per i trade
def WST_on_open(ws):
	global ws_trade_open
	# Imposto la variabile per sapere che il websocket è aperto
	ws_trade_open = True
	# Imposto il json della richiesta d'iscrizione al canale di eventi
	jsonString = json.dumps({
		"event": "bts:subscribe",
		"data": {
		"channel": f"live_trades_{COPPIA_DA_USARE_NOME}"
		}
	})
	# Invio la richiesta d'iscrizione alla piattaforma
	ws.send(jsonString)


# Funzione alla ricezione di dati dal websocket per il trade
def WST_on_message(ws, message: str):
	# Decodifico i dati ricevuti come json, convertendoli in un oggetto
	messageDict = json.loads(message)
	# Verifico che nel messaggio ricevuto ci siano i dati che mi aspetto
	if 'data' in messageDict and messageDict['data']:
		# Invio i dati alla funzione che li gestirà (al momento non implementata)
		nuovoTrade(messageDict['data'])


# Funzione in caso di errori col websocket per il trade
def WST_on_error(ws, error: str):
	global ws_trade_open
	# Imposto la variabile per sapere che il websocket è chiuso
	ws_trade_open = False
	# Printo l'errore che ha chiuso il websocket
	print(error)
	# Loggo come errore l'errore che ha chiuso il websocket
	logging.error(error)


# Funzione alla chiusura del websocket per il trade
def WST_on_close(ws):
	global ws_trade_open
	# Imposto la variabile per sapere che il websocket è chiuso
	ws_trade_open = False
	# Se il bot telegram è presente
	if tg_bot:
		# Invio un messaggio di avvertimento
		tg_bot.sendMessage(TELEGRAM_ID, "WebSocket Trade closed")
	# Printo un messaggio per avvertire della chiusura del websocket per il trade
	print("### WebSocket Trade closed ###")


# ___________________ ORDERBOOK __________________________
# Funzione d'inizializzazione del websocket per i valori dell'orderbook
def startWebSocketOrderBook():
	global ws_ob
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
		exc_type, exc_obj, exc_tb = sys.exc_info()
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
		# Invio i dati alla funzione che li gestirà (al momento non implementata)
		strategiaModulo.gestore(messageDict['data'])


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
	# Imposto la variabile per sapere che il websocket è chiuso
	ws_ob_open = False
	# Se il bot telegram è presente
	if tg_bot:
		# Invio un messaggio di avvertimento
		tg_bot.sendMessage(TELEGRAM_ID, "WebSocket Orderbook closed")
	# Printo un messaggio per avvertire della chiusura del websocket per il orderbook
	print("### WebSocket Orderbook closed ###")


# ______________________________________ API ______________________________________


# hashing
def encrypt_string(hash_string):
	# Calcolo l'HASH256 della stringa passata come argomento (hash_string)
	sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
	# Ritorno la stringa convertita in HASH256
	return sha_signature


# Creo un api con endpoint /ping
@app.route('/ping', methods=['GET'])
def ping():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Ritorno una stringa e un codice stato
		return 'online', 200
	# Ritorno 404
	return '', 404


@app.route('/ultimo_valore', methods=['GET'])
def ultimo_valore():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Leggo dal mio json l'ultimo valore
		ultimo_valore = managerJson.commercialista()[0]
		# Ritorno l'ultimo valore
		return str(ultimo_valore), 200
	# Ritorno 404
	return '', 404


@app.route('/imposta_ultimo_valore', methods=['GET'])
def imposta_ultimo_valore():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Se presente l'argomento GET
		if 'valore' in request.args:
			# Imposto nel mio json l'ultimo valore
			ultimo_valore = managerJson.commercialista(
				"ultimo_valore", float(request.args['valore'])
			)[0]
			# Ritorno l'ultimo valore appena impostato
			return str(ultimo_valore), 200
	# Ritorno 404
	return '', 404


# @app.route('/valore_acquisto', methods=['GET'])
# def valore_acquisto():
# Verifico che il token passato via GET sia corretto
# 	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
# 		valore_acquisto = commercialista()[1]
# 		return str(valore_acquisto), 200
# Ritorno 404
# 	return '', 404

# @app.route('/imposta_valore_acquisto', methods=['GET'])
# def imposta_valore_acquisto():
# Verifico che il token passato via GET sia corretto
# 	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
# 		if 'valore' in request.args:
# 			valore_acquisto = commercialista("valore_acquisto", float(request.args['valore']))[1]
# 			return str(valore_acquisto), 200
# Ritorno 404
# 	return '', 404


@app.route('/forza_bilancio', methods=['GET'])
def forza_bilancio():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# balance
		# Ottengo il timestamp attuale
		now = datetime.now()
		# Converto il timestamp in un datetime in formato umano
		dt_string = now.strftime(FORMATO_DATA_ORA)
		# Leggo dal mio json il valore di soldi e cripto
		cripto, soldi = managerJson.portafoglio()
		# Scrivo sul report
		report.FileAppend(TRADING_REPORT_FILENAME, dt_string + " Sincronizzo bilancio")
		# Chiedo il bilancio alla piattaforma
		balance = json.loads(bitstamp.getBalance())
		# Scrivo su un json la risposta del bilancio per Debug
		report.JsonWrites(LOG_CARTELLA_PERCORSO + "/sync_balance.json", "w+", balance)
		# Estraggo il valore dei soldi dalla risposta del bilancio
		soldi_balance = float(
			balance[f"{VALUTA_SOLDI}_balance"]
		) if f"{VALUTA_SOLDI}_balance" in balance else None
		# Aggiorno il valore dei soldi nel mio json
		managerJson.portafoglio("soldi", soldi_balance)
		# Se il valore nel mio json e il valore ottenuto dalla piattaforma differiscono
		if soldi_balance != soldi:
			# Scrivo sul report l'aggiornamento del valore
			report.FileAppend(
				TRADING_REPORT_FILENAME, dt_string + " Sync balance: " +
				str(round(soldi_balance - soldi, 5)) + " " + str(VALUTA_SOLDI.upper())
			)
			# Scrivo sulla console l'aggiornamento del valore
			print(
				dt_string + " Sync balance: " + str(round(soldi_balance - soldi, 5)) + " " +
				str(VALUTA_SOLDI.upper())
			)
		# Estraggo il valore delle cripto dalla risposta del bilancio
		cripto_balance = float(
			balance[f"{VALUTA_CRIPTO}_balance"]
		) if f"{VALUTA_CRIPTO}_balance" in balance else None
		# Se ho delle cripto
		if cripto_balance:
			# Ottengo gli ordini dal mio json
			ultimo_valore, orders = managerJson.commercialista()
			# Inizializzo la variabile per la stima delle cripto
			cripto_stimated = 0
			# Per tutti gli ordini
			for order in orders:
				# Se è un ordine d'acquisto
				if order['bos'] == "buy":
					cripto_stimated += order['amount']
			# Se la cripto che ho stimato di avere in base agli ordini nel json
			# è maggiore delle cripto che ho sul conto vuol dire che degli ordini non sono stati esauditi
			if cripto_stimated > cripto_balance:
				# Riprovo quindi tenendo conto solo degli ordini certamente easuditi.
				# Riazzero la cripto stimate, per rifare il conteggio
				cripto_stimated = 0

				# Per tutti gli ordini
				for order in orders:
					# Se è un ordine di acquisto
					# ed è stato completato (perchè non ha id o ha stato == finished [come da documentazione della piattaforma])
					if order['bos'] == "buy" and (
						not order['order_id'] or order['order_status'] == "finished"
					):
						cripto_stimated += order['amount']

				# Se la cripto che ho stimato di avere in base agli ordini nel json
				# è ancora maggiore delle cripto che ho sul conto vuol dire che ci sono degli ordini falsati
				# non posso continuare perchè potrei cercare di vendere cripto che non ho
				if cripto_stimated > cripto_balance:
					# Loggo come errore la discrepanza tra ordini e cripto
					logging.error("Errore valori.json falsi ordini, riverificare manualmente")
					# Scrivo nel report l'errore della discrepanza tra ordini e cripto
					report.FileAppend(
						TRADING_REPORT_FILENAME,
						dt_string + " Errore valori.json falsi ordini, riverificare manualmente"
					)
					# Creo un ecezione per avvisare del problema ed impedire di fare cazzate con i soldi veri
					raise Exception(
						"Incoerenze non sistemabili automaticamente, provvedere manualmente prima di riavviare"
					)

				# Se la cripto che ho stimato di avere in base agli ordini nel json
				# è minore delle cripto che ho sul conto vuol dire che ho delle cripto non considerate nel json
				elif cripto_stimated < cripto_balance:
					# Genero quindi un ordine fittizio da aggiungere al mio json
					# in modo da colmare la lacuna

					# Se c'è un ultimo valore
					if 'asks' in ultimo_valore:
						# Recupero l'ultimo ASKS price
						my_price = ultimo_valore['asks'][0][0]
					# Se non c'è nessun ultimo valore
					else:
						# Chiedo alla piattaforma l'orderbook
						orderbook = json.loads(bitstamp.getOrderbook())
						# Ridimensiono l'orderbook
						orderbook['asks'] = [orderbook['asks'][0]]
						orderbook['bids'] = [orderbook['bids'][0]]
						# Aggiorno l'ultimo valore con il nuovo orderbook
						managerJson.commercialista("ultimo_valore", orderbook)
						# Recupero l'ultimo ASKS price
						my_price = float(orderbook['asks'][0][0])

					# Scrivo l'ordine fittizio sul mio json
					managerJson.addOrder(
						amount=cripto_balance - cripto_stimated,
						price=float(my_price),
						order_id=0,
						order_status="forced",
						bos="buy"
					)

			# Se la cripto che ho stimato di avere in base agli ordini nel json
			# è minore delle cripto che ho sul conto vuol dire che ho delle cripto non considerate nel json
			elif cripto_stimated < cripto_balance:
				# Genero quindi un ordine fittizio da aggiungere al mio json
				# in modo da colmare la lacuna

				# Se c'è un ultimo valore
				if 'asks' in ultimo_valore:
					# Recupero l'ultimo ASKS price
					my_price = ultimo_valore['asks'][0][0]
				# Se non c'è nessun ultimo valore
				else:
					# Chiedo alla piattaforma l'orderbook
					orderbook = json.loads(bitstamp.getOrderbook())
					# Ridimensiono l'orderbook
					orderbook['asks'] = [orderbook['asks'][0]]
					orderbook['bids'] = [orderbook['bids'][0]]
					# Aggiorno l'ultimo valore con il nuovo orderbook
					managerJson.commercialista("ultimo_valore", orderbook)
					# Recupero l'ultimo ASKS price
					my_price = float(orderbook['asks'][0][0])

				# Scrivo l'ordine fittizio sul mio json
				managerJson.addOrder(
					amount=cripto_balance - cripto_stimated,
					price=float(my_price),
					order_id=0,
					order_status="forced",
					bos="buy"
				)
		# Ritorno i soldi
		return str(soldi_balance), 200

	# Ritorno 404
	return '', 404


@app.route('/bilancio', methods=['GET'])
def bilancio():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Leggo dal mio json il valore di soldi e cripto
		cripto, soldi = managerJson.portafoglio()
		# Se è presente come argomento GET
		if 'soldi' in request.args:
			# Ritorno il valore dei soldi
			return str(soldi) + " " + VALUTA_SOLDI, 200
		# Se è presente come argomento GET
		if 'cripto' in request.args:
			# Ritorno il valore delle cripto
			return str(cripto) + " " + VALUTA_CRIPTO, 200
		# Ritorno il valore di soldi e cripto
		return str(
			str(soldi) + " " + VALUTA_SOLDI if soldi else str(cripto) + " " + VALUTA_CRIPTO
		), 200
	# Ritorno 404
	return '', 404


# @app.route('/bilancio_stimato', methods=['GET'])
# def bilancio_stimato():
# Verifico che il token passato via GET sia corretto
# 	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
# 		cripto, soldi = portafoglio()
# 		ultimo_valore = commercialista()[0]
# 		return str(
# 			str(soldi) + " " + VALUTA_SOLDI if soldi else str(cripto * ultimo_valore) + " " + VALUTA_CRIPTO
# 		), 200
# Ritorno 404
# 	return '', 404

# @app.route('/imposta_bilancio', methods=['GET'])
# def imposta_bilancio():
# Verifico che il token passato via GET sia corretto
# 	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
# 		if 'soldi' in request.args:
# 			cripto, soldi = portafoglio("soldi", float(request.args['soldi']))
# 			return str(soldi) + VALUTA_SOLDI, 200
# 		if 'cripto' in request.args:
# 			cripto, soldi = portafoglio("cripto", float(request.args['cripto']))
# 			return str(cripto) + VALUTA_CRIPTO, 200
# Ritorno 404
# 	return '', 404


@app.route('/status', methods=['GET'])
def status():
	global ws_trade_open, ws_ob_open
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Creo l'oggetto con cui rispondere con i valori degli stati
		res = {
			'ws_trade': ws_trade_open,
			'ws_ob': ws_ob_open,
			'tg_bot': tg_bot
		}
		# Ritorno in formato json l'oggetto con gli stati
		return str(json.dumps(res)), 200
	# Ritorno 404
	return '', 404


@app.route('/stop', methods=['GET'])
def send_stop():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Comunica alla strategie di tirare i remi in barca
		strategiaModulo.closing = True
		# Ritorna una stringa di conferma
		return 'Stopping', 200
	# Ritorno 404
	return '', 404


@app.route('/ask_buy', methods=['GET'])
def send_buy():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Comunica alla strategie di comprare il prima possibile
		strategiaModulo.force_buy = True
		# Ritorna una stringa di conferma
		return 'Buying', 200
	# Ritorno 404
	return '', 404


@app.route('/ask_sell', methods=['GET'])
def send_sell():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Comunica alla strategie di vendere il prima possibile
		strategiaModulo.force_sell = True
		# Ritorna una stringa di conferma
		return 'Selling', 200
	# Ritorno 404
	return '', 404


# @app.route('/force_buy', methods=['GET'])
# def force_buy():
# Verifico che il token passato via GET sia corretto
# 	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
#
# 		if 'amount' in request.args and 'price' in request.args:
# 			amount = request.args['amount']
# 			price = request.args['price']
# 		else:
# 			balance = json.loads(getBalance())
# 			soldi_balance = float(balance[f"{VALUTA_SOLDI}_balance"]) if f"{VALUTA_SOLDI}_balance" in balance else None
# 			soldi = soldi_balance
#
# 		order_result = bitstamp.buyLimit(my_amount, asks_price, fok=True)
# 		managerJson.addOrder(
# 			amount=order_result['amount'],
# 			price=order_result['price'],
# 			order_id=order_result['id'],
# 			bos="sell" if int(order_result['bos']) else "buy"
# 		)
# 		managerJson.portafoglio(
# 			"soldi", soldi - (order_result['amount'] * order_result['price'])
# 		)
# 		del order_result
#
# 		return 'Buying', 200
# Ritorno 404
# 	return '', 404
#
#
# @app.route('/force_sell', methods=['GET'])
# def force_sell():
# Verifico che il token passato via GET sia corretto
# 	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
# 		cripto, soldi = portafoglio()
# 		ultimo_valore = commercialista()[0]
# 		strategiaModulo.vendi(cripto, ultimo_valore)
# 		return 'Selling', 200
# Ritorno 404
# 	return '', 404


@app.route('/start', methods=['GET'])
def start_as_daemon():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		global mybot

		# Resetto la variabile della strategia
		strategiaModulo.closing = False
		# Inizializzo il thread per la funzione avvio()
		mybot = threading.Thread(target=avvio, daemon=True)
		# Avvio come thread la funzione avvio()
		mybot.start()
		# Ritorna una stringa di conferma
		return 'Started', 200
	# Ritorno 404
	return '', 404


@app.route('/shutdown', methods=['GET'])
def shutdown():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Esegue la funzione per comunicare alla strategia che si sta chiudendo
		send_stop()
		# Recupera la funzione per la chiusura delle API
		func = request.environ.get('werkzeug.server.shutdown')
		# Chiude le API
		func()
		# Ritorna una stringa di conferma
		return 'API Server going down', 200
	# Ritorno 404
	return '', 404


if __name__ == "__main__":
	try:
		# Inizializzo il thread per la funzione avvio()
		mybot = threading.Thread(target=avvio, daemon=True)

		if True:
			# Avvio come thread la funzione avvio()
			mybot.start()

		# Avvia il il bot di telegram
		tg_bot = TelegramBot(False)

		# Avvia le API
		app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)

	except Exception as ex:
		# In caso di eccezioni printo e loggo tutti i dati disponibili
		logging.error(ex)
		print(ex)
		# Se il bot telegram è presente
		if tg_bot:
			# Invio un messaggio di avvertimento
			tg_bot.sendMessage(TELEGRAM_ID, "Error, closing")
	finally:
		# Comunico alla strategia che si sta chiudendo
		strategiaModulo.closing = True

		# Se il websocket per il trade è aperto
		if ws_trade:
			# Chiudo il websocket per il trade
			ws_trade.close()
		# Se il websocket per l'orderbook
		if ws_ob:
			# Chiudo il websocket per l'orderbook
			ws_ob.close()

		# Ottengo il timestamp attuale
		now = datetime.now()
		# Converto il timestamp in un datetime in formato umano
		dt_string = now.strftime(FORMATO_DATA_ORA)
		# Leggo dal mio json il valore di soldi e cripto
		cripto, soldi = managerJson.portafoglio()
		# Se ho soldi
		if soldi:
			# Scrivo sul report il valore dei soldi
			report.FileAppend(
				TRADING_REPORT_FILENAME, dt_string + " Finisco con " + str(round(soldi, 2)) + " " +
				str(VALUTA_SOLDI.upper())
			)
			# Scrivo sulla console il valore dei soldi
			print("Finisco con " + str(round(soldi, 2)) + " " + VALUTA_SOLDI.upper())
			# Loggo come info la chiusura
			logging.info(dt_string + " closing")
