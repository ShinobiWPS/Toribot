
import json
import sys

from costanti.portafoglio_percorso import PORTAFOGLIO_PERCORSO


def apriFileportafoglio(nuovoJson={}):
    """serve per interagire col file `valori.json`

    Keyword Arguments:

        nuovoJson {dict} -- json aggiornato (default: {{}})

    Returns:

        xrp, eur, data {list} -- Ripple, Euro, dizionario del json
    """
    with open(PORTAFOGLIO_PERCORSO, 'r+', encoding='utf-8') as jsonFile:
        if type(nuovoJson) is dict:
            if (nuovoJson != {}):
                try:
                    json.dump(nuovoJson, jsonFile, sort_keys=True, indent=4)
                except Exception:
                    sys.exit('impossibile aggiornare il file' +
                             PORTAFOGLIO_PERCORSO)
            else:
                data = json.load(jsonFile)
                xrp = data['xrp']
                eur = data['eur']
                return [xrp, eur, data]
        else:
            sys.exit('valore per il json non valida')
