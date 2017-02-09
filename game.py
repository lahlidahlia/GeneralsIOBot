import random
import os
from maps import Map
class Game(object):
    def __init__(self, sio):
        self.sio = sio

        # Game data.
        self.player_index = None

        self.map = None  # Initialized in the first update call.
        self.update_count = 0
        self.file = None  # For logging.
        self.path_name = "replay_log/"

    def on_connect(self):
        print("connect")

        user_id = "notbotbotbot"
        username = "TinBot"

        self.sio.emit("set_username", user_id, username)

        custom_game_id = "tinbotprivategame"

        self.sio.emit("join_private", custom_game_id, user_id)
        self.sio.emit("set_force_start", custom_game_id, True)
        #self.sio.emit("join_1v1", user_id)
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
        self.update_count += 1
        if not self.map:
            self.map = Map(data, self.player_index)
            return
        
        self.map.update(data)
        # Source.
        largest_army = self.map.get_largest_owned_army()
        source = largest_army
        
        # Destination.
        dest = None
        if(self.map.general_tiles):
            dest = self.map.get_closest_enemy_general_tile(largest_army)
        elif(self.map.enemy_tiles):
            dest = self.map.get_closest_enemy_tile(largest_army)
        elif(self.map.empty_tiles):
            dest = self.map.get_closest_empty_tile(largest_army)

        # Next attack.
        path = self.map.construct_path(largest_army, dest)
        attack_dest = None
        if path:
            attack_dest = path[0]
            # Send attack command.
            self.attack(self.map.coord_to_index(source, self.map.width),
                        self.map.coord_to_index(attack_dest, self.map.width),
                        False)

        #Print to console.
        self.map.print_everything()
        if path:
            print("Moving from " + str(source) + " to " +
                    str(attack_dest) + " towards " + str(dest))
        else:
            print("Moving from " + str(source) + " towards " + str(dest))
        print("Path: " + str(path))
        print("Generals: " + str(self.map.generals))

        # Log to file.
        self.file.write("Turn " + str(self.update_count) + "\n")
        if path:
            self.file.write("Path: " + str(path))
            self.file.write("Source: " + str(source) + 
                    ", To: " + str(attack_dest) + "\n")
            self.file.write("Moving toward: " + str(dest) + "\n")
        else:
            self.file.write("THERE ARE NO PATH PLEASE TAKE A LOOK")
            self.file.write("Source: " + str(source) + ", Dest: " + str(dest) + "\n")
        self.file.write("\n-------------------\n")


    def attack(self, start, end, is50):
        """ Wrapper function for the api's attack. """
        self.sio.emit("attack", start, end, is50)

    def leave_game(self, *data):
        self.sio.emit("leave_game")


