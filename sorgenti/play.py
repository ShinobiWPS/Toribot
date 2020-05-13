import json
import websocket
# il file .env con il vscode workspace.json sono necessari solo temporaneamente per ovviare al bug di intelliCode (a volte mostra import irrisolti, ma sono falsi negativi) perche usa una preview di Microsoft Python Language Analisys, come per esempio e' successo per importare "operazioni"
from operazioni import quandoVendere


def avvio():
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
    print('Luce verde')


def on_message(ws, message: str):
    # la stringa message ha la stesso formato di un json quindi possiamo passarlo come tale per ottenere il Dict
    messageDict = json.loads(message)
    # PARE che appena si aggancia il socket manda un messaggio vuoto che fa crashare il bot
    if messageDict['data'] != {}:
        # questo print serve solo a noi per lavorare
        attuale = messageDict['data']['price']
        print(attuale)
        quandoVendere(attuale)
        print("sono passato oltre")

    """
		esito = seComprareOVendere(datiDaMessage) -> {azione: compra, quantiXRP: 24} || {}
        	if esito != {}
                compra(esito)
        """


def on_error(ws, error: str):
    print(error)


def on_close(ws):
    print("### WebSocketclosed ###")


avvio()
