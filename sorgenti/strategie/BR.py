import json
import logging
import os
import sys
from datetime import datetime

import utilita.GestoreRapporti as GestoreRapporti
from costanti.log_cartella_percorso import TRADING_REPORT_FILENAME
from piattaforme.bitstamp.bitstampRequests import (buy, getBalance,
                                                   getOrderStatus, sell)
from utilita.apriFile import commercialista, portafoglio, ultimo_id_ordine

primo_acquisto = True
# Se Fattore d'approssimazione a 8 Strategia B, se inferiore di 8 strategia B+An
BR_Fattore_Approssimazionoe = 8
BR_Fattore_Perdita = -0.01

def gestore(valore_attuale):
	global primo_acquisto, BR_Fattore_Approssimazionoe
	cripto, soldi = portafoglio()

	try:
		#_______INIZIO STRATEGIA_____________________________________

		logging.info("apply strategy")
		#_____________________ Comprare _____________________________
		# Se ho soldi
		if soldi:
			ultimo_valore, valore_acquisto = commercialista()

			# Se il valore attuale è maggiore dell'ultimo valore
			#todo-fai round all inizio e basta,rimuovi i round sparsi
			if round(
			    valore_attuale,
			    BR_Fattore_Approssimazionoe) < ultimo_valore or primo_acquisto:
				primo_acquisto = False
				# Compro
				logging.info("should buy")
				compro(soldi, valore_attuale)
		#_____________________ Vendere _____________________________
		# Se ho criptomonete
		elif cripto:
			ultimo_valore, valore_acquisto = commercialista()
			# print((cripto*valore_attuale*0.5/100))
			# Se il valore attuale è maggiore dal valore d'acquisto (in caso opposto perderei i soldi)
			# if BR_Fattore_Perdita == None or valore_acquisto - round(valore_attuale,BR_Fattore_Approssimazionoe) <= BR_Fattore_Perdita - (cripto*valore_attuale*0.5/100):
			if cripto*valore_acquisto - cripto*valore_attuale <= BR_Fattore_Perdita - (cripto*valore_attuale*0.5/100*2):
				print(str(cripto*valore_acquisto)+" - "+str(cripto*valore_attuale)+" <= "+str(BR_Fattore_Perdita - (cripto*valore_attuale*0.5/100*2)))
				# Se il valore attuale è minore dell'ultimo valore, sta scendendo (forse)
				if round(valore_attuale,
				         BR_Fattore_Approssimazionoe) > ultimo_valore:
					# Vendo
					logging.info("should sell")
					vendo(cripto, valore_attuale)
		#_______FINE STRATEGIA_____________________________________
	except Exception as e:
		raise e
	finally:
		# Aggiorno l'ultimo valore
		commercialista("ultimo_valore", valore_attuale)



def compro(soldi, valore_attuale):

	try:
		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

		if "dev" in sys.argv[1:]:
			cripto_converted = soldi / valore_attuale
			cripto_feeded = cripto_converted - cripto_converted * 0.5 / 100
			GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Acquisto [" + str(valore_attuale) + "] " +
						str(soldi) + " -> " +
						str(round(cripto_feeded, 8)))
			commercialista("valore_acquisto", valore_attuale)
			portafoglio("cripto", round(cripto_feeded, 8))
			portafoglio("soldi", 0)
		else:

			# balance
			logging.info("buy / balance")
			balance = json.loads(getBalance())
			if balance:
				GestoreRapporti.JsonWrites("log/buy_balance.json","w+",balance)
				cripto_balance = float(balance["xrp_available"]) if "xrp_available" in balance else None
				soldi_balance = float(balance["eur_available"]) if "eur_available" in balance else None
				fee = float(balance["xrpeur_fee"]) if "xrpeur_fee" in balance else None

				# check order status
				ultimo_id = ultimo_id_ordine()
				logging.info("buy / order status")
				if ultimo_id:
					logging.info("buy / last order id: "+str(ultimo_id))
					status = json.loads(getOrderStatus(ultimo_id))
					GestoreRapporti.JsonWrites("log/buy_getOrderStatus.json","w+",status)
					status = status["status"] if "status" in status else None

				if soldi and soldi_balance and soldi != soldi_balance:
					GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Aggiunti soldi manualmente: "+str(soldi_balance-soldi))

				logging.info("can buy1: "+str(soldi_balance))
				logging.info("can buy2: "+str(not ultimo_id ))
				if ultimo_id:
					logging.info("can buy3: "+str(status and status.lower() == "finished"))
				if soldi_balance and ( not ultimo_id or not status or ( status and status.lower() == "finished")):
					# order
					logging.info("buy / buy")
					logging.info(str(soldi_balance)+" -> "+str(soldi_balance / valore_attuale))
					soldi_balance_feeded = soldi_balance - ( soldi_balance * fee / 100 )
					# result = json.loads(buy(round(soldi_balance / valore_attuale,8)))
					result = json.loads(buy(round(soldi_balance,8)))
					GestoreRapporti.JsonWrites("log/buy_buy.json","w+",result)
					if "id" in result:
						logging.info("buy / buy success")
						ultimo_id_ordine(result["id"] if "id" in result else None)
						prezzo_ordine = float(result["price"]) if "price" in result else None

						GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Acquisto [" + str(prezzo_ordine) + "] " +
									str(soldi_balance_feeded) + " -> " +
									str(round(soldi_balance_feeded / prezzo_ordine, 8)))
						commercialista("valore_acquisto", prezzo_ordine)
						portafoglio("cripto", round(soldi_balance_feeded / prezzo_ordine, 8))
						portafoglio("soldi", 0)

					else:
						if soldi_balance:
							portafoglio("soldi", soldi_balance)

						# logging.error(result["status"]+": "+result["reason"])
						logging.error(result)
			else:
				logging.error("Balance api error")
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		logging.info(e)
		logging.info(exc_type)
		logging.info(fname)
		logging.info(exc_tb.tb_lineno)			
		print(e, exc_type, fname, exc_tb.tb_lineno)
	

