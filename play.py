import requests
import time


def getdata() -> int:
    """Ottieni valore di Ripple da Bitstamp

        Returns:
                int -- valore di Ripple
        """
    r = requests.get('https://www.bitstamp.net/api/v2/ticker_hour/xrpeur/')
    if r.status_code == 200:
        jsonObj = r.json()
        print(jsonObj)
        return jsonObj['last']
    else:
        # todo- cosa fare se la URL da errore per qualche motivo?
        print('no..')


def seComprare(parameter_list) -> bool:
    pass


def compra(parameter_list):
    pass


def avvio():
    while True:
        attuale = getdata()
        time.sleep(1)
        print(attuale)
        """ print('valore {attuale} il {time.localtime()}') """


avvio()
