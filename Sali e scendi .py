
# valore d'acquisto = AC
# valore attuale = AT
# valore di riferimento = RF

import requests
import json


# api xpl per valori della valuta
val1 = ('https://data.ripple.com/v2/exchanges/USD+rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2q/XRP?descending=true&limit=3&result=tesSUCCESS&type=OfferCreate')
val2 = ('http://echo.jsontest.com/key/value/one/two')

r = requests.get(val1)
js = r.json()

print(js)
jslist = js['exchanges']


o = json.JSONDecoder().decode(js)

print(type(jslist))


data = json.loads(jslist)


for element in data['drinks']:
    print(element)

AC = 0.33
AT = 0.35

if AT > AC:
    RF = AT
    while True:
        if AT-RF > 0:
            print("sta crescendo")
        else:
            print("sta scendendo")
            break
