import asyncio
import json

import websockets


async def hello():
	uri = "wss://ws.bitstamp.net"
	jsonString = json.dumps({
		"event": "bts:subscribe",
		"data": {
		"channel": 'live_trades_btcgbp'
		}
	})

	async with websockets.connect(uri) as websocket:
		await websocket.send(jsonString)
		async for message in websocket:
			data = json.loads(message)
			print(data)
		"""
		greeting = await websocket.recv()
		print(f"< {greeting}") """


asyncio.get_event_loop().run_until_complete(hello())
