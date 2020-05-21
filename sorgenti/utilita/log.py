import logging

from costanti.log_cartella_percorso import LOG_CARTELLA_PERCORSO


def passa_output_al_log_file():
	logging.basicConfig(level=logging.INFO,
	                    filename="log/logfile.log",
	                    filemode="w+",
	                    format="%(asctime)s %(levelname)s %(message)s")
