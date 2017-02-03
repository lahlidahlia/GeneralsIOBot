class Map(object):
    """ Class used to deal with anything map related, such as pathfinding """
    TILE_EMPTY = -1
    TILE_MOUNTAIN = -2
    TILE_FOG = -3
    TILE_FOG_OBSTACLE = -4  # Cities and Mountains show up as Obstacles in the fog of war.

    def __init__(self, data):
        """
        data: data from the first game_update packet.
        """
        self.generals = None
        self.cities = []
        self.map = []  # Comprehensive map including size, armies and terrains info.
        self.size = None
        self.width = None
        self.height = None
        self.armies = []
        self.terrains = []

        self._first_update(data)

    def update(self, data):
        """
        Update the internal map to reflect recent changes.
        """
        self._patch(self.map, data["map_diff"])
        self._patch(self.cities, data["cities_diff"])

        armies = self.map[2:self.size+2]
        terrains = self.map[self.size+2:]

        print(chr(27) + "[2J")  # Clear console.

        print("Armies:")
        self.print_map(armies, self.width, self.height)
        print("Terrains:")
        self.print_map(terrains, self.width, self.height)


    def _first_update(self, data):
        """
        Only call this on init.
        Basically update, except with a few more variables init.
        """
        self._patch(self.map, data["map_diff"])
        self._patch(self.cities, data["cities_diff"])
        self.generals = data["generals"]

        self.width = self.map[0]
        self.height = self.map[1]
        self.size = self.width*self.height

        armies = self.map[2:self.size+2]
        terrains = self.map[self.size+2:]

        print(chr(27) + "[2J")  # Clear console.

        print("Armies:")
        self.print_map(armies, self.width, self.height)
        print("Terrains:")
        self.print_map(terrains, self.width, self.height)
        


    def get_armies(self):
        return self.armies
    
    
    def get_terrains(self):
        return self.terrains


    def get_generals(self):
        return self.generals


    def _patch(self, cache, diff):
        map_index = 0
        diff_index = 0

        while(diff_index < len(diff)):
            # Matched diff.
            map_index += diff[diff_index]
            diff_index += 1

            # Mismatched diff.
            if diff_index < len(diff):
                n = diff[diff_index]
                cache[map_index:map_index+n] = diff[diff_index+1:diff_index+1+n]
                map_index += n
                diff_index += n + 1


    def print_map(self, map_ls, width, height):
        """ 
        Print either a terrain map or an army map.
        map_ls can either be a list of armies or terrains.
        """
        for y in range(height):
            for x in range(width):
                print(map_ls[width*y + x], end=" ")
            print("")
