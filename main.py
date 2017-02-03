from game import Game
import logging
logging.getLogger("socketIO-client").setLevel(logging.DEBUG)
logging.basicConfig()
from socketIO_client import SocketIO, LoggingNamespace

sio = SocketIO("http://bot.generals.io")
game = Game(sio)

sio.on("connect", game.on_connect)
sio.on("disconnect", game.on_disconnect)
sio.on("reconnect", game.on_reconnect)
sio.on("game_start", game.game_start)
sio.on("game_update", game.game_update)
sio.on("game_won", game.leave_game)
sio.on("game_lost", game.leave_game)

sio.wait()
