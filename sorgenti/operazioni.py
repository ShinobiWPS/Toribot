import json


def seComprareOVendere(parameter_list):
    pass


def compra(parameter_list):
    pass


def vendi(parameter_list):
    pass


def aggiornaPortafoglio(xrp, eur):
    """Scrivi su file o in variabili i cambiamenti di XRP e EUR

    Arguments:
        xrp {int} -- il valore da sommare di XRP
        eur {int} -- il valore da sommare di EUR
    """
    with open('portafoglio.json', 'w') as file:
        fileData = file.read()
        portafoglioDict = json.loads(fileData)
        # accedi alle chiavi ad esempio con:
        # portafoglioDict['xrp']

        # todo- dato un numero gia esistente di quantita nel portafolgio
        # bisogna sottrarre quando vendiamo XRP e sommare quando compriamo, viceversa per gli EUR
        # suggerimento- se python supporta i numeri negativi possiamo sommare sempre e ci togliamo il pensiero
        # perche se abbiamo venduto  12 XRP e ne avevamo 20, basta fare 20 + -12
