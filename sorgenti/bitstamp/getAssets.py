import hashlib
import hmac
import time
import requests
import uuid
import sys
from urllib.parse import urlencode


def getAssets():
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
    return [r.content['xrp_available'], r.content['eur_available']]
