#!/usr/bin/env python

import asyncio
import websockets
# handler function 
import json
from connect4 import PLAYER1, PLAYER2, Connect4

# access token
import secrets

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
            "join": join_key,
        }
        await websocket.send(json.dumps(event))

        # Temporary - for testing.
        print("first player started game", id(game))
        async for message in websocket:
            print("first player sent", message)

    finally:
        del JOIN[join_key] #

async def handler(websocket):
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    # First player starts a new game.
    await start(websocket)

# async def handler(websocket):
#     game = Connect4()

#     async for message in websocket:
#         try:
#             # message = await websocket.recv()
#             # Received event from js
#             event = json.loads(message)
#             assert event['type'] == 'play'
#             print("Received event:", event)
#             column = event.get('column')
#             if column is None:
#                 print("Invalid column")
#                 continue
            
#             # passing move to Connect4 game 
#             if game.last_player == PLAYER2:
#                 try:
#                     row = game.play(PLAYER1, column)
#                 except RuntimeError as e:
#                     event = {
#                         'type': 'error',
#                         'message': e
#                     }
#                     await websocket.send(json.dumps(event))
#                     continue
#             else:
#                 try:
#                     row = game.play(PLAYER2, column)
#                 except RuntimeError as e:
#                     event = {
#                         'type': 'error',
#                         'message': e
#                     }
#                     await websocket.send(json.dumps(event))
#                     continue

#             # Play event
#             event = {
#                 'type': 'play',
#                 'player': game.last_player,
#                 'column': column,
#                 'row': row
#             }
#             await websocket.send(json.dumps(event))
#             # If there is a win
#             if game.last_player_won:
#                 event = {
#                     'type': 'win',
#                     'player': game.last_player
#                 }
#                 await websocket.send(json.dumps(event))
            
#         except websockets.ConnectionClosed:
#             print("Connection closed")
#             break
#         except json.JSONDecodeError:
#             print("Failed to decode JSON")
        

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
