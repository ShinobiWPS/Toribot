import json
from costanti.valori_percorso import VALORI_PERCORSO
from costanti.portafoglio_percorso import PORTAFOGLIO_PERCORSO


def seVendereOComprare(attuale: int):
    """Puoi vendere o comprare?

        Arguments:
                attuale {int} -- nuovo prezzo del ripple
        """
    with open(PORTAFOGLIO_PERCORSO, "r") as jsonFile:
        data = json.load(jsonFile)
        eur = data['xrp']
        xrp = data['eur']

    if eur > 0:
        quandoComprare(attuale)
    elif xrp > 0:
        quandoVendere(attuale)


def quandoVendere(attuale):
    # ATTUALE: valoro che assume la vaiabile all'evento
    # RIFERIMENTO: valore assunto al precedente evento
    # ACQUISTO: valore di acquisto
    print("sono entrato nel compra e vendi")

    # carico i valori dal json
    # valori = json.load(open(VALORI_PERCORSO))
    with open(VALORI_PERCORSO, "r") as jsonFile:
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
            print("HO VENDUTO")

            calcologuad(attuale)
            # bisognerà valutare il minimo di crescita
            quandoComprare(attuale)

    else:
        print("valore minore dell'acquisto")

    # aggiorno dati json(non so come aggirnare solo un dato, l'acquesto non è necessario)
    # ATTENZIONEEEEEEEE-------------------------------non mi aggirna il file json----
    data["riferimento"] = attuale
    with open(VALORI_PERCORSO, "w") as outfile:
        json.dump(data, outfile)


def quandoComprare(attuale):
    print("ora decido quando comprare")
    # trasformo il valore attuale in valore d'a
    with open(VALORI_PERCORSO, "r") as jsonFile:
        data = json.load(jsonFile)

    rif = data['riferimento']
    print('questo è il valore di riferimento')
    print(rif)

    # ora stabiliamo se sta scendendo o salendo
    # se sale aspettiamo che scenda
    # se scende, comriamo quando ricomincia a salire

    if attuale > rif:
        # in questo casa sinifica che sta salendo. e non faccio nulla
        print("aspetto a comprare perchè sta salendo")

    # ----------------------ATTENZIONEEEEE lo so che ci vorrebbe un elsif. lo metterò
    if attuale < rif:
        # significa che sta scendendo aspettiamo che arrviamo al minimo

        # devo mettere qualcosa che controlli quando smette di essere inferiore ad attuale

        # imposto il nuovo valore d'acquisto
        data["acquisto"] = attuale
        with open(VALORI_PERCORSO, "w") as outfile:
            json.dump(data, outfile)


def compra(parameter_list):
    print("ho aquistato a questo prezzo"+parameter_list)


def vendi(parameter_list):
    pass


def aggiornaPortafoglio(xrp, eur):
    """Scrivi su file o in variabili i cambiamenti di XRP e EUR

    Arguments:
                    xrp {int} -- il valore da sommare di XRP
                    eur {int} -- il valore da sommare di EUR
    """
    with open(PORTAFOGLIO_PERCORSO, 'w') as file:
        portafoglioLetto = file.read()
        portafoglioDict = json.loads(portafoglioLetto)
        # accedi alle chiavi ad esempio con:
        # portafoglioDict['xrp']

        # todo- dato un numero gia esistente di quantita nel portafolgio
        # bisogna sottrarre quando vendiamo XRP e sommare quando compriamo, viceversa per gli EUR
        # suggerimento- se python supporta i numeri negativi possiamo sommare sempre e ci togliamo il pensiero
        # perche se abbiamo venduto  12 XRP e ne avevamo 20, basta fare 20 + -12


def calcologuad(valVend):
    pass
    # bisognerà azzerare i ripple, e calcolare i soldi guadagnati
    # valvend saà il valore a cui sono stai venduti i ripple
    # bisogna scrivere sul json con quanti soldi si hanno
    with open("portafolio.json", "r") as jsonFile:
        data = json.load(jsonFile)

    # sul json ci saranno quanti ripple sono stai acquistati l'ultima volta
    xpr = data['xpr']
    # calcoliamo quanto abbiamo guadagnato dalla vendita
    eur = xpr*valVend

    # ANTENZIONEEEE------ bisogna ricareicare i soldi guadagnati sul file json


def calcolocompr(valcompr):
    pass
    # valcompr saà il valore a cui sono stai acquistati i ripple
    # bisogna scrivere sul json con quanti ripple sono stati acquistati
    # bisognerà azzerare i soldi e impostare i ripple che si hanno
