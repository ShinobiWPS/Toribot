import hashlib
import importlib
import json
import logging
import sys
import threading
import time
from pathlib import Path

import websocket
from costanti.api import API_TOKEN_HASH, TELEGRAM_ID
from costanti.costanti_unico import (
	BITSTAMP_WEBSOCKET_CHANNEL_ORDERBOOK, BITSTAMP_WEBSOCKET_CHANNEL_TRADE,
	BITSTAMP_WEBSOCKET_EVENT, BITSTAMP_WEBSOCKET_URL, LOG_CARTELLA_PERCORSO, LUNGHEZZA_MEMORIA,
	MEMORIA_ORDERBOOK_PERCORSO, MEMORIA_ORDERBOOK_SIMPLIFIED_PERCORSO, NUMERO_ORDINI_ORDERBOOK,
	TRADING_REPORT_FILENAME, VALUTA_CRIPTO, VALUTA_SOLDI, WEBSOCKET_AUTORECONNECT,
	WEBSOCKET_AUTORECONNECT_RETRIES
)
from flask import Flask, request
from flask_cors import CORS
#from piattaforme.bitstamp import bitstampRequests as bitstamp
from pyti import relative_strength_index
from utilita import apriFile as managerJson
from utilita import fileManager
from utilita import gestoreRapporti as report
from utilita import log
from utilita.infoAboutError import getErrorInfo
from utilita.MyWebSocket import MyWebSocket
from utilita.operazioni import dt_string
from utilita.Statistics import Statistics
from utilita.telegramBot import TelegramBot

# Inizializzo API
app = Flask(__name__)
CORS(app)

# Inizializzo i log
log.inizializza_log()

# Importo libreria in base all'argomento passato
strategiaSigla = 'BL'  #sys.argv[1]
path = f'strategie.{strategiaSigla}'
strategiaModulo = importlib.import_module(path)

MyStat = Statistics()
orderbook_history = None
simplified_orderbook_history = None
rsi = None
# ______________________________________ WEBSOCKET ______________________________________

# Ora nelle classi (MyWebSocket)

_counterAutoReconnect = 0
_counterUpdaterJson = 0


def onWSTradeClose():
	global ws_trade, tg_bot
	try:
		# Se il bot telegram è presente
		if tg_bot:
			# Invio un messaggio di avvertimento
			tg_bot.sendMessage(tg_bot.Admins_ID, "WebSocket Trade closed")
	except Exception:
		pass
	AutoReconnect(ws_trade)


def onWSTradeMessage(messageDict):
	global MyStat
	if _counterAutoReconnect:
		AutoReconnect(None, resetCounter=True)
	try:
		# Verifico che nel messaggio ricevuto ci siano i dati che mi aspetto
		if messageDict and 'data' in messageDict and messageDict['data']:

			# Aggiorno le statistiche
			MyStat.WST_update()
			pass
			# Invio i dati alla funzione che li gestirà (al momento non implementata)
			nuovoTrade(messageDict['data'])
	except Exception as ex:
		# In caso di eccezioni printo e loggo tutti i dati disponibili
		getErrorInfo(ex)


