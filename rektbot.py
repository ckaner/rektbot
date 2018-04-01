#!/usr/bin/python3
# rektbot.py

"""A very basic Discord bot that pulls in the BitMex liquidations for
XBTUSD and posts them to a Discord channel of your choice. Please note
that you need to get a valid token for the bot through your Discord app
and also the channel ID for the channel you want to post in.
"""

import discord
import websockets
import asyncio
import json

# Find out the channel ID in Discord:
# 'Appearance' -> 'Developer Mode' -> Toggle
# Then, right-click the channel and select 'Copy ID'
channel_id = '012345678901234556'
# Get your token like this:
# https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token
token = 'XXXXXXXXXXXXXXXXXXXXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYYYyyyyyyy'


client = discord.Client()

@client.event
async def on_ready():
    print('Logged into Discord as %s (%s)' % (client.user.name, client.user.id))

async def receive_bitmex_data():
    await client.wait_until_ready()
    async with websockets.connect("wss://www.bitmex.com/realtime?subscribe=liquidation:XBTUSD") as ws:
        channel = discord.Object(id=channel_id)
        await client.send_message(channel, "hello, world!")
        while not client.is_closed:
            try:
                data = await asyncio.wait_for(ws.recv(), timeout=20)
            except asyncio.TimeoutError:
                try:
                    pong_waiter = await ws.ping()
                    await asyncio.wait_for(pong_waiter, timeout=10)
                except asyncio.TimeoutError:
                    break
            else:
                print('.', end='', flush=True)
                await handle_data(data, channel)
        print('Client closed')
        ws.close()

async def handle_data(data, channel):
    """ Liquidation messages look like this:
     {
       'table': 'liquidation',
       'data':
           [{
             'orderID': '49fd4c3a-c832-dced-11d4-1e7042f97b62',
             'price': 6705,
             'side': 'Buy',
             'leavesQty': 3,
             'symbol': 'XBTUSD'
           }],
       'action': 'insert'
     }
    """
    x = json.loads(data)
    if 'table' in x and x['table'] == 'liquidation':
        #print('########################### LIQUIDATION ###########################')
        #print(x)
        #await client.send_message(channel, x)
        # XXX: Clean this mess up
        if 'action' in x and x['action'] == 'insert':
            if 'data' in x and isinstance(x['data'], list):
                side = 'short' if x['data'][0]['side'] == 'Buy' else 'long'
                liq_str = 'Liquidating ' + x['data'][0]['symbol'] + ' ' + side + ': ' + x['data'][0]['side'] + ' ' + str(x['data'][0]['leavesQty']) + ' at ' + str(x['data'][0]['price'])
                print(liq_str)
                await client.send_message(channel, liq_str)

client.loop.create_task(receive_bitmex_data())
client.run(token)
