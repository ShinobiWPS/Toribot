import json
import logging
import os
import sys

from costanti.valori_percorso import VALORI_PERCORSO


def gestoreValoriJson( chiave=None, valore=None ):
	try:
		with open( VALORI_PERCORSO, 'r+' ) as jsonFile:
			if chiave is not None and valore is not None:
				try:
					valori_json = json.loads( jsonFile.read() )

					jsonFile.seek( 0 )

					if isinstance( chiave, list ):
						tmp_config = valori_json
						for key in chiave[ :-1 ]:
							if key in tmp_config:
								if not isinstance( tmp_config[ key ], dict ):
									del tmp_config[ key ]
									tmp_config[ key ] = {}
								tmp_config = tmp_config[ key ]
							else:
								tmp_config[ key ] = {}
								tmp_config = tmp_config[ key ]
						if isinstance( chiave,
							list ) or isinstance( chiave, dict ):
							tmp_config[ chiave[ -1 ] ] = valore
						else:
							valore = str( valore )
							if valore.lower() == "True".lower() or valore.lower(
							) == "False".lower():
								tmp_config[ chiave[ -1 ]
											] = True if valore.lower(
											) == "True".lower() else False
							elif valore.replace( '-', '', 1 ).isdigit(
							) and valore[ 1: ].find( '-' ) == -1:
								tmp_config[ chiave[ -1 ] ] = int( valore )
							elif valore.replace( '-',
								'', 1 ).replace( '.', '', 1 ).replace(
								',', '', 1
								).isdigit() and valore[ 1: ].find( '-' ) == -1:
								tmp_config[ chiave[ -1 ] ] = float( valore )
							else:
								tmp_config[ chiave[ -1 ] ] = valore

						if valore == "":
							del tmp_config[ chiave[ -1 ] ]

					else:
						valori_json[ chiave ] = valore

					jsonFile.write(
						json.dumps( valori_json, sort_keys=True, indent=4 )
					)
					jsonFile.truncate()

					return valori_json
				except Exception as e:
					logging.error( e )
			else:
				return json.loads( jsonFile.read() )
	except Exception as e:
		logging.error( e )


def portafoglio( chiave=None, valore=None ):
	valori_json = gestoreValoriJson( chiave, valore )
	if valori_json and "cripto" in valori_json and "soldi" in valori_json:
		return [ valori_json[ "cripto" ], valori_json[ "soldi" ] ]
	return [ None, None ]


def commercialista( chiave=None, valore=None ):
	valori_json = gestoreValoriJson( chiave, valore )
	if valori_json and "ultimo_valore" in valori_json and "orders" in valori_json:
		return [ valori_json[ "ultimo_valore" ], valori_json[ "orders" ] ]
	return [ None, None ]


# def ultimo_id_ordine(valore=None):
# valori_json = gestoreValoriJson("ultimo_id", valore)
# if valori_json and "ultimo_id" in valori_json:
# return valori_json["ultimo_id"]
# return None
