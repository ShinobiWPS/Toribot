# LIMIT ORDER, no flag

# comprando ad un evento
# precalcola:  delta minimo di guadagno + fee = prezzo ottimale di vendita
# ogni 10sec deve valutare SE ce ne sarebbe uno migliore ,

import sched
import time

from costanti.costanti_unico import *
from piattaforme.bitstamp.websocketOrderbook import startWebSocketOrderBook
from utilita import apriFile as managerJson
from utilita.calcoli import depthChartAnalyzer, prezzoInPrimaFila
from utilita.Statistics import Statistics
from utilita.telegramBot import TelegramBot

# FEE
# DELTA = 0  # %

TIMER, TIMER_DEFAULT = 4, 4  #secondi
CORE_IS_NOT_RUNNING = True

#todo- LOCALI
GOOD_PRICE_BID, GOOD_PRICE_ASK = 0, 0


def core(sc):
	global CORE_IS_NOT_RUNNING
	CORE_IS_NOT_RUNNING = False
	unused_cripto, soldi = managerJson.portafoglio()
	if soldi:
		pass

	print("Doing stuff...")
	s.enter(TIMER, 1, core, ( sc, ))


s = sched.scheduler(time.time, time.sleep)
s.enter(TIMER, 1, core, ( s, ))


def gestore(
	orderbook: dict,
	orderbook_history=managerJson.commercialista()[0],
	MyStat=Statistics(),
	tg_bot=TelegramBot(False)
):
	if CORE_IS_NOT_RUNNING:
		s.run()
	rivalutaPrezzi(orderbook)


def rivalutaPrezzi(
	orderbook: dict,
	#orderbook_history=managerJson.commercialista()[0],
	#MyStat=Statistics(),
	#tg_bot=TelegramBot(False)
):
	global GOOD_PRICE_ASK
	global GOOD_PRICE_BID

	GOOD_PRICE_BID, GOOD_PRICE_ASK = prezzoInPrimaFila(
		orderbook['bids'],
		orderbook['asks'],
	)

	#todo- place buy order open

	#todo- on buy-order done,
	# take buy_price, amount and pass to calcoloPrezziByDelta()


if __name__ == "__main__":
	startWebSocketOrderBook(gestore)
