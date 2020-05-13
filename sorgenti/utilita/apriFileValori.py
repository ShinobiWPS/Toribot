
import json
from costanti.valori_percorso import VALORI_PERCORSO


def apriFileValori(modalita, nuovoJson={}):
    """Se passi modalita R ottieni una lista,Se passi una W devi passare anche un JSON,ottinie l esito dell operazione

        Arguments:

                modalita {str} -- [description]

        Keyword Arguments:

                nuovoJson {dict} -- [description] (default: {{}})

        Returns:

                DICT -- in modalita 'r' restituisce un dict con i valori

                BOOL -- e riuscito a scrivere o no?

            """
    with open(VALORI_PERCORSO, modalita) as jsonFile:
        if (modalita != 'r') and (modalita != 'w'):
            raise ValueError('valore di apertura file non valida')

        if modalita == 'r':
            data = json.load(jsonFile)
            rif = data['riferimento']
            acq = data['acquisto']
            return [rif, acq]
        else:  # sara una 'w'
            # potresti passare R ma con un nuovoJson vuoto, il che svuoterebbe il nostro json,
            # per prevenirlo, controllo se nuovoJson e' vuoto,
            # se si, gli passo i stessi dati originali del json
            # altrimenti , beh e' corretto e lo passo
            try:
                json.dump(data if nuovoJson == {} else nuovoJson, jsonFile)
                return True
            except Exception:
                return False
