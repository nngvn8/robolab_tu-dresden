    #!/usr/bin/env python3

import unittest
from planet import Direction, Planet


class ExampleTestPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        +--+
        |  |
        +-0,3------+
           |       |
          0,2-----2,2 (target)
           |      /
        +-0,1    /
        |  |    /
        +-0,0-1,0
           |
        (start)

        """
        # Initialize your data structure here
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.WEST), ((0, 0), Direction.WEST), 3)
        self.planet.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        self.planet.add_path(((1,0), Direction.NORTH), ((2, 2), Direction.SOUTH), 3)
        self.planet.add_path(((0, 1), Direction.NORTH), ((0, 2), Direction.SOUTH), 1)
        self.planet.add_path(((0, 2), Direction.NORTH), ((0, 3), Direction.SOUTH), 1)
        self.planet.add_path(((0, 2), Direction.EAST), ((2, 2), Direction.WEST), 4)
        self.planet.add_path(((2, 2), Direction.NORTH), ((0, 3), Direction.EAST), 5)
        self.planet.add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 5)


    @unittest.skip('Example test, should not count in final test results')
    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))


class TestRoboLabPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like):

        """
        # Initialize your data structure here
        self.planet = Planet()
        # self.planet.add_path(...)
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.WEST), ((0, 0), Direction.WEST), 1)
        self.planet.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 3)
        self.planet.add_path(((1, 0), Direction.NORTH), ((2, 2), Direction.SOUTH), 3)
        self.planet.add_path(((0, 1), Direction.NORTH), ((0, 2), Direction.SOUTH), 7)
        self.planet.add_path(((0, 2), Direction.NORTH), ((0, 3), Direction.SOUTH), 1)
        self.planet.add_path(((0, 2), Direction.EAST), ((2, 2), Direction.WEST), 4)
        self.planet.add_path(((2, 2), Direction.NORTH), ((0, 3), Direction.EAST), 5)
        self.planet.add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 5)

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the     expected structure
        """
        paths = {(0, 0): {Direction.NORTH: ((0, 1), Direction.SOUTH, 1), Direction.WEST: ((0, 1), Direction.WEST, 1), Direction.EAST: ((1, 0), Direction.WEST, 3)}, (0, 1): {Direction.SOUTH: ((0, 0), Direction.NORTH, 1), Direction.WEST: ((0, 0), Direction.WEST, 1), Direction.NORTH: ((0, 2), Direction.SOUTH, 7)}, (1, 0): {Direction.WEST: ((0, 0), Direction.EAST, 3), Direction.NORTH: ((2, 2), Direction.SOUTH, 3)}, (2, 2): {Direction.SOUTH: ((1, 0), Direction.NORTH, 3), Direction.WEST: ((0, 2), Direction.EAST, 4), Direction.NORTH: ((0, 3), Direction.EAST, 5)}, (0, 2): {Direction.SOUTH: ((0, 1), Direction.NORTH, 7), Direction.NORTH: ((0, 3), Direction.SOUTH, 1), Direction.EAST: ((2, 2), Direction.WEST, 4)}, (0, 3): {Direction.SOUTH: ((0, 2), Direction.NORTH, 1), Direction.EAST: ((2, 2), Direction.NORTH, 5), Direction.NORTH: ((0, 3), Direction.WEST, 5), Direction.WEST: ((0, 3), Direction.NORTH, 5)}}

        self.assertEqual(paths,self.planet.get_paths())

    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        self.empty_planet = Planet()
        self.assertEqual({},self.empty_planet.get_paths())

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        self.assertEqual(self.planet.shortest_path((0,0),(0,3)),[((0, 0), Direction.NORTH), ((0, 1), Direction.NORTH), ((0, 2), Direction.NORTH)])

    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        self.assertEqual(self.planet.shortest_path((0,0),(5,5)),None)

    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented returns a shortest path even if there
        are multiple shortest paths with the same length.

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """
        self.assertTrue(self.planet.shortest_path((1, 0), (0, 3)) == ([((1, 0), Direction.NORTH), ((2, 2), Direction.WEST),((0, 2), Direction.NORTH)]) or self.planet.shortest_path((1, 0), (0, 3)) == [((1, 0), Direction.NORTH), ((2, 2), Direction.NORTH)])

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable#
        """
        self.assertEqual([((0, 0), Direction.NORTH), ((0, 1), Direction.NORTH), ((0, 2), Direction.NORTH)],self.planet.shortest_path((0,0),(0,3)))

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        new planet:


        """

        self.assertIsNone(self.planet.shortest_path((0, 3), (3, 3)))



if __name__ == "__main__":
    unittest.main()
