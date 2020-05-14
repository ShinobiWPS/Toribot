import json
from costanti.valori_percorso import VALORI_PERCORSO
from costanti.portafoglio_percorso import PORTAFOGLIO_PERCORSO
from utilita.apriFileValori import apriFileValori
from utilita.apriFilePortafoglio import apriFilePortafoglio


def seVendereOComprare(attuale: int):
    """Puoi vendere o comprare?

        Arguments:

                attuale {int} -- nuovo prezzo del ripple
            """
    # ATTUALE: valoro che assume la vaiabile all'evento
    # RIFERIMENTO: valore assunto al precedente evento
    # ACQUISTO: valore di acquisto

    # todo- dato un numero gia esistente di quantita nel portafoglio
    # bisogna sottrarre quando vendiamo XRP e sommare quando compriamo, viceversa per gli EUR
    # suggerimento- se python supporta i numeri negativi possiamo sommare sempre e ci togliamo il pensiero
    # perche se abbiamo venduto  12 XRP e ne avevamo 20, basta fare 20 + -12

    print("sono entrato nel compra e vendi")
    xrp, eur, data = apriFilePortafoglio()
    print('xrp')
    print(xrp)

    if eur > 0:
        quandoComprare(attuale)
    elif xrp > 0:
        quandoVendere(attuale)


def quandoVendere(attuale):
    rif, acq, data = apriFileValori()
    print('questo è il valore di riferimento e acquisto')
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
    data["riferimento"] = attuale
    apriFileValori(data)


def quandoComprare(attuale):
    print("ora decido quando comprare")
    # trasformo il valore attuale in valore d'a
    rif, acq, data = apriFileValori()

    rif = data['riferimento']
    print('questo è il valore di riferimento')
    print(rif)

    # todo-ora stabiliamo se sta scendendo o salendo
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
        apriFileValori(data)


def compra(parameter_list):
    print("ho aquistato a questo prezzo"+parameter_list)


def vendi(parameter_list):
    pass


def calcologuad(valVend):
    # bisognerà azzerare i ripple, e calcolare i soldi guadagnati
    # valvend saà il valore a cui sono stai venduti i ripple
    # bisogna scrivere sul json con quanti soldi si hanno
    xrp, eur, data = apriFilePortafoglio()

    # sul json ci saranno quanti ripple sono stai acquistati l'ultima volta
    xpr = data['xpr']
    # calcoliamo quanto abbiamo guadagnato dalla vendita
    eur = xpr*valVend

    # attenzione------ bisogna ricaricare i soldi guadagnati sul file json


def calcolocompr(valcompr):
    pass
    # valcompr saà il valore a cui sono stai acquistati i ripple
    # bisogna scrivere sul json con quanti ripple sono stati acquistati
    # bisognerà azzerare i soldi e impostare i ripple che si hanno
