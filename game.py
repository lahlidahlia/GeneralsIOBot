import random
import os
from maps import Map
class Game(object):
    def __init__(self, sio):
        self.sio = sio

        # Game data.
        self.player_index = None

        self.map = None  # Initialized in the first update call.
        self.turn_number = 0
        self.file = None  # For logging.
        self.path_name = "replay_log/"

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
        if self.file:
            self.file.close()
        print("disconnect")


    def on_reconnect(self):
        print("reconnect")


    def game_start(self, data, teams):
        self.player_index = data["playerIndex"];
        replay_url = 'http://bot.generals.io/replays/' + data["replay_id"];
        print("Game starting! Replay available at " + replay_url)

        self.file = open(self.path_name + data["replay_id"], "w")


    def game_update(self, data, *args):
        """ Update """
        self.turn_number += 1
        if not self.map:
            self.map = Map(data, self.player_index)
            return
        
        self.map.update(data)
        largest_army = self.map.get_largest_owned_army()
        source = largest_army
        path = self.map.construct_path(largest_army, 
                    self.map.get_closest_empty_tile(largest_army))
        dest = path[0]
        self.attack(self.map.coord_to_index(source, self.map.width),
                    self.map.coord_to_index(dest, self.map.width),
                    False)

        # Print to console.
        self.map.print_everything()
        print("Moving: " + str(source) + " to " + str(dest))
        print("Path: " + str(path))

        # Log to file.
        self.file.write("Turn " + str(self.turn_number) + ": ")
        self.file.write("\n")


    def attack(self, start, end, is50):
        """ Wrapper function for the api's attack. """
        self.sio.emit("attack", start, end, is50)

    def leave_game(self):
        self.sio.emit("leave_game")


