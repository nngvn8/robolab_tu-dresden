
#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import List, Tuple, Dict, Union


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
            if target_direction not in self.map[start2]: #not sure if it checks whats in the Tuple -> checks for (x,y) not for the y in itself
                paths = self.map[start2] #gets to already mapped paths so they dont get overwritten
                paths[start_direction] = (target2,target_direction,weight)    
                self.map[start2] = paths #should work properly
            #else would be pointless since on every node theres only one path in each direction

        else:
                paths = {start_direction : (target2,target_direction,weight)}
                self.map[start2] = paths #should work properly 
        #basically the same as above, just reversed bc it is supposed to add a bidirectional path

        if target2 in self.map:
            if start_direction not in self.map[target2]:
                paths = self.map[target2] 
                paths[target_direction] = (start2,start_direction,weight)
                self.map[target2] = paths 
        else:
            paths = {target_direction : (start2,start_direction,weight)}
            self.map[target2] = paths
        

        if start2 == target2:
            paths = self.map[target2]
            paths[target_direction] = (start2,start_direction,weight)    
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

        return self.map #too good to be true ?


    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Union[None, List[Tuple[Tuple[int, int], Direction]]]:
        """
        Returns a shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: 2-Tuple[List, Direction]
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        pass


     
    


#********************-tests-************************************************************

a = Planet()

a.add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
a.add_path(((1, 3), Direction.EAST), ((2, 3), Direction.WEST), 1)


b = a.get_paths()
print(type(b)) #returns dict :)
print(b)