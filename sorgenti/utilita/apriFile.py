import sys, os
import json
import logging
from costanti.valori_percorso import VALORI_PERCORSO


def GestoreValoriJson(chiave=None, valore=None):
	try:
		with open(VALORI_PERCORSO, 'r+') as jsonFile:
			if chiave is not None and valore is not None:
				try:
					valori_json = json.loads(jsonFile.read())
					jsonFile.seek(0)
					valori_json[chiave] = valore
					jsonFile.write(json.dumps(valori_json, sort_keys=True, indent=4))
					jsonFile.truncate()
					return valori_json
				except Exception as e:
					logging.error(e)
			else:
				return json.loads(jsonFile.read())
	except Exception as e:
		logging.error(e)

def Portafoglio(chiave=None, valore=None):
	valori_json = GestoreValoriJson(chiave, valore)
	if valori_json and "cripto" in valori_json and "soldi" in valori_json:
		return [valori_json["cripto"], valori_json["soldi"]]
	return [None,None]

def Commercialista(chiave=None, valore=None):
	valori_json = GestoreValoriJson(chiave, valore)
	if valori_json and "ultimo_valore" in valori_json and "valore_acquisto" in valori_json:
		return [valori_json["ultimo_valore"], valori_json["valore_acquisto"]]
	return [None,None]
