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
        # will generate key for dictionary if empty when trying to append
        self.edge = defaultdict(list)
        self.cost = {}  # cost function
        self.num_edge = {}  # number of players on edge
        self.num_players = 0  # number of players in game

        # construct start and end points for each player
        self.source = {}
        self.destination = {}
        self.routes = {}
        pass

    # set number of players
    def set_player(self, value):
        self.num_players = value
        for i in range(self.num_players):
            self.source[i] = None
            self.destination[i] = None
            self.routes[i] = []
            pass

    # add node
    def add_node(self, value):
        self.node.add(value)
        pass

    # set start and end nodes
    def add_path(self, player, source, destination):
        self.source[player] = source
        self.destination[player] = destination
        pass

    # add edge (assumes edges are 1-directional)
    def add_edge(self, from_node, to_node, linear_rate, flat_rate):
        self.edge[from_node].append(to_node)
        self.edge[to_node].append(from_node)
        self.num_edge[(from_node, to_node)] = 0
        self.num_edge[(to_node, from_node)] = 0
        self.cost[(from_node, to_node)] = [float(linear_rate), float(flat_rate)]
        self.cost[(to_node, from_node)] = [float(linear_rate), float(flat_rate)]
        pass

    # a recurrsive function to find all possible routes
    def printAllPathsUtil(self, u, d, visited, path, player):
        # Mark the current node as visited and store in path
        visited.append(u)
        path.append(u)
        # If current vertex is same as destination, then print
        if u == d:
            route = path.copy()
            self.routes[player].append(route)
            pass
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex
            for i in self.edge[u]:
                if i not in visited:
                    self.printAllPathsUtil(i, d, visited, path, player)
                    pass
                pass
            pass
        # Remove current vertex from path[] and mark it as unvisited
        path.pop()
        visited.remove(u)

    # Prints and save all routes of a player
    def printAllPaths(self, player):
        s = self.source[player]
        d = self.destination[player]
        # Mark all the vertices as not visited and Create an array to store paths
        visited, path = [], []
        # Call the recursive helper function to print all paths
        self.printAllPathsUtil(s, d, visited, path, player)
        pass

    # calculate the cost of a route
    def route_cost_calculation(self, route):
        cost = 0
        for i in range(len(route)-1):
            self.num_edge[(route[i], route[i+1])] += 1
            edge_cost = self.cost[(route[i], route[i+1])][0] * self.num_edge[(
                route[i], route[i+1])] + self.cost[(route[i], route[i+1])][1]
            cost += edge_cost
            # return to the original value
            self.num_edge[(route[i], route[i+1])] -= 1
            pass
        return cost

    # find a nash equilibrium of the problem
    def nash(self):
        # generate all possible routes for each player
        for player in range(self.num_players):
            self.printAllPaths(player)
            pass

        # create a dictionary to save the cost of the route, the route and the status of changing route of a player
        min_cost = {}
        min_route = {}
        flag = {}
        for player in range(self.num_players):
            min_cost[player] = 99999999999999999
            min_route[player] = None
            flag[player] = True
            pass
        
        # flag for the while loop
        new_flag = False

        # find the minimum cost of route of the player
        while not new_flag:
            for player in range(self.num_players):
                # initialise the number of player in each edge to be 0
                for key in self.num_edge.keys():
                    self.num_edge[key] = 0
                    pass
                # check other player's route to calculate the num of player in each edge
                for other_player in range(self.num_players):
                    # if the player has not been given a route yet, skip it
                    # calculate the number of players in each edge
                    if min_route[other_player] != None and other_player != player:
                        for i in range(len(min_route[other_player])-1):
                            self.num_edge[(
                                min_route[other_player][i], min_route[other_player][i+1])] += 1
                            pass
                        pass
                    pass

                # extract the current number of players in each route and save it, create a flag to keep track on whether the route has been changed or not
                player_flag = True
                for route in self.routes[player]:
                    # calculate the cost of the new route
                    new_cost = self.route_cost_calculation(route)
                    last_cost = min_cost[player]
                    # recalculate the cost of the last route of the player
                    if min_route[player] != None:
                        last_cost = self.route_cost_calculation(
                            min_route[player])
                        pass
                    # compare the cost, if the new route has smaller cost, change route, update flag
                    if new_cost < last_cost:
                        min_cost[player] = new_cost
                        min_route[player] = route
                        player_flag = player_flag & False
                        pass
                    # if not, update the flag
                    else:
                        player_flag = player_flag & True
                        pass
                    pass
                # check whether the player has changed route or not 
                flag[player] = player_flag
                pass
            # regenerate flag
            new_flag = True
            for player in range(self.num_players):
                new_flag = new_flag & flag[player]
                pass
            pass
        # print(self.routes)
        return min_route


def load_game(filename, prob=CongestionGame()):
    '''
    Loads a roster saved in the specified file.
    '''
    with open(filename, 'r') as f:
        lines = f.readlines()
        # index represent the position of the player
        i = 0
        # read cost function and travel requirement
        for line in lines:
            list_of_line = line.strip().split(' ')
            # if the length of the line is 4, this is the cost function
            if len(list_of_line) == 4:
                from_node = ''.join(list(list_of_line[0])[1])
                to_node = ''.join(list(list_of_line[1])[0])
                linear = ''.join(list(list_of_line[2])[0:-1])
                flat = ''.join(list(list_of_line[3])[0:-1])
                prob.add_edge(
                    from_node, to_node, linear, flat)
                pass
            # else this is a path
            else:
                prob.add_path(i, list_of_line[1][0], list_of_line[2][0])
                i += 1
                pass
            pass
        pass
    pass


def print_nash(prob=CongestionGame(), dir='.'):
    '''
    Saves the specified roster in the specified directory.
    The filename is the time when the roster is saved.
    '''
    final_route = prob.nash()
    final_cost = {}
    # initialise the number of player in each edge to be 0
    for key in prob.num_edge.keys():
        prob.num_edge[key] = 0
        pass
    # calculate the number of players in each edge
    for player in range(prob.num_players):
        for i in range(len(final_route[player])-1):
            prob.num_edge[(final_route[player][i], final_route[player][i+1])] += 1
            pass
        final_cost[player] = 0
        pass
    # calculate the cost of the route
    for player in range(prob.num_players):
        for i in range(len(final_route[player])-1):
            edge_cost = prob.cost[(final_route[player][i], final_route[player][i+1])][0] * prob.num_edge[(
                final_route[player][i], final_route[player][i+1])] + prob.cost[(final_route[player][i], final_route[player][i+1])][1]
            final_cost[player] += edge_cost
            pass
        pass
    # print the nash equilibrium
    for player in range(prob.num_players):
        print(f"player{player+1}, Cost = {final_cost[player]}: {final_route[player]}")
        pass
    
    