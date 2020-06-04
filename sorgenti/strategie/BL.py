import json
import logging
import os
import sys
from datetime import datetime

import utilita.gestoreRapporti as gestoreRapporti
from costanti.api import API_TOKEN_HASH, TELEGRAM_ID
from costanti.costanti_unico import (COPPIA_DA_USARE_NOME, FEE,
                                     TRADING_REPORT_FILENAME, VALUTA_CRIPTO)
from utilita.apriFile import commercialista, portafoglio, ultimo_id_ordine
from utilita.telegramBot import TelegramBot

Fattore_Perdita=0

def gestore(orderbook):
	global Fattore_Perdita



	#todo- check if Order is pending? we use IOC/FOK so it shouldn't exist (credo ignori le flag!)
	try:
		# todo- calcola con un criterio se necessario riassestare il prezzo del 'attuale ordine e quindi magari cancellarlo

		# todo- Check se ultimo ultimo_id_ordine() e' stato completato
		# if YES LOGGA: Ordine [buy|sell] completo al prezzo di N VALUTA_SOLDI per N VALUTA_CRIPTO di N VALUTA_CRIPTO

		pass
	except Exception as e:
		raise e
	finally:
		# Aggiorno l'ultimo valore
		commercialista("ultimo_valore", orderbook)
