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

        self.generals = []
        self.cities = []

        self.map = []  # Comprehensive map including size, armies and terrains info.
        self.size = None
        self.width = None
        self.height = None

        self.armies = []
        self.terrains = []

        # Groups that are organized through the _update_groups methods.
        # Tiles are represented as (x, y).
        self.owned_tiles = []
        self.empty_tiles = []
        self.enemy_tiles = []
        self.city_tiles = []
        self.general_tiles = []

        # Checks for identifying enemy tiles, enemy tiles are not these things.
        # Enemy tiles are also not player's tile.
        self.enemy_tiles_check = [Map.TILE_EMPTY, 
                                 Map.TILE_MOUNTAIN,
                                 Map.TILE_FOG,
                                 Map.TILE_FOG_OBSTACLE]
        # The tile is invalidated for pathfinding if it is any one of these things.
        self.validate_tiles_check = [Map.TILE_MOUNTAIN,
                                     Map.TILE_FOG,
                                     Map.TILE_FOG_OBSTACLE]


        self._first_update = False
        self.update(data)


    def update(self, data):
        """
        Update the internal map to reflect recent changes.
        """
        self._patch(self.map, data["map_diff"])
        self._patch(self.cities, data["cities_diff"])

        if not self._first_update:
            self._first_update = True
            self.width = self.map[0]
            self.height = self.map[1]
            self.size = self.width*self.height

        self.generals = data["generals"]
        self.armies = self._list_to_2D(self.map[2:self.size+2], self.width)
        self.terrains = self._list_to_2D(self.map[self.size+2:], self.width)

        self._update_groups()


    def print_everything(self):
        """ Print everything relevant """
        print(chr(27) + "[2J")  # Clear console.

        print(str(self.width) + ", " + str(self.height))
        #print("Owned tiles: " + str(self.owned_tiles))
        print("Empty tiles: " + str(self.empty_tiles))
        #print("Enemy tiles: " + str(self.enemy_tiles))
        #print("City tiles: " + str(self.city_tiles))
        #print("General tiles: " + str(self.general_tiles))
        print("Armies:")
        self._print_map(self.armies, self.width, self.height)
        #print("Terrains:")
        #self._print_map(self.terrains, self.width, self.height)


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
        return self._get_closest_tile_from_group(source_tile, self.empty_tiles)


    def get_closest_enemy_tile(self, source_tile):
        return self._get_closest_tile_from_group(source_tile, self.enemy_tiles)


    def get_closest_enemy_general_tile(self, source_tile):
        return self._get_closest_tile_from_group(source_tile, self.general_tiles)

    def _get_closest_tile_from_group(self, source_tile, tile_group):
        """
        Find the nearest tile from the specified groupto the specified tile.
        Return (x, y).
        """
        closest_distance = 999
        closest_tile = None
        for tile in tile_group:
            distance = self.manhattan_distance(source_tile, tile)
            if (distance < closest_distance and 
                self.validate_tile(tile) and
                self.construct_path(tile, source_tile)):  
                # Validate tile, make sure it has a path to source.
                closest_distance = distance
                closest_tile = tile
        return closest_tile


    def _update_groups(self):
        """ 
        Group the tiles into a variety of useable lists.
        Lists grouped: owned tiles, empty tiles, enemy tiles.
        """
        self.owned_tiles = []
        self.empty_tiles = []
        self.enemy_tiles = []
        self.city_tiles = []
        self.general_tiles = []
        for y in range(self.height):
            for x in range(self.width):
                index = self.coord_to_index((x, y), self.width)
                if index in self.cities:
                    self.city_tiles.append((x, y))
                if (index in self.generals and
                    index != self.generals[self.player_index]):
                    self.general_tiles.append((x, y))

                if self.terrains[x][y] == self.player_index:
                    self.owned_tiles.append((x, y))
                elif (self.terrains[x][y] == Map.TILE_EMPTY and
                      (x, y) not in self.city_tiles):
                    # Exclude city tiles.
                    self.empty_tiles.append((x, y))
                elif self.terrains[x][y] not in self.enemy_tiles_check:
                    self.enemy_tiles.append((x, y))





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
            return 1/(self.armies[tile[0]][tile[1]]+1)
        else: return self.armies[tile[0]][tile[1]]+1


    # Implements astar
    def validate_tile(self, tile):
        """
        Validate the tile for the purpose of pathfinding.
        tile is (x, y).
        """
        if (tile and
            tile[0] >= 0 and
            tile[1] >= 0 and
            tile[0] < self.width and
            tile[1] < self.height and
            self.terrains[tile[0]][tile[1]] not in self.validate_tiles_check):
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
