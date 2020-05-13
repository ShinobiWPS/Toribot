import json


def seComprareOVendere(attuale):
    # ATTUALE: valoro che assume la vaiabile all'evento
    # RIFERIMENTO: valore assunto al precedente evento
    # ACQUISTO: valore di acquisto

    acquisto = 0.180  # sarà un valore assegnato dalla funzione acquisto

    if attuale > acquisto:
        print("valore maggiore dell'acquisto")
           if AT-RF > 0:
                print("sta crescendo")
            else:
                print("sta scendendo")
    else:
        print("valore minore dell'acquisto")

    # assegno al valore di riferimento l'ultimo valore assundo. in modo da confrontarlo con il prossimo
    riferimento = attuale


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
        portafoglioLetto = file.read()
        portafoglioDict = json.loads(portafoglioLetto)
        # accedi alle chiavi ad esempio con:
        # portafoglioDict['xrp']

        # todo- dato un numero gia esistente di quantita nel portafolgio
        # bisogna sottrarre quando vendiamo XRP e sommare quando compriamo, viceversa per gli EUR
        # suggerimento- se python supporta i numeri negativi possiamo sommare sempre e ci togliamo il pensiero
        # perche se abbiamo venduto  12 XRP e ne avevamo 20, basta fare 20 + -12
