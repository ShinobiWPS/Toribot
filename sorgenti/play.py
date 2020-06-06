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

log.inizializza_log()

strategiaSigla = sys.argv[1]
path = f'strategie.{strategiaSigla}'
strategiaModulo = importlib.import_module(path)

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

		now = datetime.now()
		dt_string = now.strftime(FORMATO_DATA_ORA)

		# pulisco il report prime di scriverci sopra
		Path(TRADING_REPORT_FILENAME).mkdir(parents=True, exist_ok=True)
		report.FileWrite(TRADING_REPORT_FILENAME, ('*' * 5) + "STARTED" + ('*' * 5) + "\n")

		balance = json.loads(bitstamp.getBalance())
		report.JsonWrites(LOG_CARTELLA_PERCORSO + "/sync_balance.json", "w+", balance)
		soldi_balance = float(
			balance[f"{VALUTA_SOLDI}_balance"]
		) if f"{VALUTA_SOLDI}_balance" in balance else None
		cripto, soldi = managerJson.portafoglio("soldi", soldi_balance)

		if soldi:
			logging.info(dt_string + " Starting")
			print("Inizio con " + str(round(soldi, 2)) + " " + str(VALUTA_SOLDI.upper()))
			report.FileAppend(
				TRADING_REPORT_FILENAME,
				dt_string + " Inizio con " + str(round(soldi, 2)) + " " + str(VALUTA_SOLDI.upper())
			)
		sys.stdout.flush()

		startWebSocketOrderBook()

	except Exception as ex:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(ex, exc_type, fname, exc_tb.tb_lineno)
		logging.error(ex)

	finally:
		sys.stdout.flush()


def nuovoTrade(valore):
	pass


# ______________________________________ WEBSOCKET ______________________________________


# ___________________ TRADE __________________________
def startWebSocketTrade():
	global ws_trade
	try:
		# questo mostra piu informazioni se True
		websocket.enableTrace(False)
		ws_trade = websocket.WebSocketApp(
			"wss://ws.bitstamp.net",
			on_message=WST_on_message,
			on_error=WST_on_error,
			on_close=WST_on_close
		)
		ws_trade.on_open = WST_on_open
		ws_trade.run_forever()
	except KeyboardInterrupt:
		ws_trade.close()
	except Exception as ex:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(ex, exc_type, fname, exc_tb.tb_lineno)
		logging.error(ex)


def WST_on_open(ws):
	"""Funzione all'aggancio del WebSocket"""
	global ws_trade_open
	ws_trade_open = True
	jsonString = json.dumps({
		"event": "bts:subscribe",
		"data": {
		"channel": f"live_trades_{COPPIA_DA_USARE_NOME}"
		}
	})
	# manda a bitstamp la richiesta di iscriversi al canale di eventi sopra citato
	ws.send(jsonString)


def WST_on_message(ws, message: str):
	# la stringa message ha la stesso formato di un json quindi possiamo passarlo come tale per ottenere il Dict
	messageDict = json.loads(message)
	# PARE che appena si aggancia il socket manda un messaggio vuoto che fa crashare il bot
	if 'data' in messageDict and messageDict['data']:
		nuovoTrade(messageDict['data'])


def WST_on_error(ws, error: str):
	global ws_trade_open
	ws_trade_open = False
	print(error)
	logging.error(error)


def WST_on_close(ws):
	global ws_trade_open
	ws_trade_open = False
	if tg_bot:
		tg_bot.sendMessage(TELEGRAM_ID, "WebSocket Trade closed")
	print("### WebSocket Trade closed ###")


# ___________________ ORDERBOOK __________________________
def startWebSocketOrderBook():
	global ws_ob
	try:
		# questo mostra piu informazioni se True
		websocket.enableTrace(False)
		ws_ob = websocket.WebSocketApp(
			"wss://ws.bitstamp.net",
			on_message=WSOB_on_message,
			on_error=WSOB_on_error,
			on_close=WSOB_on_close
		)
		ws_ob.on_open = WSOB_on_open
		ws_ob.run_forever()
	except KeyboardInterrupt:
		ws_ob.close()
	except Exception as ex:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(ex, exc_type, fname, exc_tb.tb_lineno)
		logging.error(ex)


