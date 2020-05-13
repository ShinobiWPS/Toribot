
import json
from costanti.valori_percorso import VALORI_PERCORSO


def apriFileValori(modalita, nuovo_json={}):
    """Se passi modalita R ottieni una lista,Se passi una W devi passare anche un JSON,ottinie l esito dell operazione

        Arguments:

                modalita STR -- [description]

        Keyword Arguments:

                nuovo_json DICT -- [description] (default: {{}})

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
            # potresti passare R ma con un nuovo_json vuoto, il che svuoterebbe il nostro json,
            # per prevenirlo, controllo se nuovo_json e' vuoto,
            # se si, gli passo i stessi dati originali del json
            # altrimenti , beh e' corretto e lo passo
            try:
                json.dump(data if nuovo_json == {} else nuovo_json, jsonFile)
                return True
            except Exception:
                return False
