# LIMIT ORDER, no flag

# comprando ad un evento
# precalcola:  delta minimo di guadagno + fee = prezzo ottimale di vendita
# ogni 10sec deve valutare SE ce ne sarebbe uno migliore ,

from costanti.costanti_unico import *
from piattaforme.bitstamp.websocketOrderbook import startWebSocketOrderBook
from utilita.calcoli import depthChartAnalyzer, ilPrezzoGiusto

# FEE
#DELTA = 0  # %


def rivalutaPrezzi(orderbook: dict):

	good_price_bid, good_price_ask = ilPrezzoGiusto(orderbook['bids'], orderbook['asks'])
	return [ good_price_bid, good_price_ask ]

	#todo- on buy-order done,
	# take buy_price, amount and pass to calcoloPrezziByDelta()


if __name__ == "__main__":
	startWebSocketOrderBook(rivalutaPrezzi)