def onWSOBMessage(messageDict):
	global MyStat, tg_bot, orderbook_history, simplified_orderbook_history, _counterUpdaterJson, rsi
	if _counterAutoReconnect:
		AutoReconnect(None, resetCounter=True)
	try:
		# Verifico che nel messaggio ricevuto ci siano i dati che mi aspetto
		if messageDict and 'data' in messageDict and messageDict['data']:
			# Aggiorno le statistiche
			MyStat.strategy_cycle_duration_update(start=time.time())

			# if not orderbook_history:
			# 	simplified_orderbook_history = {
			# 		'asks': [],
			# 		'bids': []
			# 	}
			# 	# Recupero la lista degli ultimi valori
			# 	orderbook_history = fileManager.JsonReads(MEMORIA_ORDERBOOK_PERCORSO)
			# 	if orderbook_history:
			# 		for row in orderbook_history:
			# 			simplified_orderbook_history['asks'].append(row['asks'][0][0])
			# 			simplified_orderbook_history['bids'].append(row['bids'][0][0])
			# if not orderbook_history:
			# 	orderbook_history = []
			# 	simplified_orderbook_history = {
			# 		'asks': [],
			# 		'bids': []
			# 	}

			# Aggiorno le statistiche
			MyStat.WSOB_update()

			# Invio i dati alla funzione che li gestirà
			""" strategiaModulo.gestore(
				orderbook=messageDict['data'],
				orderbook_history=orderbook_history,
				simplified_orderbook_history=simplified_orderbook_history,
				MyStat=MyStat,
				tg_bot=tg_bot,
			) """

			# Se è una lista
			if isinstance(orderbook_history, list):
				# E se la lista è maggiore o uguale al numero di elementi che voglio
				if len(orderbook_history) >= LUNGHEZZA_MEMORIA:
					# Se c'è un solo elemento
					if len(orderbook_history) - LUNGHEZZA_MEMORIA == 0:
						# Cancello dalla lista
						orderbook_history.pop(0)
						simplified_orderbook_history['asks'].pop(0)
						simplified_orderbook_history['bids'].pop(0)
						# rsi['asks'].pop(0)
						# rsi['bids'].pop(0)
						# Cancello dal mio json
						# managerJson.gestoreValoriJson([ 'ultimo_valore', 0 ], '')
					else:
						# Partendo dall'inizio cancello gli elementi in più
						for _ in range(len(orderbook_history) - LUNGHEZZA_MEMORIA + 1):
							# Cancello dalla lista
							orderbook_history.pop(0)
							simplified_orderbook_history['asks'].pop(0)
							simplified_orderbook_history['bids'].pop(0)
							# rsi['asks'].pop(0)
							# rsi['bids'].pop(0)
							# Cancello dal mio json
							# managerJson.gestoreValoriJson([ 'ultimo_valore', 0 ], '')
			# Se non è una lista qualcosa non va
			else:
				# Quindi la reinizializzo
				orderbook_history = []
				simplified_orderbook_history = {
					'asks': [],
					'bids': []
				}
				# rsi = {
				# 	'asks': [],
				# 	'bids': []
				# }

			# Clono l'orderbook per ridimensionarlo
			orderbook_resized = messageDict['data']
			# Estraggo solo il numero di asks desiderati
			orderbook_resized['asks'] = orderbook_resized['asks'][:NUMERO_ORDINI_ORDERBOOK]
			# Estraggo solo il numero di bids desiderati
			orderbook_resized['bids'] = orderbook_resized['bids'][:NUMERO_ORDINI_ORDERBOOK]

			# Addo il nuovo orderbook ridimensionato al mio json
			# managerJson.commercialista("ultimo_valore", orderbook_resized)

			simplified_orderbook_history['asks'].append(float(orderbook_resized['asks'][0][0]))
			simplified_orderbook_history['bids'].append(float(orderbook_resized['bids'][0][0]))

			# Addo il nuovo orderbook ridimensionato al mio history in ram
			orderbook_history.append(orderbook_resized)

			# rsi['asks'] = relative_strength_index.relative_strength_index(
			# 	simplified_orderbook_history['asks'], 14
			# )
			# rsi['bids'] = relative_strength_index.relative_strength_index(
			# 	simplified_orderbook_history['bids'], 14
			# )
			"""
			if _counterUpdaterJson > 5:
				_counterUpdaterJson = 0
				updateJson()
			else:
				_counterUpdaterJson += 1
			"""
			# Aggiorno le statistiche
			MyStat.strategy_cycle_duration_update(end=time.time())
			pass

	except Exception as ex:
		# In caso di eccezioni printo e loggo tutti i dati disponibili
		getErrorInfo(ex)


