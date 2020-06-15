# LIMIT ORDER, no flag

# comprando ad un evento
# precalcola:  delta minimo di guadagno + fee = prezzo ottimale di vendita
# ogni 10sec deve valutare SE ce ne sarebbe uno migliore ,

import sched
import time

from costanti.costanti_unico import *
from piattaforme.bitstamp.websocketOrderbook import startWebSocketOrderBook
from utilita import apriFile as managerJson
from utilita.calcoli import depthChartAnalyzer, ilPrezzoGiusto
from utilita.Statistics import Statistics
from utilita.telegramBot import TelegramBot

# FEE
# DELTA = 0  # %

TIMER, TIMER_DEFAULT = 4, 4  #secondi
CORE_IS_NOT_RUNNING = True

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


def core(sc):
	global CORE_IS_NOT_RUNNING
	CORE_IS_NOT_RUNNING = False
	print("Doing stuff...")
	s.enter(TIMER, 1, core, ( sc, ))


def rivalutaPrezzi(
	orderbook: dict,
	#orderbook_history=managerJson.commercialista()[0],
	#MyStat=Statistics(),
	#tg_bot=TelegramBot(False)
):
	unused_cripto, soldi = managerJson.portafoglio()
	if soldi:

		good_price_bid, good_price_ask = ilPrezzoGiusto(orderbook['bids'], orderbook['asks'])

		#todo- place buy order open

		#todo- on buy-order done,
		# take buy_price, amount and pass to calcoloPrezziByDelta()


if __name__ == "__main__":
	startWebSocketOrderBook(rivalutaPrezzi)
