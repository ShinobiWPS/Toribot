#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from pprint import pprint

import requests
import telepot
# gestisce la parte della ricezione di nuovi messaggi
from telepot.loop import MessageLoop

# è la libreria che gestisce le kaybord del tg_bot
# from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup


class TelegramBot():

	Admins_ID = [ '42219043', '33223598']
	Current_Admin_ID = 0

	toribot_API_Domain = "127.0.0.1"
	toribot_API_Port = 5000
	toribot_API_Token = ""
	toribot_API_URL = "http://" + toribot_API_Domain + ":" + str(toribot_API_Port) + "/"

	token = "1143795394:AAEYBmf6nBH0wt_9B9ANUmzPsYIMLvu1x7c"
	tg_bot = None

	_offset = 0

	def __init__(self, isLoop=False):

		self.tg_bot = telepot.Bot(self.token)
		if isLoop:
			MessageLoop(
				self.tg_bot, {
				'chat': self.messageHandler,
				'callback_query': self.callbackHandler
				}
			).run_as_thread()

	def __del__(self):
		self.tg_bot = None

	def test(self):
		pprint(self.tg_bot.getMe())

	def getUpdate(self):
		update = self.tg_bot.getUpdates(offset=self._offset + 1)
		if update:
			self._offset = int(update[-1]['update_id'])
			pprint(update)

	def messageHandler(self, message):
		content_type, chat_type, chat_id = telepot.glance(message)
		if content_type == 'text':
			if 'entities' in message and message['entities']:
				command = (
					message[content_type][int(message['entities'][0]['offset']) +
					1:int(message['entities'][0]['offset']) + int(message['entities'][0]['length'])]
				)
				if command == "start":
					self.sendMessage(chat_id, str(chat_id))
				if command == "stop":
					self.sendMessage(chat_id, "Bye bye.")
				if command == "balance" or command == "bilancio":
					try:
						r = self.getToribotAPI("bilancio")
						if r and r.status_code == 200 and r.text:
							self.sendMessage(chat_id, str(r.text))
					except requests.exceptions.ConnectionError as ex:
						print(ex)
						self.sendMessage(chat_id, "Error, ToriBot API Error" + str(ex))
					except Exception as ex:
						print(ex)
						self.sendMessage(chat_id, "Error, retrieving balance" + str(ex))

				if command == "force_balance" or command == "forza_bilancio":
					try:
						r = self.getToribotAPI("forza_bilancio")
						if r and r.status_code == 200 and r.text:
							self.sendMessage(chat_id, str(r.text))
					except requests.exceptions.ConnectionError as ex:
						print(ex)
						self.sendMessage(chat_id, "Error, ToriBot API Error" + str(ex))
					except Exception as ex:
						print(ex)
						self.sendMessage(chat_id, "Error, retrieving balance" + str(ex))

				if command == "estimate" or command == "stima":
					try:
						r = self.getToribotAPI("bilancio_stimato")
						if r and r.status_code == 200 and r.text:
							self.sendMessage(chat_id, str(r.text))
					except requests.exceptions.ConnectionError as ex:
						print(ex)
						self.sendMessage(chat_id, "Error, ToriBot API Error" + str(ex))
					except Exception as ex:
						print(ex)
						self.sendMessage(chat_id, "Error, retrieving balance" + str(ex))

				if command == "status" or command == "stato":
					try:
						r = self.getToribotAPI("status")
						if r and r.status_code == 200 and r.text:
							self.sendMessage(
								chat_id,
								str("Running" if r.text.lower() == "true" else "NOT running")
							)
							# self.sendMessage(chat_id, str(r.text))
					except requests.exceptions.ConnectionError as ex:
						print(ex)
						self.sendMessage(chat_id, "Error, ToriBot API Error" + str(ex))
					except Exception as ex:
						print(ex)
						self.sendMessage(chat_id, "Error, retrieving status" + str(ex))

				if command == "stop_toribot":
					try:
						r = self.getToribotAPI("stop")
						if r and r.status_code == 200 and r.text:
							self.sendMessage(chat_id, str(r.text))
					except requests.exceptions.ConnectionError as ex:
						print(ex)
						self.sendMessage(chat_id, "Error, ToriBot API Error" + str(ex))
					except Exception as ex:
						print(ex)
						self.sendMessage(chat_id, "Error executing" + str(ex))

				if command == "start_toribot":
					try:
						r = self.getToribotAPI("start")
						if r and r.status_code == 200 and r.text:
							self.sendMessage(chat_id, str(r.text))
					except requests.exceptions.ConnectionError as ex:
						print(ex)
						self.sendMessage(chat_id, "Error, ToriBot API Error" + str(ex))
					except Exception as ex:
						print(ex)
						self.sendMessage(chat_id, "Error executing" + str(ex))

				if command == "shutdown" or command == "spegni":
					try:
						r = self.getToribotAPI("shutdown")
						if r and r.status_code == 200 and r.text:
							self.sendMessage(chat_id, str(r.text))
					except requests.exceptions.ConnectionError as ex:
						print(ex)
						self.sendMessage(chat_id, "Error, ToriBot API Error" + str(ex))
					except Exception as ex:
						print(ex)
						self.sendMessage(chat_id, "Error executing" + str(ex))

			else:
				self.sendMessage(chat_id, str(message[content_type]))

	def callbackHandler(self, message):
		content_type, chat_type, chat_id = telepot.glance(message)
		# self.sendMessage(chat_id, str(message[content_type]))

	def sendMessage(self, telegram_id, message):
		if isinstance(telegram_id, list):
			for tid in telegram_id:
				self.tg_bot.sendMessage(tid, message)
		else:
			self.tg_bot.sendMessage(telegram_id, message)

	def getToribotAPI(self, endpoint):
		return requests.get(
			self.toribot_API_URL + endpoint + "?&token=" + self.toribot_API_Token + ""
		)


if __name__ == "__main__":

	try:

		mytg_bot = TelegramBot()
		while 1:
			time.sleep(2)

	except KeyboardInterrupt as ex:
		pass

	except Exception as ex:
		print(ex)

	finally:
		print("Telegram bot closed.")
