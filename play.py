import json
import websocket


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
    except KeyboardInterrupt as identifier:
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
    ws.send(jsonString)
    print('Luce verde')
    #thread.start_new_thread(run, ())


def on_message(ws, message: str):
    messageDict = json.loads(message)
    if messageDict['data'] != {}:
        attuale = messageDict['data']['price']
        print(attuale)
    """
		esito = seComprareOVendere(datiDaMessage) -> {azione: compra, quantiXRP: 24} || {}
        	if esito != {}
                compra(esito)
        """


def on_error(ws, error: str):
    print(error)


def on_close(ws):
    print("### WebSocketclosed ###")


def seComprareOVendere(parameter_list):
    pass


def compra(parameter_list):
    pass


def vendi(parameter_list):
    pass


avvio()
