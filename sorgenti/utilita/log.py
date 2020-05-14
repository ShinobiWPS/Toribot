from costanti.log_cartella_percorso import LOG_CARTELLA_PERCORSO
import logging


def passa_output_al_log_file():
    logging.basicConfig(level=logging.INFO,
                        filename="log/logfile.log",
                        filemode="w+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