def WSOB_on_open(ws):
	"""Funzione all'aggancio del WebSocket"""
	global ws_ob_open
	ws_ob_open = True
	jsonString = json.dumps({
		"event": "bts:subscribe",
		"data": {
		"channel": f"order_book_{COPPIA_DA_USARE_NOME}"
		}
	})
	# manda a bitstamp la richiesta di iscriversi al canale di eventi sopra citato
	ws.send(jsonString)


def WSOB_on_message(ws, message: str):
	# la stringa message ha la stesso formato di un json quindi possiamo passarlo come tale per ottenere il Dict
	messageDict = json.loads(message)
	# PARE che appena si aggancia il socket manda un messaggio vuoto che fa crashare il bot
	if 'data' in messageDict and messageDict['data']:
		nuovoTrade(messageDict['data'])


def WSOB_on_error(ws, error: str):
	global ws_ob_open
	ws_ob_open = False
	print(error)
	logging.error(error)


def WSOB_on_close(ws):
	global ws_ob_open
	ws_ob_open = False
	if tg_bot:
		tg_bot.sendMessage(TELEGRAM_ID, "WebSocket Orderbook closed")
	print("### WebSocket Orderbook closed ###")


# ______________________________________ API ______________________________________


# hashing
def encrypt_string(hash_string):
	sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
	return sha_signature


@app.route('/ping', methods=['GET'])
def ping():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		return 'online', 200
	return '', 404


@app.route('/ultimo_valore', methods=['GET'])
def ultimo_valore():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		ultimo_valore = managerJson.commercialista()[0]
		return str(ultimo_valore), 200
	return '', 404


@app.route('/imposta_ultimo_valore', methods=['GET'])
def imposta_ultimo_valore():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		if 'valore' in request.args:
			ultimo_valore = managerJson.commercialista(
				"ultimo_valore", float(request.args['valore'])
			)[0]
			return str(ultimo_valore), 200
	return '', 404


# @app.route('/valore_acquisto', methods=['GET'])
# def valore_acquisto():
# 	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
# 		valore_acquisto = commercialista()[1]
# 		return str(valore_acquisto), 200
# 	return '', 404

# @app.route('/imposta_valore_acquisto', methods=['GET'])
# def imposta_valore_acquisto():
# 	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
# 		if 'valore' in request.args:
# 			valore_acquisto = commercialista("valore_acquisto", float(request.args['valore']))[1]
# 			return str(valore_acquisto), 200
# 	return '', 404


@app.route('/forza_bilancio', methods=['GET'])
def forza_bilancio():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# balance
		now = datetime.now()
		dt_string = now.strftime(FORMATO_DATA_ORA)
		cripto, soldi = managerJson.portafoglio()
		report.FileAppend(TRADING_REPORT_FILENAME, dt_string + " Sincronizzo bilancio")
		balance = json.loads(bitstamp.getBalance())
		report.JsonWrites(LOG_CARTELLA_PERCORSO + "/sync_balance.json", "w+", balance)
		soldi_balance = float(
			balance[f"{VALUTA_SOLDI}_balance"]
		) if f"{VALUTA_SOLDI}_balance" in balance else None
		managerJson.portafoglio("soldi", soldi_balance)
		if soldi_balance != soldi:
			report.FileAppend(
				TRADING_REPORT_FILENAME, dt_string + " Sync balance: " +
				str(round(soldi_balance - soldi, 5)) + " " + str(VALUTA_SOLDI.upper())
			)
			print(
				dt_string + " Sync balance: " + str(round(soldi_balance - soldi, 5)) + " " +
				str(VALUTA_SOLDI.upper())
			)

		return str(soldi), 200

	return '', 404


