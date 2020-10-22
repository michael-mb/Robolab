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
        self.planet.add_path(((0, 1), Direction.WEST), ((0, 0), Direction.WEST), 1)
        self.planet.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        self.planet.add_path(((1, 0), Direction.NORTH), ((2, 2), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.NORTH), ((0, 2), Direction.SOUTH), 1)
        self.planet.add_path(((0, 2), Direction.EAST), ((2, 2), Direction.WEST), 1)
        self.planet.add_path(((0, 2), Direction.NORTH), ((0, 3), Direction.SOUTH), 1)
        self.planet.add_path(((0, 3), Direction.EAST), ((2, 2), Direction.NORTH,), 1)
        self.planet.add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)



    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """

        self.assertIsNone(self.planet.shortest_path((0, 0), (0, 1)))
        for key,val in self.planet.dijkstra_map.items():
            print(key, '=>',val)
        # self.planet.transform_map()




class RoboLabPlanetTests(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like):

            +------ /
            /       /
            /       /
            -1,2--- +
            /
            /
            -1,1--- 0,1*---  +
            /       /       /
            /       /       /
            -1,0*--- 0,0* --- 1,0*

        """
        # Initialize your data structure here
        self.planet = Planet()
        self.planet.add_path(((-1, 0), Direction.EAST), ((0, 0), Direction.WEST), 2)
        self.planet.add_path(((-1, 0), Direction.NORTH), ((-1, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 4)
        self.planet.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        self.planet.add_path(((1, 0), Direction.NORTH), ((0, 1), Direction.EAST), 2)
        self.planet.add_path(((0, 1), Direction.WEST), ((-1, 1), Direction.EAST), 1)
        self.planet.add_path(((-1, 1), Direction.NORTH), ((-1, 2), Direction.SOUTH), 1)
        self.planet.add_path(((-1, 2), Direction.NORTH), ((-1, 2), Direction.EAST), 4)

        # self.planet.add_path(...)

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """

        self.assertEqual(self.planet.get_paths(), {(-1, 0): {Direction.EAST: ((0, 0), Direction.WEST, 2),
                                                             Direction.NORTH: ((-1, 1), Direction.SOUTH, 1)},
                                                   (-1, 1): {Direction.SOUTH: ((-1, 0), Direction.NORTH, 1),
                                                             Direction.EAST: ((0, 1), Direction.WEST, 1),
                                                             Direction.NORTH: ((-1, 2), Direction.SOUTH, 1)},
                                                   (-1, 2): {Direction.SOUTH: ((-1, 1), Direction.NORTH, 1),
                                                             Direction.EAST: ((-1, 2), Direction.NORTH, 4),
                                                             Direction.NORTH: ((-1, 2), Direction.EAST, 4)},
                                                   (0, 0): {Direction.WEST: ((-1, 0), Direction.EAST, 2),
                                                            Direction.NORTH: ((0, 1), Direction.SOUTH, 4),
                                                            Direction.EAST: ((1, 0), Direction.WEST, 1)},
                                                   (0, 1): {Direction.SOUTH: ((0, 0), Direction.NORTH, 4),
                                                            Direction.EAST: ((1, 0), Direction.NORTH, 2),
                                                            Direction.WEST: ((-1, 1), Direction.EAST, 1)},
                                                   (1, 0): {Direction.WEST: ((0, 0), Direction.EAST, 1),
                                                            Direction.NORTH: ((0, 1), Direction.EAST, 2)}})

    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        print(self.planet.my_planet[(1, 0)][Direction.WEST])
        self.planet.planet_is_empty()

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        self.planet.shortest_path((-1, 0), (0, 1))

    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))
        self.planet.shortest_path((-1, 2), (1, 0))


    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented also can return alternatives with the
        same cost (weights)

        Requirement: Minimum of two paths with same cost in list returned
        """
        self.fail('implement me!')

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """

        self.assertIsNone(self.planet.shortest_path((0, 0), (0, 1)))

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))


if __name__ == "__main__":
    unittest.main()
