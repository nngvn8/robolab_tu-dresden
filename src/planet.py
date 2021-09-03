
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
            
        # YOUR CODE FOLLOWS (remove pass, please!)

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



        if start2 in self.map: 
            if start_direction not in self.map[start2]: #not sure if it checks whats in the Tuple -> checks for (x,y) not for the y in itself
                paths = self.map[start2] #gets to already mapped paths so they dont get overwritten
                paths[start_direction] = (target2,target_direction,weight)    
                self.map[start2] = paths #should work properly
            #else would be pointless since on every node theres only one path in each direction

        else:
            paths = {start_direction : (target2,target_direction,weight)}
            self.map[start2] = paths #should work properly
        
                
        #basically the same as above, just reversed bc it is supposed to add a bidirectional path

        if target2 in self.map:
            if target_direction not in self.map[target2]:
                paths = self.map[target2] 
                paths[target_direction] = (start2,start_direction,weight)
                self.map[target2] = paths 
        else:
            paths = {target_direction : (start2,start_direction,weight)}
            self.map[target2] = paths
        
 


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
     
        distance = copy.deepcopy(self.map)
        predecessor = copy.deepcopy(self.map)
        for i in self.map:
            predecessor[i] = None 
            distance[i] = inf
        distance[start] = 0
        NodeWO = copy.deepcopy(list(self.map.keys()))
        while bool(NodeWO):     
            u = next(iter(NodeWO))
            for it in distance:
                if distance[it] < distance[u] and it in NodeWO:
                    u = it
            NodeWO.remove(u)
            #del distancehelp[u]
            nachbarn = []
            for i in self.map[u]:
                nachbarn.append(self.map[u][i][0])
            for v in nachbarn: 
                if v in NodeWO:                    
        ########################################################## distanz_update
                    distanceuv = 0
                    for o in self.map[u]:
                        if self.map[u][o][0] == v:
                            distanceuv = self.map[u][o][2]
                    alternativ = distance[u] + distanceuv    
                    if alternativ < distance[v]:     
                        distance[v] = alternativ                    
                        predecessor[v] = u

        #####################################################
        Weg = [target]
        ab = target

        while bool(predecessor[ab]):  #Der predecessor des Startknotens ist null
            ab = predecessor[ab]
            Weg.insert(0,ab)
        ret = []
        currentdirection = Direction.SOUTH

        iter2 = 1
        for i in Weg:
            currentweight = inf
            for direction in self.map[i]:
                if iter2 < len(Weg):
                    if Weg[iter2] == self.map[i][direction][0] and self.map[i][direction][2] < currentweight:
                        currentdirection = direction
                        currentweight = self.map[i][direction][2]
        
            ret.append((i,currentdirection))
            iter2 += 1
        ret.pop()
        return ret


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
        if node in self.map and direction in self.map[node]:
            return

        if node not in self.open_nodes:
            self.open_nodes.append(node)
            self.edges_open_node[node] = [direction]
        else:
            self.edges_open_node[node].append(direction)



    def closest_open_node(self, start):
        currentdistance = inf
        shortest_path = None
        for node in self.open_nodes:
            path = self.shortest_path(start,node)
            currentweight = 0
            start_node = node
            for end_node in path:
                currentweight += self.map[start_node][end_node][2]
                start_node = end_node
            if currentdistance > currentweight:
                currentdistance = currentweight
                shortest_path = path
        return shortest_path

    def get_open_edges(self, node):
        if node in self.edges_open_node:
            return self.edges_open_node[node]
        return []



