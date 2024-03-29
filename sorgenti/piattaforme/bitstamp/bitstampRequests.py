import hashlib
import hmac
import json
import logging
import sys
import time
import uuid
from urllib.parse import urlencode

import requests

from costanti.costanti_unico import (COPPIA_DA_USARE_NOME, VALUTA_CRIPTO, VALUTA_SOLDI)
from piattaforme.bitstamp.key import API_SECRET, CUSTOMER_ID
from piattaforme.bitstamp.key import api_key as API_KEY
from piattaforme.bitstamp.key import client_id as CLIENT_ID

#Public


def sellInstant(amount):
	return makeInstantOrder("sell", amount)


def sellLimit(amount, price, ioc=None, fok=None):
	return makeLimitOrder("sell", amount, price, ioc=ioc, fok=fok)


def buyInstant(amount):
	return makeInstantOrder("buy", amount)


def buyLimit(amount, price, ioc=None, fok=None):
	return makeLimitOrder("buy", amount, price, ioc=ioc, fok=fok)


def makeInstantOrder(buyOrSell, amount):
	return makeRequest(operation="limit", buyOrSell=buyOrSell, amount=amount)


def makeLimitOrder(buyOrSell, amount, price, ioc=None, fok=None):
	return makeRequest(
		operation="limit", buyOrSell=buyOrSell, amount=amount, price=price, ioc=ioc, fok=fok
	)


def checkOrder(order_id):
	return makeRequest(operation="status", order_id=order_id)


def getBalance():
	return makeRequest(operation="balance")


def getOrderbook():
	return makeRequest(operation="orderbook")


#Private


def makeRequest(
	operation=None, buyOrSell=None, amount=None, price=None, ioc=None, fok=None, order_id=None
):

	timestamp = str(int(round(time.time() * 1000)))
	nonce = str(uuid.uuid4())

	payload = {}
	operation_string = ""
	bos = ""  # Se true mette bos e coppia
	put_couple = False  # Se true mette la coppia
	api_version = 2
	content_type = ""

	if not operation:
		raise Exception("Parameter missing")

	if operation.lower() == "instant":

		operation_string = f"{operation.lower()}/"

		if not amount:
			raise Exception("Parameter missing")

		payload['amount'] = float(amount)

		if buyOrSell.lower() == "buy":
			bos = buyOrSell.lower()
		elif buyOrSell.lower() == "sell":
			bos = buyOrSell.lower()
		else:
			if buyOrSell:
				raise Exception("Parameter error")
			else:
				raise Exception("Parameter missing")

		content_type = 'application/x-www-form-urlencoded'

	elif operation.lower() == "limit":

		operation_string = ""

		if not amount:
			raise Exception("Parameter missing")
		if not price:
			raise Exception("Parameter missing")

		payload['amount'] = float(amount)
		payload['price'] = float(price)
		if ioc:
			payload['ioc_order'] = bool(ioc)
		if fok:
			payload['fok_order'] = bool(fok)

		if buyOrSell.lower() == "buy":
			bos = buyOrSell.lower()
		elif buyOrSell.lower() == "sell":
			bos = buyOrSell.lower()
		else:
			if buyOrSell:
				raise Exception("Parameter error")
			else:
				raise Exception("Parameter missing")

		content_type = 'application/x-www-form-urlencoded'

	elif operation.lower() == "status":

		operation_string = "order_status/"

		if not order_id:
			raise Exception("Parameter missing")

		payload['id'] = order_id
		api_version = 1

	elif operation.lower() == "balance":

		operation_string = "balance/"

	elif operation.lower() == "orderbook":

		operation_string = "order_book/"
		put_couple = True

	else:
		raise Exception("Unkown API")

	payload_URLencoded = urlencode(payload)

	if api_version == 2:
		message = 'BITSTAMP ' + API_KEY + \
            'POST' + \
            'www.bitstamp.net' + \
            f'/api/v2/{operation_string}'+(f'{bos}/{COPPIA_DA_USARE_NOME}/' if bos else '') + \
            '' + \
            (content_type if content_type else "") + \
            nonce + \
            timestamp + \
            'v2' + \
            payload_URLencoded
		message = message.encode('utf-8')
		signature = hmac.new(API_SECRET, msg=message, digestmod=hashlib.sha256).hexdigest().upper()
	else:
		nonce = str(int(time.time() * 10))
		message = nonce + str(CUSTOMER_ID) + str(API_KEY)
		message = message.encode('utf-8')
		signature = hmac.new(API_SECRET, msg=message, digestmod=hashlib.sha256).hexdigest().upper()
		payload['signature'] = signature
		payload['nonce'] = nonce
		payload['key'] = API_KEY
		payload_URLencoded = urlencode(payload)

	headers = {
		'X-Auth': 'BITSTAMP ' + API_KEY,
		'X-Auth-Signature': signature,
		'X-Auth-Nonce': nonce,
		'X-Auth-Timestamp': timestamp,
		'X-Auth-Version': 'v2'
	}

	if content_type:
		headers['Content-Type'] = content_type

	if api_version == 2:
		r = requests.post(
			f'https://www.bitstamp.net/api/v2/{operation_string}' +
			(f'{bos}/{COPPIA_DA_USARE_NOME}/' if bos else '') +
			(f'{COPPIA_DA_USARE_NOME}/' if put_couple else ''),
			headers=headers,
			data=payload_URLencoded
		)

	else:
		r = requests.post(
			f'https://www.bitstamp.net/api/{operation_string}/',
			# headers=headers,
			data=payload
		)

	if not r.status_code == 200:
		if 'reason' in json.loads(r.content):
			logging.info(json.loads(r.content)['reason'])
		raise Exception('Status code not 200')

	if content_type:
		string_to_sign = (nonce + timestamp +
			r.headers.get('Content-Type')).encode('utf-8') + r.content
		signature_check = hmac.new(API_SECRET, msg=string_to_sign,
			digestmod=hashlib.sha256).hexdigest()
		if not r.headers.get('X-Server-Auth-Signature') == signature_check:
			raise Exception('Signatures do not match')

	return r.content

	# _______ OPPURE ________
	# try:
	# 	return json.loads(r.content)
	# except ValueError:
	# 	return r.content
	# finally:
	# 	return None
