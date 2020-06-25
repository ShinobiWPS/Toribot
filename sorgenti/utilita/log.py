import logging
from pathlib import Path

from costanti.costanti_unico import LOG_CARTELLA_PERCORSO


def inizializza_log():

	Path(LOG_CARTELLA_PERCORSO).mkdir(parents=True, exist_ok=True)

	# Main logger ___________________________________________
	logging.basicConfig(
		level=logging.DEBUG,
		filename=LOG_CARTELLA_PERCORSO + "/main.log",
		filemode="a+",
		format="%(asctime)s %(levelname)s %(message)s"
	)

	# Inizializzo log API ___________________________________
	logger = logging.getLogger('werkzeug')
	logger.setLevel(logging.DEBUG)
	# logger.basicConfig(
	# 	level=logging.INFO,
	# 	filename=LOG_CARTELLA_PERCORSO+"/API_requests.log",
	# 	filemode="a+",
	# 	format="%(asctime)s %(levelname)s %(message)s"
	# )
