import json


def seComprareOVendere(attuale):
    # ATTUALE: valoro che assume la vaiabile all'evento
    # RIFERIMENTO: valore assunto al precedente evento
    # ACQUISTO: valore di acquisto

    print("sono entrato nel compra e vendi")

    # carico i valori dal json
    #valori = json.load(open("valori.json"))

    with open("valori.json", "r") as jsonFile:
        data = json.load(jsonFile)

    rif = data['riferimento']
    acq = data['acquisto']
    print('questo è il valore di riferimento e acqusto')
    print(rif)
    print(acq)

    if attuale > acq:
        print("valore maggiore dell'acquisto")
        if attuale-rif > 0:
            print("sta crescendo")
        else:
            print("sta scendendo")

    else:
        print("valore minore dell'acquisto")

    # aggiorno dati json(non so come aggirnare solo un dato, l'acquesto non è necessario)
    data["riferimento"] = attuale
    with open("valori.json", "w") as outfile:
        json.dump(data, outfile)


def compra(parameter_list):
    pass
    print("ho aquistato a questo prezzo"+parameter_list)


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
