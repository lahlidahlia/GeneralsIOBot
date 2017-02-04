from astar import A_star
class Map(A_star):
    """ Class used to deal with anything map related, such as pathfinding """
    TILE_EMPTY = -1
    TILE_MOUNTAIN = -2
    TILE_FOG = -3
    TILE_FOG_OBSTACLE = -4  # Cities and Mountains show up as Obstacles in the fog of war.

    def __init__(self, data, player_index):
        """
        data: data from the first game_update packet.
        """
        self.player_index = player_index

        self.generals = None
        self.cities = []

        self.map = []  # Comprehensive map including size, armies and terrains info.
        self.size = None
        self.width = None
        self.height = None

        self.armies = []
        self.terrains = []

        # Groups that are organized through the _group_tiles methods.
        # Tiles are represented as (x, y).
        self.owned_tiles = []
        self.empty_tiles = []
        self.enemy_tiles = []

        self._first_update(data)


    def update(self, data):
        """
        Update the internal map to reflect recent changes.
        """
        self._patch(self.map, data["map_diff"])
        self._patch(self.cities, data["cities_diff"])

        self.armies = self._list_to_2D(self.map[2:self.size+2], self.width)
        self.terrains = self._list_to_2D(self.map[self.size+2:], self.width)

        self._group_tiles()


    def print_everything(self):
        """ Print everything relevant """
        print(chr(27) + "[2J")  # Clear console.
        print(chr(27) + "[2J")  # Clear console.

        print(str(self.width) + ", " + str(self.height))
        print("Owned tiles: " + str(self.owned_tiles))
        print("Empty tiles: " + str(self.empty_tiles))
        print("Enemy tiles: " + str(self.enemy_tiles))
        print("Armies:")
        self._print_map(self.armies, self.width, self.height)
        print("Terrains:")
        self._print_map(self.terrains, self.width, self.height)


    def get_neighbors(self, tile):
        """ Get non-obstacle tiles adjacent to the given tile. """
        neighbors = [(tile[0]-1, tile[1]), 
               (tile[0]+1, tile[1]),
               (tile[0], tile[1]-1),
               (tile[0], tile[1]+1)]

        ret = []
        for n in neighbors:
            if self.validate_tile(n):
                ret.append(n)

        return ret


    def get_cost(self, tile):
        """ 
        In this case, cost of the tile is how large the army is in the tile. 
        If the tile is friendly, the cost is 1/size.
        """
        if self.terrains[tile[0]][tile[1]] == self.player_index:
            return 1/self.armies[tile[0]][tile[1]]
        else: return self.armies[tile[0]][tile[1]]/1


    def get_largest_owned_army(self):
        """ Find the largest army you own. Return (x, y)"""
        largest = 0
        largest_army = None
        for tile in self.owned_tiles:
            army_size = self.armies[tile[0]][tile[1]]
            if army_size > largest:
                largest = army_size
                largest_army = tile
        return largest_army


    def get_closest_empty_tile(self, source_tile):
        """
        Find the nearest empty tile to the specified tile.
        Return (x, y).
        """
        closest_distance = 999
        closest_tile = None
        for tile in self.empty_tiles:
            distance = self.manhattan_distance(source_tile, tile)
            if distance < closest_distance and self.validate_tile(tile):
                closest_distance = distance
                closest_tile = tile
        return closest_tile


    def _group_tiles(self):
        """ 
        Group the tiles into a variety of useable lists.
        Lists grouped: owned tiles, empty tiles, enemy tiles.
        """
        self.owned_tiles = []
        self.empty_tiles = []
        self.enemy_tiles = []
        for y in range(self.height):
            for x in range(self.width):
                if self.terrains[x][y] == self.player_index:
                    self.owned_tiles.append((x, y))
                elif self.terrains[x][y] == Map.TILE_EMPTY:
                    self.empty_tiles.append((x, y))
                elif self.terrains[x][y] not in [Map.TILE_MOUNTAIN,
                                          Map.TILE_FOG,
                                          Map.TILE_FOG_OBSTACLE]:
                    self.enemy_tiles.append((x, y))


    def validate_tile(self, tile):
        if (tile[0] > 0 and
            tile[1] > 0 and
            tile[0] < self.width and
            tile[1] < self.height and
            self.terrains[tile[0]][tile[1]] != Map.TILE_MOUNTAIN):
                return True
        else: return False


    def index_to_coord(self, index, width):
        """ Turn the index of a map position to the (x, y) coordinate as a tuple. """
        return (index%width, int(index/width))


    def coord_to_index(self, coord, width):
        """ 
        Turn the coordinate (x, y) into a map index.
        """
        return coord[1]*width + coord[0]


    def _list_to_2D(self, ls, width):
        ret = []
        for _ in range(width):
            ret.append([])
        for i in range(len(ls)):
            ret[i%width].append(ls[i])
        return ret




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


    def _print_map(self, map_ls, width, height):
        """ 
        Print either a terrain map or an army map.
        map_ls can either be a list of armies or terrains.
        """
        for y in range(height):
            for x in range(width):
                print(map_ls[x][y], end="  ")
            print("")


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

        self.armies = self._list_to_2D(self.map[2:self.size+2], self.width)
        self.terrains = self._list_to_2D(self.map[self.size+2:], self.width)

        self._group_tiles()

        print(chr(27) + "[2J")  # Clear console.

        print("Armies:")
        self._print_map(self.armies, self.width, self.height)
        print("Terrains:")
        self._print_map(self.terrains, self.width, self.height)


