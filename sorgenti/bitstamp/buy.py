import hashlib
import hmac
import time
import requests
import uuid
import sys
from urllib.parse import urlencode


def buy(xrp):
    """Buy order

	Arguments:

		xrp {float} -- ammontare di XRP

	Raises:

		Exception: ('Status code not 200')
		Exception: ('Signatures do not match')

	Returns:

		dict -- response object
	"""
    payload = {'amount': '100'}

    payload_string = urlencode(payload)

    # '' (empty string) in message represents any query parameters or an empty string in case there are none
    message = 'BITSTAMP ' + api_key + \
             'POST' + \
             'www.bitstamp.net' + \
             '/api/v2/buy/instant/xrpeur/' + \
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
        'https://www.bitstamp.net/api/v2/buy/instant/xrpeur/',
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

    # {"status": "error", "reason": {"__all__": ["You have only 0.00000 EUR available. Check your account balance for details."]}}
    return r.content