@app.route('/bilancio', methods=['GET'])
def bilancio():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		cripto, soldi = managerJson.portafoglio()
		if 'soldi' in request.args:
			return str(soldi) + " " + VALUTA_SOLDI, 200
		if 'cripto' in request.args:
			return str(cripto) + " " + VALUTA_CRIPTO, 200
		return str(
			str(soldi) + " " + VALUTA_SOLDI if soldi else str(cripto) + " " + VALUTA_CRIPTO
		), 200
	return '', 404


# @app.route('/bilancio_stimato', methods=['GET'])
# def bilancio_stimato():
# 	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
# 		cripto, soldi = portafoglio()
# 		ultimo_valore = commercialista()[0]
# 		return str(
# 			str(soldi) + " " + VALUTA_SOLDI if soldi else str(cripto * ultimo_valore) + " " + VALUTA_CRIPTO
# 		), 200
# 	return '', 404

# @app.route('/imposta_bilancio', methods=['GET'])
# def imposta_bilancio():
# 	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
# 		if 'soldi' in request.args:
# 			cripto, soldi = portafoglio("soldi", float(request.args['soldi']))
# 			return str(soldi) + VALUTA_SOLDI, 200
# 		if 'cripto' in request.args:
# 			cripto, soldi = portafoglio("cripto", float(request.args['cripto']))
# 			return str(cripto) + VALUTA_CRIPTO, 200
# 	return '', 404


@app.route('/status', methods=['GET'])
def status():
	global ws_trade_open, ws_ob_open
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		res = {
			'ws_trade': ws_trade_open,
			'ws_ob': ws_ob_open,
			'tg_bot': tg_bot
		}
		return str(json.dumps(res)), 200
	return '', 404


@app.route('/stop', methods=['GET'])
def send_stop():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# comunica alla strategie di tirare i remi in barca
		strategiaModulo.closing = True
		return 'Stopping', 200
	return '', 404


@app.route('/ask_buy', methods=['GET'])
def send_buy():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# comunica alla strategie di comprare
		strategiaModulo.force_buy = True
		return 'Buying', 200
	return '', 404


@app.route('/ask_sell', methods=['GET'])
def send_sell():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# comunica alla strategie di comprare
		strategiaModulo.force_sell = True
		return 'Selling', 200
	return '', 404


# @app.route('/force_buy', methods=['GET'])
# def force_buy():
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
# 	return '', 404
#
#
# @app.route('/force_sell', methods=['GET'])
# def force_sell():
# 	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
# 		cripto, soldi = portafoglio()
# 		ultimo_valore = commercialista()[0]
# 		strategiaModulo.vendi(cripto, ultimo_valore)
# 		return 'Selling', 200
# 	return '', 404


@app.route('/start', methods=['GET'])
def start_as_daemon():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		global mybot

		strategiaModulo.closing = False
		mybot = threading.Thread(target=avvio, daemon=True)
		mybot.start()
		return 'Started', 200
	return '', 404


@app.route('/shutdown', methods=['GET'])
def shutdown():
	if 'token' in request.args and encrypt_string(request.args['token']) == API_TOKEN_HASH:
		# stop running process
		send_stop()
		# close api app
		func = request.environ.get('werkzeug.server.shutdown')
		func()
		return 'API Server going down', 200
	return '', 404


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
			tg_bot.sendMessage(TELEGRAM_ID, "Error, closing")
	finally:
		STOP = True
		strategiaModulo.closing = True

		if ws_trade:
			ws_trade.close()
		if ws_ob:
			ws_ob.close()

		now = datetime.now()
		dt_string = now.strftime(FORMATO_DATA_ORA)
		cripto, soldi = managerJson.portafoglio()
		if soldi:
			report.FileAppend(
				TRADING_REPORT_FILENAME, dt_string + " Finisco con " + str(round(soldi, 2)) + " " +
				str(VALUTA_SOLDI.upper())
			)
			print("Finisco con " + str(round(soldi, 2)) + " " + VALUTA_SOLDI.upper())
			logging.info(dt_string + " closing")
