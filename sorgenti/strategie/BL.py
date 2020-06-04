import json
import logging
import os
import sys
from datetime import datetime

import utilita.gestoreRapporti as gestoreRapporti
from costanti.api import API_TOKEN_HASH, TELEGRAM_ID
from costanti.costanti_unico import (COPPIA_DA_USARE_NOME, FEE,
                                     TRADING_REPORT_FILENAME,
                                     VALUTA_DA_USARE_CRIPTO,
                                     VALUTA_DA_USARE_SOLDI)
from piattaforme.bitstamp.bitstampRequests import (buy, getBalance,
                                                   getOrderStatus, sell)
from utilita.apriFile import commercialista, portafoglio, ultimo_id_ordine
from utilita.telegramBot import TelegramBot

Fattore_Perdita=0

def gestore():
	global Fattore_Perdita

	#todo- calcola se necessario riassestare il prezzo del 'attuale ordine

	#todo- check if Order is pending? I use FOK so it shouldn't exist
	try:
		pass
	except Exception as e:
		raise e
	finally:
		# Aggiorno l'ultimo valore
		commercialista("ultimo_valore", valore_attuale)
