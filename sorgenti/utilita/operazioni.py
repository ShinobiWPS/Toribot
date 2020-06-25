import math as m

from costanti.costanti_unico import MEMORIA_ORDERBOOK_PERCORSO, VALUTA_CRIPTO
from utilita import fileManager


def percentageOf(percent: float, whole: float):
	return (percent * whole) / 100.0


def calcolaSpread(primo_prezzo: float, secondo_prezzo: float):
	# do we need to round() ?
	return abs(primo_prezzo - secondo_prezzo)


def calcoloPrezziByDelta(buy_price, amount):
	buy_price = float(buy_price)
	amount = float(amount)

	#delta for profit
	delta = float(1.007)  #e' circa il 1.05% del buy_price
	# XRPdelta = float(0.00182)

	#buy/bid

	cost = buy_price * amount
	buy_fee = (cost / 100) * 0.5
	buy_expanse = cost + buy_fee

	#sell/ask
	sell_price = buy_price + delta
	income = sell_price * amount
	#sell_fee = (income / 100) * 0.5
	#sell_expanse = income - sell_fee
	#profit = round(sell_expanse - buy_expanse, 5)
	return sell_price


def depthChartAnalyzer(bids: list, asks: list):
	totalBidsSumCriptoAmount = sumOf_AmountOrValue(bids)
	totalAsksSumCriptoAmount = sumOf_AmountOrValue(asks)
	return [ totalBidsSumCriptoAmount, totalAsksSumCriptoAmount ]


def priceChange(prezzo_float: float, bid_or_ask: str):
	prezzo = str(prezzo_float)

	if bid_or_ask == 'bid':
		operator = '-'
		if VALUTA_CRIPTO == 'btc':
			num2 = '0.01'
		elif VALUTA_CRIPTO == 'xrp':
			num2 = '0.00001'
		else:
			raise Exception('Cripto not listed in priceChange() for MINUS operator')
	elif bid_or_ask == 'ask':
		operator = '+'
		if VALUTA_CRIPTO == 'btc':
			num2 = '0.01'
		elif VALUTA_CRIPTO == 'xrp':
			num2 = '0.00001'
		else:
			raise Exception('Cripto not listed in priceChange() for PLUS operator')
	else:
		raise Exception('wrong argument in priceChange()')

	return eval(prezzo + operator + num2)


def ilPrezzoGiusto(bids: list, asks: list):
	#todo- criterio che analizza tutti i prezzi della colonna attuale
	buyOrderPrice = firstOrderPrice(bids)
	good_price_bid = priceChange(buyOrderPrice, 'bid')

	sellOrderPrice = firstOrderPrice(asks)
	good_price_ask = priceChange(sellOrderPrice, 'ask')

	return [ good_price_bid, good_price_ask ]


def sumOf_AmountOrValue(arrayOfOrders: list, valueOrAmount: str = 'amount'):
	#orderbook['bids'][0][0]
	if valueOrAmount == 'amount':
		key = 1
		totalSum = 0
		for order in arrayOfOrders:
			totalSum += float(order[key])
		return totalSum
	else:
		raise Exception("per ora calcolo soltanto l'amount")


def getAsksMemory(orderbook_history=fileManager.JsonReads(MEMORIA_ORDERBOOK_PERCORSO)):
	all_asks = []
	if orderbook_history:
		for mem_row in orderbook_history:
			for asks in range(len(mem_row['asks'])):
				all_asks.append(mem_row['asks'][asks][0])
		return all_asks
	return None


def getBidsMemory(orderbook_history=fileManager.JsonReads(MEMORIA_ORDERBOOK_PERCORSO)):
	all_bids = []
	if orderbook_history:
		for mem_row in orderbook_history:
			for bids in range(len(mem_row['bids'])):
				all_bids.append(mem_row['bids'][bids][0])
		return all_bids
	return None


def getAsksPercentage(
	asks=getAsksMemory(fileManager.JsonReads(MEMORIA_ORDERBOOK_PERCORSO)),
	my_value=0,
):
	if asks:
		up_len = len([ v for v in asks if float(my_value) < float(v) ])
		dw_len = len([ v for v in asks if float(my_value) > float(v) ])
		return [up_len / len(asks) * 100, dw_len / len(asks) * 100]
	return None


def getBidsPercentage(
	bids=getBidsMemory(fileManager.JsonReads(MEMORIA_ORDERBOOK_PERCORSO)),
	my_value=0,
):
	if bids:
		up_len = len([ v for v in bids if float(my_value) < float(v) ])
		dw_len = len([ v for v in bids if float(my_value) > float(v) ])
		return [up_len / len(bids) * 100, dw_len / len(bids) * 100]
	return None


def firstOrderPrice(bids_or_asks: list):
	return float(bids_or_asks[0][0])


def firstOrderAmount(bids_or_asks: list):
	return float(bids_or_asks[0][1])


# def forOrderCheck(data):
# 	buy_order_id = data['buy_order_id']
# 	sell_order_id = data['sell_order_id']
# 	amount = data['amount']
#
# 	#todo- if ultimo_id_ordine() NOT presente entrambi gli ID,allora non e' stato completato
# 	#else:
# 	# aggiorna valori.json togliendo l ID
# 	# synca l amount per creare la frazione di order
# 	pass

#if tg_bot:
#todo- printa tutti i reason

#	tg_bot.sendMessage(TELEGRAM_ID, result['reason']['__all__'][0])


def truncate(number, digits) -> float:
	stepper = 10.0**digits
	return m.trunc(stepper * number) / stepper