def onWSOBClose():
	global ws_ob, tg_bot
	try:
		# Se il bot telegram è presente
		if tg_bot:
			# Invio un messaggio di avvertimento
			tg_bot.sendMessage(tg_bot.Admins_ID, "WebSocket OrderBook closed")
	except Exception:
		pass
	AutoReconnect(ws_ob)


def AutoReconnect(ws, resetCounter=False):
	global _counterAutoReconnect, tg_bot

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
			try:
				# Se il bot telegram è presente
				if tg_bot:
					# Invio un messaggio di avvertimento
					tg_bot.sendMessage(tg_bot.Admins_ID, "Restarting WebSocket")
			except Exception:
				pass


# Inizializzo variabili per il funzionamento dello script
ws_trade = None
ws_ob = None
mybot = None
tg_bot = None

# Inizializzo i websocket
ws_trade = MyWebSocket(
	run=False,
	WS_URL=BITSTAMP_WEBSOCKET_URL,
	WS_EVENT=BITSTAMP_WEBSOCKET_EVENT,
	WS_CHANNEL=BITSTAMP_WEBSOCKET_CHANNEL_TRADE,
	callbackOnMessage=onWSTradeMessage,
	callbackOnClose=onWSTradeClose
)
ws_ob = MyWebSocket(
	run=False,
	WS_URL=BITSTAMP_WEBSOCKET_URL,
	WS_EVENT=BITSTAMP_WEBSOCKET_EVENT,
	WS_CHANNEL=BITSTAMP_WEBSOCKET_CHANNEL_ORDERBOOK,
	callbackOnMessage=onWSOBMessage,
	callbackOnClose=onWSOBClose
)


def updateJson():
	global MyStat, tg_bot, orderbook_history, simplified_orderbook_history, rsi
	MyStat.update_json()
	if orderbook_history:
		fileManager.JsonWrites(MEMORIA_ORDERBOOK_PERCORSO, 'w', orderbook_history)
	if simplified_orderbook_history:
		fileManager.JsonWrites(
			MEMORIA_ORDERBOOK_SIMPLIFIED_PERCORSO, 'w', simplified_orderbook_history
		)
	# if rsi:
	# 	fileManager.JsonWrites(MEMORIA_RSI_PERCORSO, 'w', rsi)
	threading.Timer(10.0, updateJson).start()


def avvio():
	global ws_trade, ws_ob, orderbook_history, simplified_orderbook_history, rsi
	try:
		# argv:  gli argomenti tranne il primo perche e' il nome del file
		# argv = sys.argv[1:]
		#todo- crea cartella log se non esiste

		# Creo tutte le cartelle necessarie
		Path(TRADING_REPORT_FILENAME).parent.mkdir(parents=True, exist_ok=True)
		# Scrivo sul report
		report.FileAppend(
			TRADING_REPORT_FILENAME,
			dt_string() + " " + ('*' * 5) + "STARTED" + ('*' * 5) + "\n"
		)
		logging.info(dt_string() + " " + ('*' * 5) + "STARTED" + ('*' * 5) + "")

		# Chiedo alla piattaforma il bilancio
		balance = json.loads(bitstamp.getBalance())
		# Scrivo la risposta del bilancio su file json per Debug
		report.JsonWrites(LOG_CARTELLA_PERCORSO + "/sync_balance.json", "w+", balance)
		# Estraggo dalla risposta il valore dei soldi
		soldi_balance = float(
			balance[f"{VALUTA_SOLDI}_balance"]
		) if f"{VALUTA_SOLDI}_balance" in balance else None
		# Aggiorno il valore dei soldi sul mio json
		unused_cripto, soldi = managerJson.portafoglio("soldi", soldi_balance)

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

		if not orderbook_history:
			simplified_orderbook_history = {
				'asks': [],
				'bids': []
			}
			# rsi = {
			# 	'asks': [],
			# 	'bids': []
			# }

			# Recupero la lista degli ultimi valori
			orderbook_history = fileManager.JsonReads(MEMORIA_ORDERBOOK_PERCORSO)
			if orderbook_history:
				for row in orderbook_history:
					simplified_orderbook_history['asks'].append(float(row['asks'][0][0]))
					simplified_orderbook_history['bids'].append(float(row['bids'][0][0]))

					# if len(simplified_orderbook_history['asks']) >= 14:
					# 	rsi['asks'] = relative_strength_index.relative_strength_index(
					# 		simplified_orderbook_history['asks'], 14
					# 	)

					# if len(simplified_orderbook_history['bids']) >= 14:
					# 	rsi['bids'] = relative_strength_index.relative_strength_index(
					# 		simplified_orderbook_history['bids'], 14
					# 	)

		if not orderbook_history:
			orderbook_history = []
			simplified_orderbook_history = {
				'asks': [],
				'bids': []
			}
			# rsi = {
			# 	'asks': [],
			# 	'bids': []
			# }

		# Forzo il print a console
		sys.stdout.flush()

		# jsonUpdater = threading.Thread(target=updateJson, daemon=True)
		# jsonUpdater.start()
		threading.Timer(1.0, updateJson).start()

		# Starto il websocket dell'orderbook
		ws_ob.run_forever()
		# ws_th = threading.Thread(target=ws_ob.run_forever, daemon=True)
		# ws_th.start()

	except Exception as ex:
		# In caso di eccezioni printo e loggo tutti i dati disponibili
		getErrorInfo(ex)

	finally:
		# Comunque sia andata
		# Forzo il print a console
		sys.stdout.flush()