def vendo(cripto, valore_attuale):

	try:

		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

		if "dev" in sys.argv[1:]:
			soldi_converted = cripto * valore_attuale
			soldi_feeded = soldi_converted - soldi_converted * 0.5 / 100
			# Resetto il valore d'acquisto, dato che non ho più roba
			commercialista("valore_acquisto", 0)
			GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Vendita [" + str(valore_attuale) + "] " +
						str(cripto) + " -> " +
						str(round(soldi_feeded, 8)))
			portafoglio("soldi", round(soldi_feeded, 5))
			portafoglio("cripto", 0)
		else:
			# balance
			logging.info("sell / balance")
			balance = json.loads(getBalance())
			if balance:
				GestoreRapporti.JsonWrites("log/sell_balance.json","w+",balance)
				cripto_balance = float(balance["xrp_available"]) if "xrp_available" in balance else None
				soldi_balance = float(balance["eur_available"]) if "eur_available" in balance else None
				fee = float(balance["xrpeur_fee"]) if "xrpeur_fee" in balance else None

				# check order status
				ultimo_id = ultimo_id_ordine()
				logging.info("sell / order status")
				if ultimo_id:
					logging.info("sell / last order id: "+str(ultimo_id))
					status = json.loads(getOrderStatus(ultimo_id))
					GestoreRapporti.JsonWrites("log/sell_getOrderStatus.json","w+",status)
					status = status["status"] if "status" in status else None

				if cripto and cripto_balance and cripto != cripto_balance:
					GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Aggiunta cripto manualmente: "+str(cripto_balance-cripto))

				logging.info("can sell: "+str(cripto_balance and ( not ultimo_id or ( status and status.lower() == "finished"))))
				if cripto_balance and ( not ultimo_id or not status or ( status and status.lower() == "finished")):
					# order
					logging.info("sell / sell")
					logging.info(str(cripto_balance)+" -> ")
					# result = json.loads(sell(round(cripto_balance * valore_attuale,8)))
					result = json.loads(sell(round(cripto_balance,8)))
					logging.info(result)
					GestoreRapporti.JsonWrites("log/sell_sell.json","w+",result)
					if "id" in result:
						logging.info("sell / sell success")
						ultimo_id_ordine(result["id"] if "id" in result else None)
						prezzo_ordine = float(result["price"]) if "price" in result else None

						soldi_converted = cripto_balance * valore_attuale
						soldi_feeded = soldi_converted - ( soldi_converted * fee / 100 )

						# Resetto il valore d'acquisto, dato che non ho più roba
						commercialista("valore_acquisto", 0)
						GestoreRapporti.FileAppend(TRADING_REPORT_FILENAME,dt_string+" Vendita [" + str(prezzo_ordine) + "] " +
									str(cripto_balance) + " -> " +
									str(round(soldi_feeded, 8)))
						portafoglio("soldi", round(soldi_feeded, 5))
						portafoglio("cripto", 0)

					else:
						if cripto_balance:
							portafoglio("cripto", cripto_balance)

						# logging.error(result["status"]+": "+result["reason"])
						logging.error(result)
			else:
				logging.error("Balance api error")
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		logging.info(e)
		logging.info(exc_type)
		logging.info(fname)
		logging.info(exc_tb.tb_lineno)			
		print(e, exc_type, fname, exc_tb.tb_lineno)
