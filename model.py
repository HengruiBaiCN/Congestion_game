from typing import List, Set, Dict
import re, os
from datetime import datetime
from collections import defaultdict
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
        self.num_players = 0  # number of players in game

        # construct start and end points
        self.start_node = start_node
        self.end_node = end_node
        self.s_num = None
        
    # set number of players
    def set_player(self, value):
        self.num_players = value
    
    # add node
    def add_node(self, value):
        self.node.add(value)

    # set start and end nodes
    def path(self, start_node, end_node):
        self.start_node = start_node
        self.end_node = end_node

    # add edge (assumes edges are bi-directional)
    def add_edge(self, from_node, to_node, cost):
        self.edge[from_node].append(to_node)
        self.edge[to_node].append(from_node)
        self.cost[(from_node, to_node)] = cost
        self.cost[(to_node, from_node)] = cost
        self.num_edge[(from_node, to_node)] = None
        self.num_edge[(to_node, from_node)] = None

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

def load_game(filename):
    '''
    Loads a roster saved in the specified file.
    '''
    with open(filename) as f:
        return f.readlines()

def read_costs(prob=CongestionGame):
    '''
      Reads the cost for each nurse, day, and shift from the cost file.  
      This method first requires you to modify and run `create_costs.py` (you can run that file multiple times).
      The result is a table that indicates the costs for a nurse to work during a shift.  
      For instance, Nurse 5 being scheduled to work during day 16 in the Morning shift 
      induces the cost `read_costs()[5][16%7][SHIFT_MORNING].
      The cost is only defined for the work shift (in other words, the cost for SHIFT_OFFDUTY is 0).
    '''
    cost_list = []
    with open('costs.rcosts') as f:
        line = f.readline()
        cost_list = [ float(f) for f in re.findall('0\.\d*', line)]

    costs = []
    k = 0
    for _i in range(prob._nb_nurses):
        nurse_costs = []
        for _d in range(DAYS_PER_WEEK):
            day_costs = {}
            for shift_type in [SHIFT_AFTERNOON, SHIFT_MORNING, SHIFT_NIGHT]:
                day_costs[shift_type] = cost_list[k]
                k += 1
            nurse_costs.append(day_costs)
        costs.append(nurse_costs)
    return costs