def nuovoTrade(valore):
	# Funzione non implementata
	# Prevista per la verifica dell'esecuzione degli ordini senza l'uso di checkOrder
	pass


# ______________________________________ API ______________________________________


# hashing
def encrypt_string(hash_string):
	# Calcolo l'HASH256 della stringa passata come argomento (hash_string)
	sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
	# Ritorno la stringa convertita in HASH256
	return sha_signature


# resetto cycle max on stats
@app.route('/reset_max', methods=['GET'])
def reset_max():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		MyStat.strategy['WST']["duration"]["max"] = None
		MyStat.strategy['WSOB']["duration"]["max"] = None
		MyStat.strategy["cycle"]["duration"]["max"] = None
		MyStat.strategy["trade"]["duration"]["max"] = None
		MyStat.strategy["buy"]["duration"]["max"] = None
		MyStat.strategy["sell"]["duration"]["max"] = None
		MyStat.strategy["spread"]["max"] = None
		# Ritorno una stringa e un codice stato
		return 'Resetted', 200
	# Ritorno 404
	return '', 404


# aggiorno json
@app.route('/update_json', methods=['GET'])
def update_json():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		updateJson()
		# Ritorno una stringa e un codice stato
		return 'Updated', 200
	# Ritorno 404
	return '', 404


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
		ultimo_valore = fileManager.JsonReads(MEMORIA_ORDERBOOK_PERCORSO)
		# Ritorno l'ultimo valore
		return str(ultimo_valore[-1]['bids'][0]), 200
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

		# Leggo dal mio json il valore di soldi e cripto
		unused_cripto, soldi = managerJson.portafoglio()
		# Scrivo sul report
		report.FileAppend(TRADING_REPORT_FILENAME, dt_string() + " Sincronizzo bilancio")
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
			ultimo_valore = fileManager.JsonReads(MEMORIA_ORDERBOOK_PERCORSO)
			orders = managerJson.getOrders()
			# Estraggo l'ultimo ultimo valore
			ultimo_valore = ultimo_valore[-1]
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
						fileManager.JsonWrites(MEMORIA_ORDERBOOK_PERCORSO, 'w', [orderbook])
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
					fileManager.JsonWrites(MEMORIA_ORDERBOOK_PERCORSO, 'w', [orderbook])
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
			return str(soldi) + " " + VALUTA_SOLDI.upper(), 200
		# Se è presente come argomento GET
		if 'cripto' in request.args:
			# Ritorno il valore delle cripto
			return str(cripto) + " " + VALUTA_CRIPTO.upper(), 200
		# Ritorno il valore di soldi e cripto
		return str(
			str(soldi) + " " + VALUTA_SOLDI.upper() if soldi else str(cripto) + " " +
			VALUTA_CRIPTO.upper()
		), 200
	# Ritorno 404
	return '', 404


