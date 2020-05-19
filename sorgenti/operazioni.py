# -*- coding: utf-8 -*-
import json
import logging
from costanti.valori_percorso import VALORI_PERCORSO
from costanti.portafoglio_percorso import PORTAFOGLIO_PERCORSO
from utilita.apriFile import Portafoglio, Commercialista


def Gestore(valore_attuale):
	cripto, soldi = Portafoglio()

	#_______INIZIO STRATEGIA_____________________________________

	#_____________________ Comprare _____________________________
	# Se ho soldi
	if soldi:
		ultimo_valore, valore_acquisto = Commercialista()

		# Se il valore attuale è maggiore dell'ultimo valore
		if valore_attuale > ultimo_valore:
			# Compro
			logging.info("Acquisto [" + str(valore_attuale) + "] " +
			             str(soldi) + " -> " +
			             str(round(soldi / valore_attuale, 8)))
			Commercialista("valore_acquisto", valore_attuale)
			Portafoglio("cripto", round(soldi / valore_attuale, 8))
			Portafoglio("soldi", 0)

	#_____________________ Vendere _____________________________
	# Se ho criptomonete
	elif cripto:
		ultimo_valore, valore_acquisto = Commercialista()

		# Se il valore attuale è maggiore dal valore d'acquisto (in caso opposto perderei i soldi)
		if valore_attuale > valore_acquisto:
			# Se il valore attuale è minore dell'ultimo valore, sta scendendo (forse)
			if valore_attuale < ultimo_valore:
				# Resetto il valore d'acquisto, dato che non ho più roba
				Commercialista("valore_acquisto", 0)
				# Vendo
				logging.info("Vendita [" + str(valore_attuale) + "] " +
				             str(cripto) + " -> " +
				             str(round(cripto * valore_attuale, 8)))
				Portafoglio("soldi", round(cripto * valore_attuale, 5))
				Portafoglio("cripto", 0)

	#_______FINE STRATEGIA_____________________________________

	# Aggiorno l'ultimo valore
	Commercialista("ultimo_valore", valore_attuale)
