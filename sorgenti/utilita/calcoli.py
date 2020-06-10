from costanti.costanti_unico import *


def percentageOf(percent: float, whole: float):
	return (percent * whole) / 100.0


def calcolaSpread(primo_prezzo: float, secondo_prezzo: float):
	# do we need to round() ?
	return abs(primo_prezzo - secondo_prezzo)


def calcoloPrezziByDelta(buy_price, amount):
	buy_price = float(0.18065)
	amount = float(100.00000000)

	#delta for profit
	delta = float(0.00182)  #e' circa il 1.05% del buy_price
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


def firstOrderPrice(bids_or_asks: list):
	return float(bids_or_asks[0][0])


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
