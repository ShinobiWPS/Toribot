import logging

from utilita.apriFile import commercialista, portafoglio

primo_acquisto = True
# Se Fattore d'approssimazione a 8 Strategia B, se inferiore di 8 strategia B+An
BR_Fattore_Approssimazionoe = 8
BR_Fattore_Perdita = 100

def gestore(valore_attuale):
	global primo_acquisto, BR_Fattore_Approssimazionoe
	cripto, soldi = portafoglio()

	#_______INIZIO STRATEGIA_____________________________________

	#_____________________ Comprare _____________________________
	# Se ho soldi
	if soldi:
		ultimo_valore, valore_acquisto = commercialista()

		# Se il valore attuale è maggiore dell'ultimo valore
		#todo-fai round all inizio e basta,rimuovi i round sparsi
		if round(
		    valore_attuale,
		    BR_Fattore_Approssimazionoe) < ultimo_valore or primo_acquisto:
			primo_acquisto = False
			# Compro
			compro(soldi, valore_attuale)
	#_____________________ Vendere _____________________________
	# Se ho criptomonete
	elif cripto:
		ultimo_valore, valore_acquisto = commercialista()

		# Se il valore attuale è maggiore dal valore d'acquisto (in caso opposto perderei i soldi)
		if BR_Fattore_Perdita < 0 or valore_acquisto - round(valore_attuale,BR_Fattore_Approssimazionoe) <= BR_Fattore_Perdita:
			# Se il valore attuale è minore dell'ultimo valore, sta scendendo (forse)
			if round(valore_attuale,
			         BR_Fattore_Approssimazionoe) > ultimo_valore:
				# Vendo
				vendo(cripto, valore_attuale)
	#_______FINE STRATEGIA_____________________________________



	# Aggiorno l'ultimo valore
	commercialista("ultimo_valore", valore_attuale)



def compro(soldi, valore_attuale):
	logging.info("Acquisto [" + str(valore_attuale) + "] " +
	             str(soldi) + " -> " +
	             str(round(soldi / valore_attuale, 8)))
	commercialista("valore_acquisto", valore_attuale)
	portafoglio("cripto", round(soldi / valore_attuale, 8))
	portafoglio("soldi", 0)
	
def vendo(cripto, valore_attuale):
	# Resetto il valore d'acquisto, dato che non ho più roba
	commercialista("valore_acquisto", 0)
	logging.info("Vendita [" + str(valore_attuale) + "] " +
	             str(cripto) + " -> " +
	             str(round(cripto * valore_attuale, 8)))
	portafoglio("soldi", round(cripto * valore_attuale, 5))
	portafoglio("cripto", 0)
