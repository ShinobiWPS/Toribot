#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telepot
import pprint
import os
import time
import sys
# è la libreria che gestisce le kaybord del bot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from pprint import pprint  # printa il risultato del oggetto msg in modo ordinato
# gestisce la parte della ricezione di nuovi messaggi
from telepot.loop import MessageLoop



def telegram(azione, text):
    # ---------------------set del bot---------------------------------
    # percorso dove è inserito lo script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # print(BASE_DIR) printa il percorso dello script

    token = '1143795394:AAEYBmf6nBH0wt_9B9ANUmzPsYIMLvu1x7c'

    bot = telepot.Bot(token)
    chat_id = 102377514
    # dati=bot.getMe() #dati del bot
    cronologia = bot.getUpdates()

    # ________________riconoscimento se il testo corrisponde a un determinato valore______
    ric1 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Si, sono io', callback_data='sonoio')], [
            InlineKeyboardButton(text='No,non sono', callback_data='prova 2')], ])

    ric1 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='si', callback_data='si')], [
            InlineKeyboardButton(text='No', callback_data='no')], ])

    # tastiera=telepot.namedtuple

    # _____________________________invio messagio da bot____________

    def nuovo_mexbot(testo):
        # l'ultimo aromento, fà comparire la keyboard
        bot.sendMessage(chat_id, testo)

    # ______________________________quando arriva un nuovo messaggio da utente_______________________

    def new_mex(msg):  # questa funzione viene eseuita se arriva un nuovo messaggio

        # questa funzione restituisce il tipo di messagio, id di chi ha inviato il messaggio
        content_type, chat_type, chat_id = telepot.glance(msg)

        # ora settiamo una ktastiera keybord, con dei bottoni.
        # si possono creare varie keyboard in base al messaggio ricevuto
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='tasto 1', callback_data='prova 1')], [
                InlineKeyboardButton(text='tasto 2', callback_data='prova 2')],
        ])

        # riuarda al riconoscimento di testo
        if content_type == 'text':  # se il nuovo messaggio è un testo
            # prendi solo laromento testo di msg, e dividilo per parole
            cmd = msg['text'].split()

            # l'ultimo aromento, fà comparire la keyboard
            bot.sendMessage(chat_id, 'hai inviato un messaggio?',
                            reply_markup=keyboard)

            # li if che seguono sono se nel caso la prima parola del testo corrisponde
            if cmd[0] == '/start':
                print('viaaaa')
            elif cmd[0] == '/ciao':
                print('ciaoo')
            else:
                print(chat_id, "scusa, non ho capito'")
        print(cmd)
        sys.stdout.flush()

    # _________________________quando l'utente click su keyboard in chat________________

 # ---------------------click su keyboard in chat---------------------------------

    def new_query(msg):  # questa funzione viene eseuita se viene cliccato un tasto keyborad
        # nel ultimo argomenti specifichiamo che è un testo derivante da una tastiera keyboard
        query_id, from_id, query_data = telepot.glance(
            msg, flavor='callback_query')
        print('siiii')
        bot.answerCallbackQuery(query_id, text='yheeeaa')
        if query_data == 'press':
            bot.sendMessage(chat_id, 'puoi dormire')
        if azione == "mex":
            print("sto inviando un nuovo messagio")
            nuovo_mexbot(text)

    # _____________________________operazioni che effettua bot
    # il secondo argomento è la funzione che andiamo a chiamare, che esegue quando c'è un nuovo messagio
    MessageLoop(
        bot, {'chat': new_mex, 'callback_query': new_query}).run_as_thread()

    while 1:
        time.sleep(3)

