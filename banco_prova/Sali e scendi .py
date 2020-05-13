import json
import os
#from telegrambotprova import nuovo_mexbot


""" attuale = 0.17
print("sono entrato nel compra e vendi") """

print(os.getcwd())
with open("banco_prova/valoriprova.json", "r") as jsonFile:
    print('pre')
    data = json.load(jsonFile)
    print('post')
    print(data)

""" data = json.load(open("valoriprova.json")) """


""" rif = data['riferimento']
acq = data['acquisto'] """
# nuovo_mexbot("Ho Venduto")

""" print('questo è il valore di riferimento')
print(rif)
print(acq)

if attuale > acq:
    print("valore maggiore dell'acquisto")
    if attuale-rif > 0:
        print("sta crescendo")
    else:
        print("sta scendendo")


else:
    print("valore minore dell'acquisto") """
"""
data = {'riferimento': attuale, 'acquisto': acq}

with open("valori.json", "w") as outfile:
	json.dump(data, outfile)
"""
""" data["riferimento"] = attuale """
""" with open("valoriprova.json", "w+") as outfile:
	json.dump(data, outfile) """
