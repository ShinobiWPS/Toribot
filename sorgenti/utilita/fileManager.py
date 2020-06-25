import json
import logging
import os


def FileWrites(filename, mode, string):
	try:
		with open(str(filename).strip(), str(mode).strip()) as file:
			if bool(str(string).strip()):
				file.write(str(string).strip() + "\n")
			else:
				file.write(str(string).strip())
	except Exception as e:

		raise e


def FileReads(filename):
	if os.path.isfile(str(filename).strip()):
		res = None
		try:
			with open(str(filename).strip(), "r") as file:
				res = file.read().strip()
		except Exception as e:
			raise e
		finally:
			return res
	return None


def JsonWrites(filename, mode, json_object):
	FileWrites(filename, mode, json.dumps(json_object, sort_keys=True, indent=4))


def JsonReads(filename):
	return json.loads(FileReads(filename))


def JsonEdit(filename, chiave=None, valore=None):
	try:
		with open(filename, 'r+') as jsonFile:
			if chiave is not None and valore is not None:
				try:
					valori_json = json.loads(jsonFile.read())
					jsonFile.seek(0)
					valori_json[chiave] = valore
					jsonFile.write(json.dumps(valori_json, sort_keys=True, indent=4))
					jsonFile.truncate()
					return valori_json
				except Exception as e:
					logging.error(e)
			else:
				return json.loads(jsonFile.read())
	except Exception as e:
		raise e


def FileWrite(filename, string):
	FileWrites(filename, "w+", string)


def FileAppend(filename, string):
	FileWrites(filename, "a+", string)
