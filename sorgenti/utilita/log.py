from costanti.log_cartella_percorso import LOG_CARTELLA_PERCORSO
import logging


def passa_output_al_log_file():
    logging.basicConfig(level=logging.INFO,
                        filename="log/logfile.log",
                        filemode="w+",
<<<<<<< HEAD
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
=======
                        format="%(asctime)s %(levelname)s %(message)s")
>>>>>>> 3d671195135050a7b4389d5c4683c3557bceb67d
