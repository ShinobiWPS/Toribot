import json
import logging
import os
import sys
from datetime import datetime

import utilita.gestoreRapporti as gestoreRapporti
from costanti.api import API_TOKEN_HASH, TELEGRAM_ID
from costanti.coppia_da_usare import (COPPIA_DA_USARE_NOME,
                                      VALUTA_CRIPTO,
                                      VALUTA_SOLDI)
from costanti.log_cartella_percorso import TRADING_REPORT_FILENAME
from piattaforme.bitstamp.bitstampRequests import (buy, getBalance,
                                                   getOrderStatus, sell)
from utilita.apriFile import commercialista, portafoglio, ultimo_id_ordine
from utilita.telegramBot import TelegramBot

# Se Fattore d'approssimazione a 8 Strategia B, se inferiore di 8 strategia B+An
BR_Fattore_Approssimazionoe = 8
BR_Fattore_Perdita = 10
FEE = 0.0

primo_acquisto = True
closing = False
force_sell = False
force_buy = False



def gestore(valore_attuale):
	global primo_acquisto, closing, BR_Fattore_Approssimazionoe
	cripto, soldi = portafoglio()

	try:
		#_______INIZIO STRATEGIA_____________________________________

		#_____________________ Comprare _____________________________
		# Se ho soldi
		if soldi and not closing:
			ultimo_valore, valore_acquisto = commercialista()

			# Se il valore attuale è maggiore dell'ultimo valore
			#todo-fai round all inizio e basta,rimuovi i round sparsi
			if round(
			    valore_attuale,
			    BR_Fattore_Approssimazionoe) < ultimo_valore or primo_acquisto:
				primo_acquisto = False
				# Compro
				compro(soldi, valore_attuale)
		#_____________________ Vendere _____________________________
		# Se ho criptomonete
		elif cripto:
			ultimo_valore, valore_acquisto = commercialista()

			# Se il valore attuale è maggiore dal valore d'acquisto (in caso opposto perderei i soldi)
			# if BR_Fattore_Perdita == None or valore_acquisto - round(valore_attuale,BR_Fattore_Approssimazionoe) <= BR_Fattore_Perdita - (cripto*valore_attuale*0.5/100):
			if valore_acquisto < valore_attuale :
			#if valore_acquisto - valore_attuale <= BR_Fattore_Perdita - (valore_attuale*FEE/100*2):
				# Se il valore attuale è minore dell'ultimo valore, sta scendendo (forse)
				#if round(valore_attuale,BR_Fattore_Approssimazionoe) > ultimo_valore:
					# Vendo
				vendo(cripto, valore_attuale)
		#_______FINE STRATEGIA_____________________________________

		cripto, soldi = portafoglio()
		if soldi and force_buy:
			compro(soldi, valore_attuale)
		if cripto and force_sell:
			vendo(cripto, valore_attuale)


	except Exception as e:
		raise e
	finally:
		# Aggiorno l'ultimo valore
		commercialista("ultimo_valore", valore_attuale)



def compro(soldi, valore_attuale):
	try:
		tg_bot = TelegramBot()
		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

		if "dev" in sys.argv[1:]:
			cripto_converted = soldi / valore_attuale
			cripto_feeded = cripto_converted - cripto_converted * FEE / 100
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Acquisto al prezzo di [" + str(valore_attuale) + "] usando " +
						str(soldi) + VALUTA_SOLDI +" -> " +
						str(round(cripto_feeded, 8)) + " " + VALUTA_CRIPTO)
			commercialista("valore_acquisto", valore_attuale)
			portafoglio("cripto", round(cripto_feeded, 8))
			portafoglio("soldi", 0)
		else:

			# balance
			balance = json.loads(getBalance())
			if balance:
				gestoreRapporti.JsonWrites("log/buy_balance.json","w+",balance)
				#cripto_balance = float(balance[f"{VALUTA_SOLDI}balance"]) if f"{VALUTA_CRIPTO}_balance" in balance else None
				soldi_balance = float(balance[f"{VALUTA_SOLDI}_balance"]) if f"{VALUTA_SOLDI}_balance" in balance else None
				fee = float(balance[f"{COPPIA_DA_USARE_NOME}_fee"]) if f"{COPPIA_DA_USARE_NOME}_fee" in balance else None

				# check order status
				ultimo_id = ultimo_id_ordine()
				if ultimo_id:
					status = json.loads(getOrderStatus(ultimo_id))
					gestoreRapporti.JsonWrites("log/buy_getOrderStatus.json","w+",status)
					status = status["status"] if "status" in status else None

				if soldi and soldi_balance and soldi != soldi_balance:
					gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Discrepanza!: "+str(soldi_balance-soldi))

				if soldi_balance and ( not ultimo_id or not status or ( status and status.lower() == "finished")):

					# order
					soldi_balance_feeded = soldi_balance - ( soldi_balance * fee / 100 )
					#result = json.loads(buy(round(valore_attuale,5),round(soldi_balance / valore_attuale,8)))
					result = json.loads(buy(soldi_balance))

					gestoreRapporti.JsonWrites("log/buy_buy.json","w+",result)
					print(">>> Buy result:")
					print(result)
					if "id" in result:
						ultimo_id_ordine(result["id"] if "id" in result else None)
						prezzo_ordine = float(result["price"]) if "price" in result else None

						gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Acquisto al prezzo di [" + str(prezzo_ordine) + "] usando " +
									str(soldi_balance_feeded)+ VALUTA_SOLDI + " -> " +
									str(round(soldi_balance_feeded / prezzo_ordine, 8))+ " " + VALUTA_CRIPTO)
						commercialista("valore_acquisto", prezzo_ordine)
						portafoglio("cripto", round(soldi_balance_feeded / prezzo_ordine, 8))
						portafoglio("soldi", 0)

					else:
						if soldi_balance:
							portafoglio("soldi", soldi_balance)

						if tg_bot:
							tg_bot.sendMessage(TELEGRAM_ID, result['reason']['__all__'][0]) #todo- printa tutti i reason

						# logging.error(result["status"]+": "+result["reason"])
						logging.error(result)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		logging.info(e)
		logging.info(exc_type)
		logging.info(fname)
		logging.info(f'Line: {exc_tb.tb_lineno}')
		print(e, exc_type, fname, exc_tb.tb_lineno)


