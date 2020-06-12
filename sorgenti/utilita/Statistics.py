import json
import logging
import os
import sys
import time

from costanti.costanti_unico import STATISTICA_PERCORSO
from utilita.infoAboutError import getErrorInfo


class Statistics(object):
	def __init__(self):
		self.strategy = None
		if os.path.exists(STATISTICA_PERCORSO):
			with open(str(STATISTICA_PERCORSO).strip(), "r") as file:
				content = file.read().strip()
				if content:
					self.strategy = json.loads(content)
				if self.strategy:
					self.strategy["cycle"]["start"] = None
					self.strategy["cycle"]["stop"] = None
					self.strategy['WST']["last"] = None
					self.strategy['WSOB']["last"] = None

		if not self.strategy:
			self.strategy = {
				'soldi': {
				'init': {},
				'gain': {}
				},
				'WST': {
				'duration': {}
				},
				'WSOB': {
				'duration': {}
				},
				'cycle': {
				'duration': {}
				},
				'trade': {
				'duration': {}
				},
				'buy': {
				'duration': {}
				},
				'sell': {
				'duration': {}
				},
				'spread': {}
			}

			self.strategy['soldi']["init"]['soldi'] = 0
			self.strategy['soldi']["init"]['timestamp'] = 0
			self.strategy['soldi']["current"] = 0
			self.strategy['soldi']["gain"]["soldi"] = None
			self.strategy['soldi']["gain"]["percentage"] = None
			self.strategy['soldi']["gain"]["h"] = None

			self.strategy['WST']["last"] = None
			self.strategy['WST']["duration"]["avg"] = None
			self.strategy['WST']["duration"]["min"] = None
			self.strategy['WST']["duration"]["max"] = None
			self.strategy['WST']["duration"]["last"] = None

			self.strategy['WSOB']["last"] = None
			self.strategy['WSOB']["duration"]["avg"] = None
			self.strategy['WSOB']["duration"]["min"] = None
			self.strategy['WSOB']["duration"]["max"] = None
			self.strategy['WSOB']["duration"]["last"] = None

			self.strategy["cycle"]["start"] = None
			self.strategy["cycle"]["stop"] = None
			self.strategy["cycle"]["duration"]["avg"] = None
			self.strategy["cycle"]["duration"]["min"] = None
			self.strategy["cycle"]["duration"]["max"] = None
			self.strategy['cycle']["duration"]["last"] = None

			self.strategy["trade"]["last"] = None
			self.strategy["trade"]["duration"]["avg"] = None
			self.strategy["trade"]["duration"]["min"] = None
			self.strategy["trade"]["duration"]["max"] = None
			self.strategy['trade']["duration"]["last"] = None

			self.strategy["buy"]["last"] = None
			self.strategy["buy"]["duration"]["avg"] = None
			self.strategy["buy"]["duration"]["min"] = None
			self.strategy["buy"]["duration"]["max"] = None
			self.strategy['buy']["duration"]["last"] = None

			self.strategy["sell"]["last"] = None
			self.strategy["sell"]["duration"]["avg"] = None
			self.strategy["sell"]["duration"]["min"] = None
			self.strategy["sell"]["duration"]["max"] = None
			self.strategy['sell']["duration"]["last"] = None

			self.strategy["spread"]["last"] = None
			self.strategy["spread"]["avg"] = None
			self.strategy["spread"]["min"] = None
			self.strategy["spread"]["max"] = None

	def __del__(self):
		pass

	def strategy_soldi_update(self, soldi):

		try:
			soldi = float(soldi)

			if self.strategy["soldi"]["init"]['soldi']:

				self.strategy["soldi"]["gain"]['soldi'
												] = soldi - self.strategy["soldi"]["init"]['soldi']
				self.strategy["soldi"]["gain"]['percentage'] = (
					soldi - self.strategy["soldi"]["init"]['soldi']
				) / self.strategy["soldi"]["init"]['soldi'] * 100

				if self.strategy["soldi"]["init"]['timestamp']:
					self.strategy["soldi"]["gain"]['h'] = (
						soldi - self.strategy["soldi"]["init"]['soldi']
					) / ((time.time() - self.strategy["soldi"]["init"]['timestamp']) / 3600)

			self.strategy["soldi"]["current"] = soldi

			self.update_json()

		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			exc_type, unused_exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(ex, exc_type, fname, exc_tb.tb_lineno)
			logging.error(ex)

	def WST_update(self, WST_timestamp=None):

		try:
			current_duration = None

			if not WST_timestamp:
				WST_timestamp = float(time.time())

			if self.strategy["WST"]["last"]:
				current_duration = WST_timestamp - self.strategy["WST"]["last"]

			if current_duration:

				if self.strategy["WST"]["duration"]["max"]:
					if current_duration > self.strategy["WST"]["duration"]["max"]:
						self.strategy["WST"]["duration"]["max"] = current_duration
				else:
					self.strategy["WST"]["duration"]["max"] = current_duration

				if self.strategy["WST"]["duration"]["min"]:
					if current_duration < self.strategy["WST"]["duration"]["min"]:
						self.strategy["WST"]["duration"]["min"] = current_duration
				else:
					self.strategy["WST"]["duration"]["min"] = current_duration

				if self.strategy["WST"]["duration"]["avg"]:
					self.strategy["WST"]["duration"][
						"avg"] = (self.strategy["WST"]["duration"]["avg"] + current_duration) / 2
				else:
					self.strategy["WST"]["duration"]["avg"] = current_duration

			self.strategy["WST"]["duration"]["last"] = current_duration

			self.strategy["WST"]["last"] = WST_timestamp

			self.update_json()

		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			getErrorInfo(ex)

	def WSOB_update(self, WSOB_timestamp=None):
		try:

			current_duration = None

			if not WSOB_timestamp:
				WSOB_timestamp = float(time.time())

			if self.strategy["WSOB"]["last"]:
				current_duration = WSOB_timestamp - self.strategy["WSOB"]["last"]

			if current_duration:

				if self.strategy["WSOB"]["duration"]["max"]:
					if current_duration > self.strategy["WSOB"]["duration"]["max"]:
						self.strategy["WSOB"]["duration"]["max"] = current_duration
				else:
					self.strategy["WSOB"]["duration"]["max"] = current_duration

				if self.strategy["WSOB"]["duration"]["min"]:
					if current_duration < self.strategy["WSOB"]["duration"]["min"]:
						self.strategy["WSOB"]["duration"]["min"] = current_duration
				else:
					self.strategy["WSOB"]["duration"]["min"] = current_duration

				if self.strategy["WSOB"]["duration"]["avg"]:
					self.strategy["WSOB"]["duration"][
						"avg"] = (self.strategy["WSOB"]["duration"]["avg"] + current_duration) / 2
				else:
					self.strategy["WSOB"]["duration"]["avg"] = current_duration

			self.strategy["WSOB"]["duration"]["last"] = current_duration

			self.strategy["WSOB"]["last"] = WSOB_timestamp

			self.update_json()
		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			getErrorInfo(ex)

	def strategy_cycle_duration_update(self, start=None, end=None):
		try:

			current_duration = None

			if start:
				self.strategy["cycle"]["start"] = float(start)
				self.strategy["cycle"]["stop"] = None
			if end:
				self.strategy["cycle"]["stop"] = float(end)

			if self.strategy["cycle"]["start"] and self.strategy["cycle"]["stop"]:
				current_duration = self.strategy["cycle"]["stop"] - self.strategy["cycle"]["start"]

			if current_duration:
				if current_duration < 0:
					print("start ", start, " end ", end)

				if self.strategy["cycle"]["duration"]["max"]:
					if current_duration > self.strategy["cycle"]["duration"]["max"]:
						self.strategy["cycle"]["duration"]["max"] = current_duration
				else:
					self.strategy["cycle"]["duration"]["max"] = current_duration

				if self.strategy["cycle"]["duration"]["min"]:
					if current_duration < self.strategy["cycle"]["duration"]["min"]:
						self.strategy["cycle"]["duration"]["min"] = current_duration
				else:
					self.strategy["cycle"]["duration"]["min"] = current_duration

				if self.strategy["cycle"]["duration"]["avg"]:
					self.strategy["cycle"]["duration"][
						"avg"] = (self.strategy["cycle"]["duration"]["avg"] + current_duration) / 2
				else:
					self.strategy["cycle"]["duration"]["avg"] = current_duration

			self.strategy["cycle"]["duration"]["last"] = current_duration

			self.update_json()

		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			getErrorInfo(ex)

	def strategy_trade_duration_update(self, trade_timestamp=None):

		try:

			current_duration = None

			if not trade_timestamp:
				trade_timestamp = float(time.time())

			if self.strategy["trade"]["last"]:
				current_duration = trade_timestamp - self.strategy["trade"]["last"]

			if current_duration:

				if self.strategy["trade"]["duration"]["max"]:
					if current_duration > self.strategy["trade"]["duration"]["max"]:
						self.strategy["trade"]["duration"]["max"] = current_duration
				else:
					self.strategy["trade"]["duration"]["max"] = current_duration

				if self.strategy["trade"]["duration"]["min"]:
					if current_duration < self.strategy["trade"]["duration"]["min"]:
						self.strategy["trade"]["duration"]["min"] = current_duration
				else:
					self.strategy["trade"]["duration"]["min"] = current_duration

				if self.strategy["trade"]["duration"]["avg"]:
					self.strategy["trade"]["duration"][
						"avg"] = (self.strategy["trade"]["duration"]["avg"] + current_duration) / 2
				else:
					self.strategy["trade"]["duration"]["avg"] = current_duration

			self.strategy["trade"]["duration"]["last"] = current_duration

			self.strategy["trade"]["last"] = trade_timestamp

			self.update_json()
		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			getErrorInfo(ex)

	def strategy_buy_duration_update(self, buy_timestamp=None):

		try:

			current_duration = None

			if not buy_timestamp:
				buy_timestamp = float(time.time())

			self.strategy_trade_duration_update(buy_timestamp)

			if self.strategy["buy"]["last"]:
				current_duration = buy_timestamp - self.strategy["buy"]["last"]

			if current_duration:

				if self.strategy["buy"]["duration"]["max"]:
					if current_duration > self.strategy["buy"]["duration"]["max"]:
						self.strategy["buy"]["duration"]["max"] = current_duration
				else:
					self.strategy["buy"]["duration"]["max"] = current_duration

				if self.strategy["buy"]["duration"]["min"]:
					if current_duration < self.strategy["buy"]["duration"]["min"]:
						self.strategy["buy"]["duration"]["min"] = current_duration
				else:
					self.strategy["buy"]["duration"]["min"] = current_duration

				if self.strategy["buy"]["duration"]["avg"]:
					self.strategy["buy"]["duration"][
						"avg"] = (self.strategy["buy"]["duration"]["avg"] + current_duration) / 2
				else:
					self.strategy["buy"]["duration"]["avg"] = current_duration

			self.strategy["buy"]["duration"]["last"] = current_duration

			self.strategy["buy"]["last"] = buy_timestamp

			self.update_json()
		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			getErrorInfo(ex)

	def strategy_sell_duration_update(self, sell_timestamp=None):

		try:

			current_duration = None

			if not sell_timestamp:
				sell_timestamp = float(time.time())

			self.strategy_trade_duration_update(sell_timestamp)

			if self.strategy["sell"]["last"]:
				current_duration = sell_timestamp - self.strategy["sell"]["last"]

			if current_duration:

				if self.strategy["sell"]["duration"]["max"]:
					if current_duration > self.strategy["sell"]["duration"]["max"]:
						self.strategy["sell"]["duration"]["max"] = current_duration
				else:
					self.strategy["sell"]["duration"]["max"] = current_duration

				if self.strategy["sell"]["duration"]["min"]:
					if current_duration < self.strategy["sell"]["duration"]["min"]:
						self.strategy["sell"]["duration"]["min"] = current_duration
				else:
					self.strategy["sell"]["duration"]["min"] = current_duration

				if self.strategy["sell"]["duration"]["avg"]:
					self.strategy["sell"]["duration"][
						"avg"] = (self.strategy["sell"]["duration"]["avg"] + current_duration) / 2
				else:
					self.strategy["sell"]["duration"]["avg"] = current_duration

			self.strategy["sell"]["duration"]["last"] = current_duration

			self.strategy["sell"]["last"] = sell_timestamp

			self.update_json()
		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			getErrorInfo(ex)

	def strategy_spread_duration_update(self, spread):

		try:
			spread = float(spread)

			if self.strategy["spread"]["max"]:
				if spread > self.strategy["spread"]["max"]:
					self.strategy["spread"]["max"] = spread
			else:
				self.strategy["spread"]["max"] = spread

			if self.strategy["spread"]["min"]:
				if spread < self.strategy["spread"]["min"]:
					self.strategy["spread"]["min"] = spread
			else:
				self.strategy["spread"]["min"] = spread

			if self.strategy["spread"]["avg"]:
				self.strategy["spread"]["avg"] = (self.strategy["spread"]["avg"] + spread) / 2
			else:
				self.strategy["spread"]["avg"] = spread

			self.strategy["spread"]["last"] = spread

			self.update_json()
		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			getErrorInfo(ex)

	def update_json(self):
		try:
			pass
			with open(str(STATISTICA_PERCORSO).strip(), "w") as file:
				file.write(json.dumps(self.strategy, sort_keys=True, indent=4).strip())
			# NON VA MOLTO BENE, DA RIPENSARE
		except Exception as ex:
			# In caso di eccezioni printo e loggo tutti i dati disponibili
			getErrorInfo(ex)
