import logging
from utilita.log import passa_output_al_log_file
from costanti.argomenti_per_il_bot import ARGOMENTI_PER_IL_BOT
import sys
from operazioni import seVendereOComprare, quandoVendere
import json
import websocket
import os
from costanti.dati_forgiati import DATI_FORGIATI_CARTELLA_PERCORSO
import csv

# ______________________________________roba che serve all'avvio____________________


def avvio(argv):
    print('Rock and Roll, baby!')
    ARGOMENTI_PER_IL_BOT = argv
    if len(ARGOMENTI_PER_IL_BOT) > 0:
        if ARGOMENTI_PER_IL_BOT[0] == 'log':
            passa_output_al_log_file()
    if os.environ.get('ISDEVELOPMENT') == 'true':
        dati_statici()
    else:
        dati_da_Bitstamp_websocket()


def processaNuovoPrezzo(attuale):
    print("questo è il prezzo atuale:")
    print(attuale)

    logging.info(attuale)
    seVendereOComprare(attuale)

    print("ho finito processa nuovo prezzo")


# _____________________________________elabora i dati inseriti da noi__________________-
def dati_statici():
    with open(f'{DATI_FORGIATI_CARTELLA_PERCORSO}/salita_discesa.csv') as csvFile:
        datiStatici = csv.reader(csvFile)
        for riga in datiStatici:
            processaNuovoPrezzo(float(riga[0]))


# ______________________________________parte con dati websoket______________________________________
def dati_da_Bitstamp_websocket():
    try:
        # questo mostra piu informazioni se True
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp("wss://ws.bitstamp.net",
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.on_open = on_open
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()


def on_open(ws):
    """Funzione all'aggancio del WebSocket

    Arguments:
                    ws {tipo_boh} -- sono dei caratteri apparentemente inutili
                                    """
    jsonString = json.dumps({
        "event": "bts:subscribe",
        "data": {
            "channel": "live_trades_xrpeur"
        }
    })
    # manda a bitstamp la richiesta di iscriversi al canale di eventi 'live_trades_xrpeur'
    ws.send(jsonString)
    print('Luce verde 🟢🟢🟢')


def on_message(ws, message: str):
    # la stringa message ha la stesso formato di un json quindi possiamo passarlo come tale per ottenere il Dict
    messageDict = json.loads(message)
    # PARE che appena si aggancia il socket manda un messaggio vuoto che fa crashare il bot
    if messageDict['data'] != {}:
        # questo print serve solo a noi per lavorare
        attuale = messageDict['data']['price']
        processaNuovoPrezzo(attuale)

    """
		esito = seComprareOVendere(datiDaMessage) -> {azione: compra, quantiXRP: 24} || {}
		if esito != {}
			compra(esito)
		"""


def on_error(ws, error: str):
    print(error)
    print('❌')


def on_close(ws):
    print("### WebSocketclosed 🔴🔴🔴 ###")


avvio(sys.argv[1:])
