import json
import logging
import os
import sys


def FileWrites( fname, mode, string ):
	try:
		with open( str( fname ).strip(), str( mode ).strip() ) as file:
			if bool( str( string ).strip() ):
				file.write( str( string ).strip() + "\n" )
			else:
				file.write( str( string ).strip() )
	except Exception as e:

		raise e


def FileReads( fname ):
	if os.path.isfile( str( fname ).strip() ):
		res = None
		try:
			with open( open( str( fname ).strip(), "r" ) ) as file:
				res = file.read().strip()
		except Exception as e:
			raise e
		finally:
			return res
	return None


def JsonWrites( fname, mode, json_object ):
	FileWrites(
		fname, mode, json.dumps( json_object, sort_keys=True, indent=4 )
	)


def JsonReads( fname ):
	return json.loads( FileReads( fname ) )


def JsonEdit( fname, chiave=None, valore=None ):
	try:
		with open( fname, 'r+' ) as jsonFile:
			if chiave is not None and valore is not None:
				try:
					valori_json = json.loads( jsonFile.read() )
					jsonFile.seek( 0 )
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
		raise e


def FileWrite( fname, string ):
	FileWrites( fname, "w+", string )


def FileAppend( fname, string ):
	FileWrites( fname, "a+", string )
