## Description

Connect 4 game which uses python WebSockets to establish a conection between 2 users playing the same connect 4 game.

While I was given starter code (from https://websockets.readthedocs.io/en/stable/intro/tutorial1.html#part-1-send-receive) to implement the websocket server, handling clicks, etc, the game logic (i.e. parsing json events using the handler function in app.py) was done myself

## Prerequisites

In order to run this code you must install websockets

pip install websockets

## Starting HTTP server

python -m http.server

## Starting WebSocket server 

python app.py 

# Interactive client

python -m websockets ws://localhost:8001/

# Exiting 

Exit client, HTTP server, and websocket server using:

Ctrl-C



