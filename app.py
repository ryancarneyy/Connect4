#!/usr/bin/env python

import asyncio

import websockets

# handler function 
import json

from connect4 import PLAYER1, PLAYER2, Connect4


async def handler(websocket):
    game = Connect4()
    async for message in websocket:
        try:
            # message = await websocket.recv()
            # Received event from js
            event = json.loads(message)
            print("Received event:", event)
            column = event.get('column')
            if column is None:
                print("Invalid column")
                continue
            
            # passing move to Connect4 game 
            if game.last_player == PLAYER2:
                try:
                    row = game.play(PLAYER1, column)
                except RuntimeError as e:
                    event = {
                        'type': 'error',
                        'message': e
                    }
                    await websocket.send(json.dumps(event))
                    continue
            else:
                try:
                    row = game.play(PLAYER2, column)
                except RuntimeError as e:
                    event = {
                        'type': 'error',
                        'message': e
                    }
                    await websocket.send(json.dumps(event))
                    continue

            # Play event
            event = {
                'type': 'play',
                'player': game.last_player,
                'column': column,
                'row': row
            }
            await websocket.send(json.dumps(event))
            # If there is a win
            if game.last_player_won:
                event = {
                    'type': 'win',
                    'player': game.last_player
                }
                await websocket.send(json.dumps(event))
            
        except websockets.ConnectionClosed:
            print("Connection closed")
            break
        except json.JSONDecodeError:
            print("Failed to decode JSON")
        
    # for player, column, row in [
    #     (PLAYER1, 3, 0),
    #     (PLAYER2, 3, 1),
    #     (PLAYER1, 4, 0),
    #     (PLAYER2, 4, 1),
    #     (PLAYER1, 2, 0),
    #     (PLAYER2, 1, 0),
    #     (PLAYER1, 5, 0),
    # ]:
    #     event = {
    #         "type": "play",
    #         "player": player,
    #         "column": column,
    #         "row": row,
    #     }
    #     await websocket.send(json.dumps(event))
    #     await asyncio.sleep(0.5)
    # event = {
    #     "type": "win",
    #     "player": PLAYER1,
    # }
    # await websocket.send(json.dumps(event))

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
