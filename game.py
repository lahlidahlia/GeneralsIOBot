import random
import os
from maps import Map
class Game(object):
    def __init__(self, sio):
        self.sio = sio

        # Game data.
        self.playerIndex = None

        self.map = None  # Initialized in the first update call.


    def on_connect(self):
        print("connect")

        user_id = "tinlun123bot"
        username = "TinBot"

        self.sio.emit("set_username", user_id, username)

        custom_game_id = "tinbotprivategame"

        self.sio.emit("join_private", custom_game_id, user_id)
        self.sio.emit("set_force_start", custom_game_id, True)
        print("bot.generals.io/games/" + custom_game_id)


    def on_disconnect(self):
        print("disconnect")


    def on_reconnect(self):
        print("reconnect")


    def game_start(self, data, teams):
        self.playerIndex = data["playerIndex"];
        replay_url = 'http://bot.generals.io/replays/' + data["replay_id"];
        print("Game starting! Replay available at " + replay_url)


    def game_update(self, data, *args):
        """ Update """
        if not self.map:
            self.map = Map(data)
            return
        
        self.map.update(data)
    

    def leave_game(self):
        self.sio.emit("leave_game")


