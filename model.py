import os
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Set

import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


class CongestionGame:

    # initialize
    def __init__(self):
        self.node = set()
        self.edge = defaultdict(list)  # will generate key for dictionary if empty when trying to append
        self.cost = {}  # cost function
        self.num_edge = {}  # number of players on edge
        self.num_players = None  # number of players in game

        # construct start and end points for each player
        self.source = {}
        self.destination = {}
        self.s_num = None
        
    # set number of players
    def set_player(self, value):
        self.num_players = value
        for i in range(self.num_players):
            self.source[i] = None
            self.destination[i] = None
            pass
    
    # add node
    def add_node(self, value):
        self.node.add(value)

    # set start and end nodes
    def add_path(self, player, source, destination):
        self.source[player] = source
        self.destination[player] = destination

    # add edge (assumes edges are 1-directional)
    def add_edge(self, from_node, to_node, linear_rate, flat_rate):
        self.edge[from_node].append(to_node)
        self.cost[(from_node, to_node)] = linear_rate * self.num_edge + flat_rate
        self.num_edge[(from_node, to_node)] = None

    # find the vertex with minimum cost from source, from the set of
    # vertices not yet included in shortest path tree. Determines which
    # branch to explore next
    @staticmethod
    def __min_cost(cost, node_set):
        # initialize minimum cost for next node
        min_cost = float('inf')
        min_node = None

        # search vertex not in the shortest path tree
        for u in node_set:
            if cost[u] < min_cost:
                min_cost = cost[u]
                min_node = u

        # return index for minimum vertex
        return min_node, min_cost
    
        # Dijkstra's algorithm
    def __dijkstra(self):
        # dynamic node set
        node_set = set(self.node)

        # pre-allocate cost and visit_log
        cost_log = {}
        visit_log = {}
        for node in node_set:
            cost_log[node] = float('inf')

        # initialize starting node
        cost_log[self.start_node] = 0

        while node_set:
            # find node with minimum cost
            min_node, min_cost = self.__min_cost(cost_log, node_set)

            # remove minimum node from set
            node_set.remove(min_node)

            # check if we're at end_node
            if min_node is self.end_node:
                break

            # loop over neighbors that are still in node_set
            for neighbor in self.edge[min_node]:
                if neighbor in node_set:
                    # +1 to cost to account for current player
                    alt = min_cost + self.cost[(min_node, neighbor)](self.num_edge[(min_node, neighbor)] + 1)

                    if alt < cost_log[neighbor]:
                        cost_log[neighbor] = alt
                        visit_log[neighbor] = min_node

        # re-construct path
        path = [self.end_node]
        node = self.end_node
        while True:
            # iterate backwards through visit_log
            node = visit_log[node]

            # insert node to front
            path.insert(0, node)

            # update number of players on path
            self.num_edge[(path[0], path[1])] += 1
            self.num_edge[(path[1], path[0])] += 1

            # exit if at starting node
            if node is self.start_node:
                break

        total_cost = cost_log[self.end_node]
        return path, total_cost

    def nash(self, num_players=None):
        if num_players is None:
            num_players = self.num_players

        # reset number of players on edge to 0
        for key in self.num_edge:
            self.num_edge[key] = 0

        # compute Nash through sequential dijkstra best response calculations
        path_pp = []  # path per player
        for _ in range(num_players):
            path = self.__dijkstra()[0]
            path_pp.append(path)

        # sum up cost to each player after all players have played
        cost_pp = []  # cost per player
        for path in path_pp:
            total_cost = 0
            for idx, node in enumerate(path):
                if node is not path[-1]:
                    num_on_edge = self.num_edge[(path[idx], path[idx + 1])]
                    total_cost += self.cost[(path[idx], path[idx + 1])](num_on_edge)
                else:
                    cost_pp.append(total_cost)

        return cost_pp, path_pp

def load_game(filename, prob=CongestionGame):
    '''
    Loads a roster saved in the specified file.
    '''
    with open(filename, 'r') as f:
        lines = f.readlines()
        print(lines)
        # index represent the position of the player
        i = 0
        # read cost function and travel requirement
        for line in lines:
            list_of_line = list(line)
            # if the start of the line is '(', this is the cost function
            if list_of_line[0] == '(':
                prob.add_edge(list_of_line[1], list_of_line[4], list_of_line[8], list_of_line[11])
                pass
            #else if the start of the line is 'p', this is a path
            else:
                prob.add_path(0, list_of_line[9], list_of_line[12])
                i += 1
                pass
            pass
        pass
    pass

def save_nash(roster, dir='.'):
    '''
    Saves the specified roster in the specified directory.  
    The filename is the time when the roster is saved.
    '''
    # Create a file based on the current time
    filename = os.path.join(dir,re.subn(':|-','_',str(datetime.now()))[0] + ".rost")
    with open(filename,'w') as f:
        for line in roster:
            f.write(line)
            if not line.endswith('\n'):
                f.write('\n')