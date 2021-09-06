
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

        start_coordinates, start_direction = start     # get directions and coordinates from start
        target_coordinates, target_direction = target  # get directions and coordinates from target

        # remove open edges and if necessary the open node
        if start_coordinates in self.open_nodes:
            if start_direction in self.edges_open_node[start_coordinates]:
                self.edges_open_node[start_coordinates].remove(start_direction)
            if len(self.edges_open_node[start_coordinates]) <= 0:
                del self.edges_open_node[start_coordinates]
                self.open_nodes.remove(start_coordinates)

        if target_coordinates in self.open_nodes:
            if target_direction in self.edges_open_node[target_coordinates]:
                self.edges_open_node[target_coordinates].remove(target_direction)

            if len(self.edges_open_node[target_coordinates]) <= 0:
                del self.edges_open_node[target_coordinates]
                self.open_nodes.remove(target_coordinates)

        if start_coordinates not in self.map:
            self.map[start_coordinates] = {}

        if target_coordinates not in self.map:
            self.map[target_coordinates] = {}

        self.map[start_coordinates][start_direction] = (target_coordinates, target_direction, weight)
        self.map[target_coordinates][target_direction] = (start_coordinates, start_direction, weight)

        if len(self.map[start_coordinates].keys()) == 4 and start_coordinates not in self.scanned_nodes:
            self.scanned_nodes.append(start_coordinates)

        if len(self.map[target_coordinates].keys()) == 4 and target_coordinates not in self.scanned_nodes:
            self.scanned_nodes.append(target_coordinates)

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
            if distance[closest_unvisited_node] == inf:
                return None
            # if the closest_unvisited_node is not reachable, the algorithm stops and returns None
            if closest_unvisited_node == target:
                break
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

        print(f"path to open node: {path}")

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
        if node in self.scanned_nodes or node in self.map and len(self.map[node].keys()) == 4:
            return

        # node is unveiled node -> added to open nodes but with out any open edges
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
        current_distance = inf
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
            if current_distance > cur_weight:
                current_distance = cur_weight
                shortest_path = path
        return shortest_path

    def get_open_edges(self, node):
        if node in self.edges_open_node:
            return self.edges_open_node[node]
        return []



