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
			Commercialista("valore_acquisto", valore_attuale)
			Portafoglio("cripto", soldi * valore_attuale)
			Portafoglio("soldi", 0)

	#_____________________ Vendere _____________________________
	# Se ho criptomonete
	elif cripto:
		ultimo_valore, valore_acquisto = Commercialista()

		# Se il valore attuale è maggiore dal valore d'acquisto (in caso opposto perderei i soldi)
		if valore_attuale > valore_acquisto:
			# Se il valore attuale è minore dell'ultimo valore, sta scendendo (forse)
			if valore_attuale < ultimo_valore:
				# Vendo
				Portafoglio("soldi", cripto * valore_attuale)
				Portafoglio("cripto", 0)

	#_______FINE STRATEGIA_____________________________________

	# Aggiorno l'ultimo valore
	Commercialista("ultimo_valore", valore_attuale)

