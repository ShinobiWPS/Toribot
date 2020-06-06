import json
import logging
import os
import sys
from datetime import datetime

import utilita.gestoreRapporti as gestoreRapporti
from costanti.api import API_TOKEN_HASH, TELEGRAM_ID
from costanti.costanti_unico import (
	COPPIA_DA_USARE_NOME, FEE, TRADING_REPORT_FILENAME, VALUTA_CRIPTO
)
from piattaforme.bitstamp import bitstampRequestsRefactored as bitstamp
from utilita.apriFile import commercialista, portafoglio, ultimo_id_ordine
from utilita.telegramBot import TelegramBot

Fattore_Perdita = 0


def gestore( orderbook ):
	global Fattore_Perdita

	#todo- check if Order is pending? we use IOC/FOK so it shouldn't exist (credo ignori le flag!)
	try:
		# todo -SE NON USI IOC/FOK calcola con un criterio se necessario riassestare il prezzo del 'attuale ordine e quindi magari cancellarlo

		# todo- Check se ultimo ultimo_id_ordine() e' stato completato
		# if YES LOGGA: Ordine [buy|sell] completo al prezzo di N VALUTA_SOLDI per N VALUTA_CRIPTO di N VALUTA_CRIPTO
		cripto, soldi = portafoglio()

		bids_price = orderbook[ 'bids' ][ 0 ][ 0 ]
		bids_amount = orderbook[ 'bids' ][ 0 ][ 0 ]

		asks_price = orderbook[ 'asks' ][ 0 ][ 0 ]
		asks_amount = orderbook[ 'asks' ][ 0 ][ 0 ]

		if asks_amount * asks_price >= soldi:
			# Compro
			my_amount = soldi / asks_price
			bitstamp.buyLimit( my_amount, asks_price, fok=True )

		ultimo_valore, orders = commercialista()

		if orders:
			for order in orders:
				#check if every order is complete
				#if complete check if sell
				if order[ 'buy' ] and order[ 'order_status'
											] == "finished" and order[
					'price' ] < bids_price and bids_amount <= order[ 'amount' ]:
					# Vendo
					bitstamp.sellLimit(
						order[ 'amount' ], bids_price, fok=True
					)


	except Exception as e:
		raise e
	finally:
		# Aggiorno l'ultimo valore
		commercialista( "ultimo_valore", orderbook )


def forOrderCheck( data ):
	buy_order_id = data[ 'buy_order_id' ]
	sell_order_id = data[ 'sell_order_id' ]
	amount = data[ 'amount' ]

	#todo- if ultimo_id_ordine() NOT presente entrambi gli ID,allora non e' stato completato
	#else:
	# aggiorna valori.json togliendo l ID
	# synca l amount per creare la frazione di order
	pass


#if tg_bot:
#todo- printa tutti i reason

#	tg_bot.sendMessage(TELEGRAM_ID, result['reason']['__all__'][0])
