#!/usr/bin/env python

import asyncio
import websockets
# handler function 
import json
from connect4 import PLAYER1, PLAYER2, Connect4

# access token
import secrets

import os
import signal

JOIN = {}

async def start(websocket):
    game = Connect4()
    connected = {websocket} # set containing websocket

    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = (game, connected) # tuple of game and connected
    
    try:
        # Send the secret access token to the browser of the first player,
        # where it'll be used for building a "join" link.
        event = {
            "type": "init",
            "join": join_key
        }
        await websocket.send(json.dumps(event))

        # Temporary - for testing.
        print("first player started game", id(game))
        async for message in websocket:
            await play(websocket, game, PLAYER1, connected)

    finally:
        del JOIN[join_key] 

async def join(websocket, join_key):
    try:
        (game, connected) = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found")
        return 
    
    connected.add(websocket)
    try:
        # Temporary - for testing.
        print("second player joined game", id(game))
        async for message in websocket:
            await play(websocket, game, PLAYER2, connected)

    finally:
        connected.remove(websocket)

async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def broadcast_message(connected, message):
    for websocket in connected:
        await websocket.send(message)


async def play(websocket, game, player, connected):
    async for message in websocket:
        try:
            # Received event from js
            event = json.loads(message)
            assert event['type'] == 'play'
            print("Received event:", event)
            column = event.get('column')
            if column is None:
                print("Invalid column")
                continue
            
            # passing move to Connect4 game 
            try:
                row = game.play(player, column)
            except RuntimeError as e:
                event = {
                    'type': 'error',
                    'message': str(e)
                }
                await broadcast_message(connected, json.dumps(event))
                continue

            # Play event
            event = {
                'type': 'play',
                'player': player,
                'column': column,
                'row': row
            }
            await broadcast_message(connected, json.dumps(event))
            # If there is a win
            if game.last_player_won:
                event = {
                    'type': 'win',
                    'player': game.last_player
                }
                await broadcast_message(connected, json.dumps(event))
            
        except websockets.ConnectionClosed:
            print("Connection closed")
            break
        except json.JSONDecodeError:
            print("Failed to decode JSON")
        



async def handler(websocket):
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event['type'] == 'init'
    if 'join' in event:
        print(event['join'])
        await join(websocket, event['join'])
    else: 
        await start(websocket)


async def main():
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT", "8001"))
    async with websockets.serve(handler, "", port):
        await stop

if __name__ == "__main__":
    asyncio.run(main())
