
#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import List, Tuple, Dict, Union
from math import inf
import copy


@unique
class Direction(IntEnum):
    """ Directions in shortcut """
    NORTH = 0   
    EAST = 90
    SOUTH = 180
    WEST = 270





Weight = int
"""
Weight of a given path (received from the server)

Value:  -1 if blocked path
        >0 for all other paths
        never 0
"""

class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    def __init__(self):
        """ Initializes the data structure """
        self.target = None
        self.map = {} #initalizes a dict named map to store all the nodes and their paths
        self.task_done = False
        self.type_task_done = ""
        self.open_nodes = []
        self.edges_open_node = {}
        self.scanned_nodes = []
        self.meteor_nodes = []

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):
        """
         Adds a bidirectional path defined between the start and end coordinates to the map and assigns the weight to it
         
        Example:
            add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
        :param start: 2-Tuple
        :param target:  2-Tuple
        :param weight: Integer
        :return: void
        """

        start2, start_direction = start     #get directions from start
        start_x, start_y = start2           #get coordinates from start
        target2, target_direction = target  #get directions from target
        target_x, target_y = target2        #get coordinates from target

        # {(x,y):[SOUTH,NORTH]}

        if start2 in self.open_nodes:
            if start_direction in self.edges_open_node[start2]:
                self.edges_open_node[start2].remove(start_direction)
            if len(self.edges_open_node[start2]) <= 0:
                del self.edges_open_node[start2]
                self.open_nodes.remove(start2)

        if target2 in self.open_nodes:
            if target_direction in self.edges_open_node[target2]:
                self.edges_open_node[target2].remove(target_direction)

            if len(self.edges_open_node[target2]) <= 0:
                del self.edges_open_node[target2]
                self.open_nodes.remove(target2)



        # if start2 in self.map:
        #     if start_direction not in self.map[start2]: #not sure if it checks whats in the Tuple -> checks for (x,y) not for the y in itself
        #         paths = self.map[start2] #gets to already mapped paths so they dont get overwritten
        #         paths[start_direction] = (target2,target_direction,weight)
        #         self.map[start2] = paths #should work properly
        #     #else would be pointless since on every node theres only one path in each direction
        #
        # else:
        #     paths = {start_direction : (target2,target_direction,weight)}
        #     self.map[start2] = paths #should work properly
        
                
        #basically the same as above, just reversed bc it is supposed to add a bidirectional path

        if target2 in self.map:
            if target_direction not in self.map[target2]:
                paths = self.map[target2]
                paths[target_direction] = (start2,start_direction,weight)
                self.map[target2] = paths
        else:
            paths = {target_direction : (start2,start_direction,weight)}
            self.map[target2] = paths

        if start2 not in self.map:
            self.map[start2] = {}

        if target2 not in self.map:
            self.map[target2] = {}

        # if start_direction not in self.map[start2]:
        #     self.map[target2][start_direction] = {}
        #
        # if target_direction not in self.map[target2]:
        #     self.map[target2][target_direction] = {}

        self.map[start2][start_direction] = (target2, target_direction, weight)
        self.map[target2][target_direction] = (start2, start_direction, weight)
        
 


    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:
        """
        Returns all paths

        Example:
            {
                (0, 3): {
                    Direction.NORTH: ((0, 3), Direction.WEST, 1),
                    Direction.EAST: ((1, 3), Direction.WEST, 2),
                    Direction.WEST: ((0, 3), Direction.NORTH, 1)
                },
                (1, 3): {
                    Direction.WEST: ((0, 3), Direction.EAST, 2),
                    ...
                },
                ...
            }
        :return: Dict
        """

        # YOUR CODE FOLLOWS (remove pass, please!)

        return self.map     

    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Union[None, List[Tuple[Tuple[int, int], Direction]]]:

        ##- returns the shortest path between a give start (tuple of x and y coordinate) and a given target (tuple of x and y coordinate) -##
        # - returns None if there is no possible path between those two nodes

        # checks if we dont even know the start or target
        if start not in self.map or target not in self.map:
            return None
        # distance: dict of "keys who are already on the map" : "distance to start node"
        distance = copy.deepcopy(self.map)
        # predecessor: dict of  "node" : "predecessor of said node"
        predecessor = copy.deepcopy(self.map)
        for i in self.map:
            # sets all predecessors to None
            predecessor[i] = None
            # sets all distances to infinity
            distance[i] = inf
        # distance of startnode gets set to 0
        distance[start] = 0
        # unvisited_nodes: List of nodes where the shortest path hasnt been found yet
        unvisited_nodes = copy.deepcopy(list(self.map.keys()))
        while bool(unvisited_nodes):
            # Node in unvisited_nodes with the smallest value in distance
            closest_unvisited_node = next(iter(unvisited_nodes))
            # goes through every node in distance to find the new closest unvisited node
            for node in distance:
                if distance[node] < distance[closest_unvisited_node] and node in unvisited_nodes:
                    # updates closest_unvisited_node
                    closest_unvisited_node = node
            # print(f"distance to {closest_unvisited_node}: {distance[closest_unvisited_node]}")
            if closest_unvisited_node == target:
                break
            # if the closest_unvisited_node is not reachable, the algorithm stops and returns None
            if distance[closest_unvisited_node] == inf:
                return None
            # removes the closest_unvisited_node from unvisited_nodes because now it has been visited
            unvisited_nodes.remove(closest_unvisited_node)
            # temporary list of neighbours of the closest_unvisited_node
            neighbours = []

            # fills neighbours
            for node in self.map[closest_unvisited_node]:
                neighbours.append(self.map[closest_unvisited_node][node][0])

            # goes through neighbours to see if any neighbour is an unvisited node
            for neighbour in neighbours:
                if neighbour in unvisited_nodes:
                    # closest_unvisited_node becomes predecessor of neighbour if if the distance between the
                    # two is shorter than the already known shortest_path
                    distance_closest_unvisited_node_to_neighbour = 0
                    # goes through every known path of closest_unvisited_node to see if
                    # one of these paths goes to neighbour
                    for direction in self.map[closest_unvisited_node]:
                        if self.map[closest_unvisited_node][direction][0] == neighbour:
                            # if so, it updates the distance_closed_unvisited_node_to_neighbour
                            distance_closest_unvisited_node_to_neighbour = self.map[closest_unvisited_node][direction][
                                2]

                    # checks if the path between unvisited_node to neighbour isnt blocked
                    if distance_closest_unvisited_node_to_neighbour < 0:
                        continue
                    alternative = distance[closest_unvisited_node] + distance_closest_unvisited_node_to_neighbour

                    # checks if alternaitve is faster than the already found path
                    if alternative < distance[neighbour]:
                        distance[neighbour] = alternative
                        predecessor[neighbour] = closest_unvisited_node

        path = [target]
        cur_node = target

        # assembles the shortest path
        while bool(predecessor[cur_node]):
            cur_node = predecessor[cur_node]
            path.insert(0, cur_node)

        ###- add directions to the already assembled shortest_path -###

        # empty list to fill with the shortest path + direction Tuples
        path_with_directions = []
        # sets the direction to a random direction
        cur_direction = Direction.SOUTH

        # goes through path to add the shortest path between two adjacent nodes in the already assembled shortest path
        iterator = 1
        for node in path:
            # searches for the path with the smallest weight between those two nodes
            cur_weight = inf
            for direction in self.map[node]:
                if iterator < len(path):
                    # if a new smallest weight has been found it updates the cur_weight
                    if path[iterator] == self.map[node][direction][0] and self.map[node][direction][2] < cur_weight:
                        cur_direction = direction
                        cur_weight = self.map[node][direction][2]

            path_with_directions.append((node, cur_direction))
            iterator += 1
        # deletes the last element since its the target node
        path_with_directions.pop()
        # returns the shortest path
        return path_with_directions

    ################################################################
    """
    list_nodes = [(1,2),(2,3)]

    directions_open_node = {
                    (1,2) : [NORTH,SOUTH,EAST],

                    (2,3) : [EAST]
                 }
    """

    def add_open_node(self, node, direction):

        # dont add node if already in map
        if node in self.scanned_nodes or node in self.map and (self.map[node].keys()) == 4:
            return

        if node in self.map and direction in self.map[node]:
            if node not in self.open_nodes:
                self.open_nodes.append(node)
            self.edges_open_node[node] = []

        elif node not in self.open_nodes:
            self.open_nodes.append(node)
            self.edges_open_node[node] = [direction]
        else:
            self.edges_open_node[node].append(direction)

    def closest_open_node(self, start):
        currentdistance = inf
        shortest_path = None
        for node in self.open_nodes:
            path = self.shortest_path(start, node)
            if path is None:
                continue
            cur_weight = 0

            # determine total weight of the path
            for path_node in path:
                cur_weight += self.map[path_node[0]][path_node[1]][2]

            # update node if shorter path
            if currentdistance > cur_weight:
                currentdistance = cur_weight
                shortest_path = path
        return shortest_path

    def get_open_edges(self, node):
        if node in self.edges_open_node:
            return self.edges_open_node[node]
        return []



