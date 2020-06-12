import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from costanti.costanti_unico import (FORMATO_DATA_ORA, VALORI_PERCORSO, VALORI_TEMPLATE_PERCORSO)


def gestoreValoriJson(chiave=None, valore=None):
	# try:

	Path(VALORI_PERCORSO).parent.mkdir(parents=True, exist_ok=True)
	if not os.path.exists(VALORI_PERCORSO) and os.path.exists(VALORI_TEMPLATE_PERCORSO):
		with open(str(VALORI_TEMPLATE_PERCORSO).strip(), "r") as file:
			template = file.read().strip()
		with open(str(VALORI_PERCORSO).strip(), "w") as file:
			file.write(template.strip())

	with open(VALORI_PERCORSO, 'r+') as jsonFile:
		if chiave is not None and valore is not None:
			# try:
			valori_json = json.loads(jsonFile.read())

			jsonFile.seek(0)

			if isinstance(chiave, list):
				tmp_config = valori_json
				for key in chiave[:-1]:
					if (isinstance(tmp_config, dict) and key
						in tmp_config) or (isinstance(tmp_config, list) and key < len(tmp_config)):
						if not isinstance(tmp_config[key],
							dict) and not isinstance(tmp_config[key], list):
							del tmp_config[key]
							tmp_config[key] = {}
						tmp_config = tmp_config[key]
					else:
						tmp_config[key] = {}
						tmp_config = tmp_config[key]
				if isinstance(chiave, list) or isinstance(chiave, dict):
					if isinstance(tmp_config[chiave[-1]], list):
						tmp_config[chiave[-1]].append(valore)
					else:
						tmp_config[chiave[-1]] = valore
				else:
					valore = str(valore)
					if valore.lower() == "True".lower() or valore.lower() == "False".lower():
						tmp_config[chiave[-1]] = True if valore.lower() == "True".lower() else False
					elif valore.replace('-', '', 1).isdigit() and valore[1:].find('-') == -1:
						tmp_config[chiave[-1]] = int(valore)
					elif valore.replace('-', '', 1).replace('.', '', 1).replace(',', '',
						1).isdigit() and valore[1:].find('-') == -1:
						tmp_config[chiave[-1]] = float(valore)
					else:
						tmp_config[chiave[-1]] = valore

				if valore == "":
					del tmp_config[chiave[-1]]

			else:
				if isinstance(valori_json[chiave], list):
					valori_json[chiave].append(valore)
				else:
					valori_json[chiave] = valore

			jsonFile.write(json.dumps(valori_json, sort_keys=True, indent=4))
			jsonFile.truncate()

			return valori_json
			#except Exception as ex:
			#	# In caso di eccezioni printo e loggo tutti i dati disponibili
			#	exc_type, exc_obj, exc_tb = sys.exc_info()
			#	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			#	print(ex, exc_type, fname, exc_tb.tb_lineno)
			#	logging.error(ex)
		else:
			return json.loads(jsonFile.read())
	# except Exception as ex:
	# 	# In caso di eccezioni printo e loggo tutti i dati disponibili
	# 	exc_type, exc_obj, exc_tb = sys.exc_info()
	# 	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	# 	print(ex, exc_type, fname, exc_tb.tb_lineno)
	# 	logging.error(ex)


def portafoglio(chiave=None, valore=None):
	valori_json = gestoreValoriJson(chiave, valore)
	if valori_json and "cripto" in valori_json and "soldi" in valori_json:
		return [valori_json["cripto"], valori_json["soldi"]]
	return [ None, None ]


def commercialista(chiave=None, valore=None):
	valori_json = gestoreValoriJson(chiave, valore)
	if valori_json and "ultimo_valore" in valori_json and "orders" in valori_json:
		return [valori_json["ultimo_valore"], valori_json["orders"]]
	return [ None, None ]


def getOrders(chiave='order_id', valore=None):
	orders = []
	valori_json = gestoreValoriJson()
	if valore:
		for order in valori_json['orders']:
			if str(order[chiave]) == str(valore):
				orders.append(order)
		return orders if orders else None
	else:
		if valori_json and "orders" in valori_json:
			return valori_json["orders"]
	return None


def addOrder(amount, price, order_id, bos, timestamp=None, my_datetime=None, order_status=None):

	if timestamp == None:
		timestamp = datetime.now()
	if not order_status:
		order_status = "processing"
	if not my_datetime:
		my_datetime = timestamp.strftime(FORMATO_DATA_ORA)
	order = {
		'amount': amount,
		'price': price,
		'order_id': order_id,
		'order_status': order_status,
		'bos': bos,
		'timestamp': time.mktime(timestamp.timetuple()),
		'datetime': my_datetime
	}
	valori_json = gestoreValoriJson("orders", order)
	if valori_json and "orders" in valori_json:
		return valori_json["orders"]
	return None


def searchOrder(chiave='order_id', valore=None):
	orders = gestoreValoriJson()['orders']
	for index, order in enumerate(orders):
		if str(order[chiave]) == str(valore):
			return index
	return None


def removeOrder(chiave='order_id', valore=None):
	index = searchOrder(chiave=chiave, valore=valore)
	valori_json = gestoreValoriJson([ "orders", index ], "")
	if valori_json and "orders" in valori_json:
		return valori_json["orders"]
	return None