def vendo(cripto, valore_attuale):

	try:


		tg_bot = TelegramBot()


		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

		if "dev" in sys.argv[1:]:
			soldi_converted = cripto * valore_attuale
			soldi_feeded = soldi_converted - soldi_converted * FEE / 100
			# Resetto il valore d'acquisto, dato che non ho più roba
			commercialista("valore_acquisto", 0)
			gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Vendita al prezzo di [" + str(valore_attuale) + "] usando " +
						str(cripto) + VALUTA_CRIPTO + " -> " +
						str(round(soldi_feeded, 8))+  VALUTA_SOLDI)
			portafoglio("soldi", round(soldi_feeded, 5))
			portafoglio("cripto", 0)
		else:
			# balance
			balance = json.loads(getBalance())
			if balance:
				gestoreRapporti.JsonWrites("log/sell_balance.json","w+",balance)
				cripto_balance = float(balance[f"{VALUTA_CRIPTO}_balance"]) if f"{VALUTA_CRIPTO}_balance" in balance else None
				# soldi_balance = float(balance[f"VALUTA_USATASOLDI_balance"]) if f"VALUTA_USATASOLDI_balance" in balance else None
				fee = float(balance[f"{COPPIA_DA_USARE_NOME}_fee"]) if f"{COPPIA_DA_USARE_NOME}_fee" in balance else None

				# check order status
				ultimo_id = ultimo_id_ordine()
				if ultimo_id:
					status = json.loads(getOrderStatus(ultimo_id))
					gestoreRapporti.JsonWrites("log/sell_getOrderStatus.json","w+",status)
					status = status["status"] if "status" in status else None

				if cripto and cripto_balance and cripto != cripto_balance:
					gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Aggiunta cripto manualmente: "+str(cripto_balance-cripto))

				if cripto_balance and ( not ultimo_id or not status or ( status and status.lower() == "finished")):
					# order
					#result = json.loads(sell(round(cripto_balance,8)))
					result = json.loads(sell(cripto_balance))
					print(">>> Sell result:")
					print(result)
					gestoreRapporti.JsonWrites("log/sell_sell.json","w+",result)
					if "id" in result:
						ultimo_id_ordine(result["id"] if "id" in result else None)
						prezzo_ordine = float(result["price"]) if "price" in result else None

						soldi_converted = cripto_balance * valore_attuale
						soldi_feeded = soldi_converted - ( soldi_converted * fee / 100 )

						# Resetto il valore d'acquisto, dato che non ho più roba
						commercialista("valore_acquisto", 0)
						gestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Vendita al prezzo di [" + str(prezzo_ordine) + "] usando " +
									str(cripto_balance) +VALUTA_CRIPTO + " -> " +
									str(round(soldi_feeded, 8))+ VALUTA_SOLDI)
						portafoglio("soldi", round(soldi_feeded, 5))
						portafoglio("cripto", 0)

					else:
						if cripto_balance:
							portafoglio("cripto", cripto_balance)

						if tg_bot:
							tg_bot.sendMessage(TELEGRAM_ID,result['reason']['__all__'][0]) #tod- same as above


						# logging.error(result["status"]+": "+result["reason"])
						logging.error(result)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		logging.info(e)
		logging.info(exc_type)
		logging.info(fname)
		logging.info(f'Line: {exc_tb.tb_lineno}')
		print(e, exc_type, fname, exc_tb.tb_lineno)
