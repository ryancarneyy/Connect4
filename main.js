import { createBoard, playMove } from "./connect4.js";

function getWebSocketServer() {
  if (window.location.host === "ryancarneyy.github.io") {
    return "wss://connect-four-websocket-11212664fb48.herokuapp.com/";
  } else if (window.location.host === "localhost:8000") {
    return "ws://localhost:8001/";
  } else {
    throw new Error(`Unsupported host: ${window.location.host}`);
  }
}

function initGame(websocket) {
    websocket.addEventListener("open", () => {
        const params = new URLSearchParams(window.location.search);
        // second player is joining game
        let event = { type: 'init' };
        if (params.has('join')) {   
            event.join = params.get('join');
        }
        websocket.send(JSON.stringify(event));
    });
}

function sendMoves(board, websocket) {
    // When clicking a column, send a "play" event for a move in that column.
    board.addEventListener("click", ({ target }) => {
      const column = target.dataset.column;
      // Ignore clicks outside a column.
      if (column === undefined) {
        return;
      }
      const event = {
        type: "play",
        column: parseInt(column, 10),
      };
      websocket.send(JSON.stringify(event));
    });
  }

  function showMessage(message) {
    window.setTimeout(() => window.alert(message), 50);
  }
  
function receiveMoves(board, websocket) {
    websocket.addEventListener("message", ({ data }) => {
        const event = JSON.parse(data);
        switch (event.type) {
        case "init":
            // const currentURL = window.location.href;
            // const linkElement = document.querySelector(".join");
            // linkElement.dataset.link = window.location.href + "/?join=" + event.join;
            document.querySelector('.join').href = "?join=" + event.join;
            break;
        case "play":
            // Update the UI with the move.
            playMove(board, event.player, event.column, event.row);
            break;
        case "win":
            showMessage(`Player ${event.player} wins!`);
            // No further messages are expected; close the WebSocket connection.
            websocket.close(1000);
            break;
        case "error":
            showMessage(event.message);
            break;
        default:
            throw new Error(`Unsupported event type: ${event.type}.`);
        }
    });
}


window.addEventListener("DOMContentLoaded", () => {
    // Initialize the UI.
    const board = document.querySelector(".board");
    createBoard(board);
    // Open the WebSocket connection and register event handlers.
    const websocket = new WebSocket(getWebSocketServer());
    initGame(websocket)
    receiveMoves(board, websocket);
    sendMoves(board, websocket);
  });