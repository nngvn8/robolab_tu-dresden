
#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import List, Tuple, Dict, Union
from math import inf


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
        self.unknown_paths = {}  #change to nodes_w_open_edges

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
     
        abstand = copy.deepcopy(map)   
        vorgänger = copy.deepcopy(map)                                   
        for v in map:
            vorgänger[v] = None 
            abstand[v] = 999 #spaghetti
        abstand[Startknoten] = 0        
          ################################ 
        NodeWO = copy.deepcopy(list(map.keys()))
        #abstandhelp = copy.deepcopy(abstand)
        while bool(NodeWO):   
            #u = min(abstandhelp,key = abstandhelp.get) #u:= Knoten in Q mit kleinstem Wert in abstand[]
        
            u = next(iter(NodeWO))
            for it in abstand:
                if abstand[it] < abstand[u] and it in NodeWO:
                    u = it
            NodeWO.remove(u)
            #del abstandhelp[u]
            nachbarn = []
            for i in map[u]:
                nachbarn.append(map[u][i][0])
            for v in nachbarn: 
                if v in NodeWO:                    
        ########################################################## distanz_update
                    abstanduv = 0
                    for o in map[u]:
                        if map[u][o][0] == v:
                            abstanduv = map[u][o][2]
                    alternativ = abstand[u] + abstanduv    
                    if alternativ < abstand[v]:     
                        abstand[v] = alternativ                    
                        vorgänger[v] = u

        #####################################################
        Weg = [Zielknoten]
        ab = Zielknoten

        while bool(vorgänger[ab]):  #Der Vorgänger des Startknotens ist null
            ab = vorgänger[ab]
            Weg.insert(0,ab)
        ret = []
        currentdirection = Direction.SOUTH

        iter2 = 1
        for i in Weg:
            currentweight = inf
            for direction in map[i]:
                print(direction)
                if iter2 < len(Weg):
                    if Weg[iter2] == map[i][direction][0] and map[i][direction][2] < currentweight:
                        currentdirection = direction
                        currentweight = map[i][direction][2]
        
            ret.append((i,currentdirection))
            print(Weg)
            iter2 += 1
        ret.pop()
        return ret
