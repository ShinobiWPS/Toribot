import os
import logging
from pathlib import Path
from costanti.log_cartella_percorso import LOG_CARTELLA_PERCORSO


def inizializza_log():

	Path(LOG_CARTELLA_PERCORSO).mkdir(parents=True, exist_ok=True)
	
	# Main logger ___________________________________________
	logging.basicConfig(
		level=logging.INFO,
		filename=LOG_CARTELLA_PERCORSO+"/main.log",
		filemode="a+",
		format="%(asctime)s %(levelname)s %(message)s"
	)

	# Inizializzo log API ___________________________________
	log = logging.getLogger('werkzeug')
	# log.setLevel(logging.ALL)
	log.basicConfig(
		level=logging.INFO,
		filename=LOG_CARTELLA_PERCORSO+"/API_requests.log",
		filemode="a+",
		format="%(asctime)s %(levelname)s %(message)s"
	)

