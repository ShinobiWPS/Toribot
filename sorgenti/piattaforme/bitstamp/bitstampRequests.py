import hashlib
import hmac
import sys
import time
import uuid
from urllib.parse import urlencode

import requests

from piattaforme.bitstamp.key import API_SECRET, api_key, client_id

content_type = 'application/x-www-form-urlencoded'

def buy(price:float,cripto:float):
	return buyORsell('buy',str(price), str(cripto))

def sell(price:float,cripto:float):
	return buyORsell('sell', str(price),str(cripto))


def buyORsell(operation:str,price:str,cripto:str):
	"""Make a BUY or SELL request

	Arguments:

		operation {str} -- operazione
		price {str} -- prezzo del XRP
		cripto {str} -- ammontare di XRP

	Raises:

		Exception: ('Status code not 200')
		Exception: ('Signatures do not match')

	Returns:

		dict-- contenuto della risposta completo
	"""
	timestamp = str(int(round(time.time() * 1000)))
	nonce = str(uuid.uuid4())
	payload = {
		'price':price,
		'amount':cripto,
		# vogliamo che si esegua come un instant Order
		'ioc_order ': 'True',
		'fok_order ': 'True',
		}
	payload_string = urlencode(payload)

	# '' (empty string) in message represents any query parameters or an empty string in case there are none
	message = 'BITSTAMP ' + api_key + \
			 'POST' + \
			 'www.bitstamp.net' + \
			 f'/api/v2/{operation}/instant/xrpeur/' + \
			 '' + \
			 content_type + \
			 nonce + \
			 timestamp + \
			 'v2' + \
			 payload_string
	message = message.encode('utf-8')
	signature = hmac.new(API_SECRET, msg=message,
						 digestmod=hashlib.sha256).hexdigest()
	headers = {
		'X-Auth': 'BITSTAMP ' + api_key,
		'X-Auth-Signature': signature,
		'X-Auth-Nonce': nonce,
		'X-Auth-Timestamp': timestamp,
		'X-Auth-Version': 'v2',
		'Content-Type': content_type
	}
	r = requests.post(
		f'https://www.bitstamp.net/api/v2/{operation}/instant/xrpeur/',
		headers=headers,
		data=payload_string
	)


	if not r.status_code == 200:
		print(r.content)
		raise Exception('Status code not 200')

	string_to_sign = (nonce + timestamp + r.headers.get('Content-Type')
					 ).encode('utf-8') + r.content
	signature_check = hmac.new(
		API_SECRET, msg=string_to_sign, digestmod=hashlib.sha256
	).hexdigest()
	if not r.headers.get('X-Server-Auth-Signature') == signature_check:
		raise Exception('Signatures do not match')

	print(r.content)
	# ON BUY ERROR: {"status": "error", "reason": {"__all__": ["You have only 0.00000 EUR available. Check your account balance for details."]}}
	# todo- ON SELL ERROR:
	return r.content

def getBalance():
	"""Ottieni XRP ed EUR disponibili

	Returns:
		list -- array di XRP,EUR disponibili
	"""
	timestamp = str(int(round(time.time() * 1000)))
	nonce = str(uuid.uuid4())
	payload = {}

	payload_string = urlencode(payload)

	# '' (empty string) in message represents any query parameters or an empty string in case there are none
	message = 'BITSTAMP ' + api_key + \
			  'POST' + \
			  'www.bitstamp.net' + \
			  '/api/v2/balance/' + \
			  '' + \
			  nonce + \
			  timestamp + \
			  'v2' + \
			  payload_string
	message = message.encode('utf-8')
	signature = hmac.new(API_SECRET, msg=message,
						 digestmod=hashlib.sha256).hexdigest()
	headers = {
		'X-Auth': 'BITSTAMP ' + api_key,
		'X-Auth-Signature': signature,
		'X-Auth-Nonce': nonce,
		'X-Auth-Timestamp': timestamp,
		'X-Auth-Version': 'v2',
	}
	r = requests.post(
		'https://www.bitstamp.net/api/v2/balance/',
		headers=headers,
		data=payload_string
	)
	# /balance puo' failare solo per colpa dell'autenticazione, non ha risposte negative
	return r.content

def getOrderStatus(order_id):
	"""Ottieni XRP ed EUR disponibili

	Returns:
		list -- array di XRP,EUR disponibili
	"""
	timestamp = str(int(round(time.time() * 1000)))
	nonce = str(uuid.uuid4())
	payload = {'id':order_id}

	payload_string = urlencode(payload)

	# '' (empty string) in message represents any query parameters or an empty string in case there are none
	message = 'BITSTAMP ' + api_key + \
			  'POST' + \
			  'www.bitstamp.net' + \
			  '/api/order_status/' + \
			  '' + \
			  nonce + \
			  timestamp + \
			  'v2' + \
			  payload_string
	message = message.encode('utf-8')
	signature = hmac.new(API_SECRET, msg=message,
						 digestmod=hashlib.sha256).hexdigest()
	headers = {
		'X-Auth': 'BITSTAMP ' + api_key,
		'X-Auth-Signature': signature,
		'X-Auth-Nonce': nonce,
		'X-Auth-Timestamp': timestamp,
		'X-Auth-Version': 'v2',
	}
	r = requests.post(
		'https://www.bitstamp.net/api/order_status/',
		headers=headers,
		data=payload_string
	)

	return r.content
