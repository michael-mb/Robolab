#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import Enum, unique
from typing import List, Optional, Tuple, Dict
from pprint import pprint


@unique
class Direction(Enum):
    """ Directions in shortcut """
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'


Weight = int

""" 
Weight of a given path (received from the server)!!!

Value:  -1 if blocked path
        >0 for all other paths
        never 0
"""


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """
    ls = []
    currentPos = (-999, -999)
    def __init__(self):
        """ Initializes the data structure """
        self.my_planet = {}
        self.my_planet_copy = {}
        self.empty_Planet = {}
        self.depth_first_list = []
        self.dijkstra_map = {}
        self.distances_to_compare = []
        self.discovered_notes = []
        self.nodes_from_server = []
        self.visited_nodes = []

        self.no_visited_paths = {}
        self.node_list = []

    ################################################################################################################ Start of exploration algorithm

    def get_next_unvisited_node(self):
        for e in self.my_planet:
            if e not in self.visited_nodes:
               # print('get_next_unvisited_node',e)
                return e
            else:
                d = None
        return d

    def add_no_visited_paths(self, currentPosition, allDirection):
        if currentPosition not in self.no_visited_paths:
            self.no_visited_paths[currentPosition] = list(allDirection)
            for direction in self.my_planet[currentPosition]:
                if direction in self.no_visited_paths[currentPosition]:
                    self.remove_no_visited_path(currentPosition,direction)
            return True
        return False

    def get_no_visited_paths(self):
        return self.no_visited_paths

    def get_no_visited_paths_for_node(self, node):
        return self.no_visited_paths[node]

    def remove_no_visited_path(self, node, direction):
        if node in self.no_visited_paths:
            if direction in self.no_visited_paths[node]: # if direction drin ist
                self.no_visited_paths[node] = list(filter(lambda a: a != direction, self.no_visited_paths[node])) # Wie in A&D
                return True
        return False

    def update_no_visited_paths(self):
        for node in self.my_planet:
            if node in self.no_visited_paths:
                for direction in self.my_planet[node]:
                    self.remove_no_visited_path(node, direction)

    def no_no_visited_paths_left(self):
        for node in self.get_no_visited_paths():
            if self.get_no_visited_paths()[node]:
                return False
        return True

    def get_node_with_undiscovered_paths(self):
        self.node_list = []
        #print("GetNodeWithUndiscoveredPaths; No_Visited_Paths: ",end=" ")
       # pprint(self.no_visited_paths)
        for node in self.my_planet:
            if node not in self.visited_nodes:
                self.node_list.append(node)

        for node in self.no_visited_paths:
            if self.no_visited_paths[node]:
                self.node_list.append(node)

        if not self.node_list:
          #  print("Resulting node_list is empty, returning NONE")
            return None

       # print("Resulting node_list is",self.node_list,"returning",self.node_list[-1])
        return self.node_list[-1]

    ################################################################################################################ End of exploration algorithm

    def planet_is_empty(self):
        if self.empty_Planet == self.my_planet:
            return True
        else:
            return False

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):


        if not start[0] in self.my_planet:
            self.my_planet[start[0]] = {}

        self.my_planet[start[0]][start[1]] = (target[0], target[1], weight)


        if not target[0] in self.my_planet:
            self.my_planet[target[0]] = {}

        self.my_planet[target[0]][target[1]] = (start[0], start[1], weight)
       # print("Start: ", start)
       # print("Target: ", target)

        if start[0] in self.no_visited_paths:
            self.remove_no_visited_path(start[0],start[1])

        if target[0] in self.no_visited_paths:
            self.remove_no_visited_path(target[0],target[1])

        """
         Adds a bidirectional path defined between the start and end coordinates to the map and assigns the weight to it

        Example:
            add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
        :param start: 2-Tuple
        :param target:  2-Tuple
        :param weight: Integer
        :return: void
        """

    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:

        return self.my_planet

    """

        Returns all paths

        Example:
            {
                (0, 3): {
                    Direction.NORTH: ((0, 3), Direction.WEST, 1),
                    Direction.EAST: ((1, 3), Direction.WEST, 2)
                },
                (1, 3): {
                    Direction.WEST: ((0, 3), Direction.EAST, 2),
                    ...
                },
                ...
            }
        :return: Dict
    """
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


    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]):
        #print("PLANET----------->>> ", self.my_planet)

        if target not in self.my_planet:
           # print("Target is not reachable")
            return []

        elif start == target:
           # print("You already reached your destiny")
            return None

        else:

            self.my_planet_copy = self.my_planet.copy()
            self.dijkstra_map = {start: [0, []]}
            result = self.djikstra(start, target)
            #print("Dijkstra-Result to SP-Result",result)
            return result

    def djikstra(self, start: Tuple[int, int], target: Tuple[int, int]):

        # print("1_self.dijkstra_map = ", self.dijkstra_map)

        key = start
        ways_to_go = []

        discovered_notes = []

        # print("2_self.dijkstra_map = ", self.dijkstra_map )

        for direction in Direction:
            if direction in self.my_planet_copy[key]:
                if ((self.my_planet.get(start) or {}).get(direction) or [None])[0] in (start, None):
                    continue
                if self.my_planet[start][direction][2] > 0 and start != target:
                    ways_to_go.append((self.my_planet[key][direction][2], direction, self.my_planet[key][direction][0]))
        # print("3_self.dijkstra_map = ", self.dijkstra_map)

        ways_to_go.sort(key=lambda x: int(x[0]))            # from Kilian
        ways_to_go = ways_to_go[::-1]

        # print("ways_to_go = ", ways_to_go)
        # print("self.dijkstra_map before while = ", self.dijkstra_map)
        # print("\n")

        while(ways_to_go != []):
            #print(ways_to_go)
            a = ways_to_go.pop()

            if not a[2] in self.dijkstra_map:
                self.dijkstra_map[a[2]] = [9999, []]

            # print("while key = ", key)
            # print("while a = ",                           a)
            # print("while a[0] = added_distance = ",                         a[0])
            # print("while self.dijkstra_map =", self.dijkstra_map)
            # print("while self.dijkstra_map[key][0] = distance_previous_note = ",    self.dijkstra_map[key][0])
          #  print("Dijkstra Map:")
          #  print(self.dijkstra_map)
            distance_previous_note_and_added_distance = self.dijkstra_map[key][0] + a[0]
            distance_next_note = self.dijkstra_map[a[2]][0]

            if (distance_next_note >= distance_previous_note_and_added_distance):
                # print("1 if self.dijkstra_map = ", self.dijkstra_map)
                previous_note = key
                new_list = []
                previous_list = []
                new_note = a[2]
                # print("if new_note", new_note)

                direction = a[1]
                self.dijkstra_map[new_note][0] = distance_previous_note_and_added_distance
                # print("2 if self.dijkstra_map = ", self.dijkstra_map)
                previous_list = self.dijkstra_map[previous_note][1]
                new_list = previous_list.copy()
                # print("new_list = ", new_list)
                new_list.append((previous_note, direction))
                # print("new_list = ", new_list)
                # print("3 if self.dijkstra_map = ", self.dijkstra_map)
                # print("if new_note", new_note)
                self.dijkstra_map[new_note][1] = new_list
                # print("4 if self.dijkstra_map = ", self.dijkstra_map)
                # print("if distance_privious_note_and_added_distance =", distance_previous_note_and_added_distance)
                # print("1 self.distances_to_compare = ", self.distances_to_compare)
                if not new_note in discovered_notes and new_note != target:
                    # print("2 self.distances_to_compare = ", self.distances_to_compare)
                    node_to_delete = [item for item in self.distances_to_compare if new_note in item]
                    # print("node to delete = ", node_to_delete)

                    if node_to_delete != []:
                        self.distances_to_compare.remove(node_to_delete[0])
                        # print("4 self.distances_to_compare = ", self.distances_to_compare)

                    self.distances_to_compare.append((distance_previous_note_and_added_distance, new_note))
                    # print("5 self.distances_to_compare = ", self.distances_to_compare)
                # print("if distances_to_compare = ", self.distances_to_compare )
                # print("if key =", key)
                # print("if destination = ", new_note)
                # print("if direction = ", direction)
                # print("5 if self.dijkstra_map = ", self.dijkstra_map)
                if new_note == target:
                    # print("self.dijkstra_map[new_note] = ", self.dijkstra_map[new_note])
                    # print(self.dijkstra_map)
                    list_to_print = self.dijkstra_map[new_note][1]
                   # print("pre-reverse return",list_to_print)
                    #list_to_print = list_to_print[::-1]
                    #print("dijkstra_return",list_to_print[-1][1])
                    return list_to_print

                direction_arrive = self.my_planet[key][direction][1]
                # print("while_after_if direction_arrive = ", direction_arrive)
                # print("\n")
                if direction_arrive in self.my_planet_copy[new_note]:
                    self.my_planet_copy[new_note].pop(direction_arrive)

        # self.discovered_notes[key] = 0
        # print("after while discovered_notes = ", self.discovered_notes)

        self.distances_to_compare.sort()
        self.distances_to_compare = self.distances_to_compare[::-1]

        if self.distances_to_compare:
            new_key = self.distances_to_compare.pop()[1]
            return self.djikstra(new_key, target)
