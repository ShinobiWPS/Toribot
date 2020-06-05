





import importlib
import sys
from datetime import datetime

import websocket

from costanti.costanti_unico import COPPIA_DA_USARE_NOME

strategiaSigla = sys.argv[1]
path = f'strategie.{strategiaSigla}'
strategiaModulo = importlib.import_module(path)
CANALE = 'order_book'

def startOrderbook(parameter_list):
	#todo- copia codice websocket gia in uso con canale diverso e message che passa orderbook al gestore di BL
	global ws
	try:
		ultimo_id_ordine(0)

		# balance
		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
		cripto, soldi = portafoglio()
		gestoreRapporti.FileAppend(
			TRADING_REPORT_FILENAME, dt_string+" Sincronizzo bilancio")
		balance = json.loads(getBalance())
		gestoreRapporti.JsonWrites("log/sync_balance.json", "w+", balance)
		cripto_balance = float(
			balance[f"{VALUTA_CRIPTO}_balance"]) if f"{VALUTA_CRIPTO}_balance" in balance else None
		soldi_balance = float(
			balance[f"{VALUTA_SOLDI}_balance"]) if f"{VALUTA_SOLDI}_balance" in balance else None
		portafoglio("soldi", soldi_balance)
		if soldi_balance != soldi:
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME, dt_string +
									   " Sync balance: "+str(round(soldi_balance-soldi, 5))+" "+str(MONETA))
		portafoglio("cripto", cripto_balance)
		if cripto_balance != cripto:
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME, dt_string+" Sync balance: "+str(
				round(cripto_balance-cripto, 8))+" "+str(CRIPTOMONETA))

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
	global CANALE
	"""Funzione all'aggancio del WebSocket

	Arguments:

		ws {tipo_boh} -- sono dei caratteri apparentemente inutili
																	"""
	jsonString = json.dumps({
		"event": "bts:subscribe",
		"data": {
			"channel": f"{CANALE}_{COPPIA_DA_USARE_NOME}"
		}
	})
	# manda a bitstamp la richiesta di iscriversi al canale di eventi sopra citato
	_ws.send(jsonString)
	isOpenWS = True
	print('Luce verde')


def on_message(_ws, message: str):
	global CANALE
	# la stringa message ha la stesso formato di un json quindi possiamo passarlo come tale per ottenere il Dict
	messageDict = json.loads(message)
	# PARE che appena si aggancia il socket manda un messaggio vuoto che fa crashare il bot
	if messageDict['data'] != {}:
		processaNuovoTrade(messageDict['data'])


def on_error(_ws, error: str):
	global isOpenWS
	isOpenWS = False
	print(error)


def on_close(_ws):
	global isOpenWS
	isOpenWS = False
	if tg_bot:
		tg_bot.sendMessage(TELEGRAM_ID, "WebSocket closed")
	print("### WebSocketclosed ###")
