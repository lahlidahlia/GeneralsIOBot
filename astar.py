from queue import PriorityQueue
import math
import abc

class A_star(metaclass=abc.ABCMeta):
    """ 
    A-star implementation assuming that all tile objects are represented 
    as a tuple of (x, y).
    """
    def construct_path(self, start_tile, goal_tile):
        """
        Construct a path using the a-star algorithm
        Returns a path list of (x, y), starting at, but doesn't include, start_tile.
        """
        if not self.validate_tile(goal_tile):
            print("Error: Invalid goal tile: " + str(goal_tile))
            return None
        if start_tile == goal_tile:
            return [start_tile]

        frontier = PriorityQueue()
        frontier.put((0, start_tile))
        came_from = {}
        came_from[start_tile] = None
        cost_so_far = {}
        cost_so_far[start_tile] = 0
        
        while not frontier.empty():
            current = frontier.get()[1]
            #print("Expanding: {}, {}".format(current[0], current[1]))
            
            if current == goal_tile:
                break
            
            for next in self.get_neighbors(current):
                new_cost = cost_so_far[current] + self.get_cost(next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.manhattan_distance((goal_tile[0], goal_tile[1]), (next[0], next[1]))
                    #print("Priority: {}, {}: {}".format(next[0], next[1], priority))
                    frontier.put((priority, next))
                    came_from[next] = current
                
        if goal_tile not in came_from:
            # Check to make sure that we found a way to this tile.
            return None
        current = goal_tile
        path = [current]
        while current != start_tile:
            current = came_from[current]
            path.append(current)
        path.pop()  # Remove the starting node.
        path.reverse()
        return path
                

    def manhattan_distance(self, a, b):
       # Manhattan distance on a square grid
       return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


    @abc.abstractmethod
    def get_neighbors(self, tile):
        """ Get the neighbors of the tile. """
        raise NotImplementedError

    
    @abc.abstractmethod
    def get_cost(self, tile):
        """ Get the cost to traverse through this tile. """
        raise NotImplementedError


    @abc.abstractmethod
    def validate_tile(self, tile):
        """ True if the tile is valid, False otherwise. """
        raise NotImplementedError
