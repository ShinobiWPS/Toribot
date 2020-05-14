import json
from costanti.valori_percorso import VALORI_PERCORSO
import sys


def apriFileValori(nuovoJson={}):
    """serve per interagire col file `valori.json`

    Keyword Arguments:

        nuovoJson {dict} -- json aggiornato (default: {{}})

    Returns:

        rif, acq, data {list} -- rif, acq, data
        """
    with open(VALORI_PERCORSO, 'r+') as jsonFile:
        if type(nuovoJson) is dict:
            if (nuovoJson != {}):
                try:
                    json.dump(nuovoJson, jsonFile)
                except Exception:
                    sys.exit('impossibile aggiornare il file' + VALORI_PERCORSO)
            else:
                data = json.load(jsonFile)
                rif = data['riferimento']
                acq = data['acquisto']
                return [rif, acq, data]
        else:
            sys.exit('valore per il json non valida')
