# -*- coding: utf-8 -*-
import json
from costanti.valori_percorso import VALORI_PERCORSO
from costanti.portafoglio_percorso import PORTAFOGLIO_PERCORSO
from utilita.apriFile import Portafoglio, Commercialista
import logging

def Gestore(valore_attuale):
	cripto, soldi = Portafoglio()

	if soldi:
		# Decide se comprare e nel caso compra
		ultimo_valore, valore_acquisto = Commercialista()
		
		if valore_attuale > ultimo_valore:
			Commercialista(valore_acquisto)
			Portafoglio("cripto", soldi * valore_attuale)
			Portafoglio("soldi", 0)

	elif cripto:
		# Decide se vendere e nel caso vende
		ultimo_valore, valore_acquisto = Commercialista()

		if valore_attuale > valore_acquisto:
			if valore_attuale > ultimo_valore:
				Commercialista("ultimo_valore", ultimo_valore)
			else:
				Portafoglio("soldi", cripto * valore_attuale)
				Portafoglio("cripto", 0)

