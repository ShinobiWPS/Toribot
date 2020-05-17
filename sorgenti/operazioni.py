import json
from costanti.valori_percorso import VALORI_PERCORSO
from costanti.portafoglio_percorso import PORTAFOGLIO_PERCORSO
from utilita.apriFileValori import apriFileValori
from utilita.apriFilePortafoglio import apriFilePortafoglio
import logging

# ATTUALE: valoro che assume la variabile all'evento
# RIFERIMENTO: valore assunto al precedente evento
# ACQUISTO: valore di acquisto


def seVendereOComprare(attuale: int):
	"""Puoi vendere o comprare?

	Arguments:

		attuale {int} - - nuovo prezzo del ripple
                    """

	# todo- dato un numero gia esistente di quantita nel portafoglio
	# bisogna sottrarre quando vendiamo XRP e sommare quando compriamo, viceversa per gli EUR
	# suggerimento- se python supporta i numeri negativi possiamo sommare sempre e ci togliamo il pensiero
	# perche se abbiamo venduto  12 XRP e ne avevamo 20, basta fare 20 + -12

	print("devo vendere o comprare?")
	xrp, eur, data = apriFilePortafoglio()
	print("questi sono i ripple che abbiamo")
	print(xrp)
	print("questi sono gli euro che abbiamo")
	print(eur)

	# domandaaaaaaaaaaaaaaaaaaaaaaaaaa
	if eur > 0:
		print("devo comprare...")
		quandoComprare(attuale)
	elif xrp > 0:
		print("devo vendere...")
		quandoVendere(attuale)


# _________________________________________________VENDITA______________________________________________________
def quandoVendere(attuale):

	rif, acq, data = apriFileValori()
	print("sto valutando quando vendere")

	# il valore attuale è magiore di quello di acquisto?
	if attuale > acq:
		# se il valore attuale è maggiore dell'acquisto vuol dire sta salendo
		print("attuale > acquisto")

		# ora valutiamo se scende o sale
		if attuale > rif:
			# in questo caso sta salendo

			print("aspetto a vendere....sta crescendo....")
			# nel caso in cui il valore è più alto a quello di acquisto. ma più piccolo dell'ultimo valore registrato.
			# significa che ha iniziato a scendere
			# todo- scrivi rif sul file\
			data['riferimento'] = attuale
			apriFileValori(data)

		else:
			# nel momento che si verifichino due situazioni, allora vendo
			# 1° che si abbia un valore più alto dell'aquisto----->quindi indica una crescita(anche se minima)
			# 2° che si abbia un cambiamento di andamento. cioè una discesa.

			# ora calcolo la tranazione, e passo all'acquisto
			calcolo_vendita(attuale)
			logging.info("HO VENDUTO")
			print("HO VENDUTO")

	else:
		# in questo caso sinifica che siamo a un valore sotto all'acquisto
		print("valore minore dell'acquisto")


# _________________________________________COMPRO_____________________________________________________

# per decidere quando comprare, diamo per certo che stiamo scendendo. visto che vendiamo quando incomincia a scendere


def quandoComprare(attuale):
	# ora dobbiamo decidere quando comprare
	print("ora decido quando comprare.....")
	rif, acq, data = apriFileValori()
	# consideriamo che se abbiamo venduto, siamo già in fase di discesa
	if attuale > rif:
		# in questo casa sinifica che sta salendo. è l'ora di acquistare
		logging.info("HO ACQUISTATO")
		print("HO ACQUISTATO")

		data["acquisto"] = attuale
		apriFileValori(data)

	# calcoliamo quanti ripple abbiamo acquistato. e passiamo alla funzione vendere
	calcolo_acquisto(attuale)


def compra(parameter_list):
	# todo-API per comprare N XRP
	pass


def vendi(xrp):
	# todo-API per vendere N XRP
	pass


def calcolo_vendita(attuale):
	# questo calcolo avviene quando vendo i ripple

	# apro il json con i ripple che si avevano all'ultimo acquisto
	xrp, eur, data = apriFilePortafoglio()

	# calcoliamo quanto abbiamo guadagnato dalla vendita
	# azzeriamo i ripple
	eur = xrp * attuale

	data["eur"] = eur
	data["xrp"] = 0
	apriFilePortafoglio(data)


def calcolo_acquisto(attuale):
	# questo calcolo avviene quando compro i ripple

	# apro il json con i soldi che avevo
	xrp, eur, data = apriFilePortafoglio()

	# calcoliamo quanti ripple abbiamo acquistato
	# azzeriamo gli euro
	xrp = eur * attuale

	data["xrp"] = xrp
	data["eur"] = 0
	apriFilePortafoglio(data)