@app.route('/bilancio_stimato', methods=['GET'])
def bilancio_stimato():
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Ottengo gli ordini dal mio json
		unused_cripto, soldi = managerJson.portafoglio()
		ultimo_valore = fileManager.JsonReads(MEMORIA_ORDERBOOK_PERCORSO)
		orders = managerJson.getOrders()
		# Inizializzo la variabile per la stima
		soldi_stimati = 0
		# Per tutti gli ordini
		for order in orders:
			# Sommo il valore attuale delle cripto in soldi
			soldi_stimati += order['amount'] * float(ultimo_valore[-1]['bids'][0][0])
		# Sommo i soldi stimati con i soldi rimasti inutilizzati
		soldi_stimati += soldi
		# Ritorno il valore dei soldi stimati
		return str(soldi_stimati) + " " + VALUTA_SOLDI.upper(), 200

	# Ritorno 404
	return '', 404


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
	global ws_trade, ws_ob
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Creo l'oggetto con cui rispondere con i valori degli stati
		unused_res = {
			'ws_trade': ws_trade.trace,
			'ws_ob': ws_ob.isOpen,
			'tg_bot': (True if tg_bot else False)
		}
		# Ritorno in formato json l'oggetto con gli stati
		# return str(json.dumps(res)), 200
		# Temporaneamente invio solo lo stato del websocket dell' orderbook
		return str(ws_ob.isOpen), 200
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
	global tg_bot
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Se il bot telegram è presente
		if tg_bot:
			# Invio un messaggio di avvertimento
			tg_bot.sendMessage(TELEGRAM_ID, "Forcing buy")
		# Comunica alla strategie di comprare il prima possibile
		strategiaModulo.force_buy = True
		# Ritorna una stringa di conferma
		return 'Buying', 200
	# Ritorno 404
	return '', 404


@app.route('/ask_sell', methods=['GET'])
def send_sell():
	global tg_bot
	# Verifico che il token passato via GET sia corretto
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# Se il bot telegram è presente
		if tg_bot:
			# Invio un messaggio di avvertimento
			tg_bot.sendMessage(TELEGRAM_ID, "Forcing sell")
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
# 		strategiaModulo.vendi(cripto, ultimo_valore[-1])
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


print(__name__)

if __name__ == "__main__":
	try:
		# Inizializzo il thread per la funzione avvio()
		mybot = threading.Thread(target=avvio, daemon=True)

		if True:
			# Avvio come thread la funzione avvio()
			mybot.start()

		# Avvia il il bot di telegram
		tg_bot = TelegramBot(True)

		# Avvia le API
		app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)

	except Exception as ex:
		# In caso di eccezioni printo e loggo tutti i dati disponibili
		logging.error(ex)
		print(ex)
		try:
			# Se il bot telegram è presente
			if tg_bot:
				# Invio un messaggio di avvertimento
				tg_bot.sendMessage(TELEGRAM_ID, "Error, closing")
		except Exception:
			pass
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

		# Leggo dal mio json il valore di soldi e cripto
		cripto, soldi = managerJson.portafoglio()
		# Se ho soldi
		if soldi:
			# Scrivo sul report il valore dei soldi
			report.FileAppend(
				TRADING_REPORT_FILENAME,
				dt_string() + " Finisco con " + str(round(soldi, 2)) + " " +
				str(VALUTA_SOLDI.upper())
			)
			# Scrivo sulla console il valore dei soldi
			print("Finisco con " + str(round(soldi, 2)) + " " + VALUTA_SOLDI.upper())
			# Loggo come info la chiusura
			logging.info(dt_string() + " closing")
