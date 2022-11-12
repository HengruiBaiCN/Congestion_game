import model
import re, os

if __name__ == '__main__':
    # initialise the problem
    prob = model.CongestionGame()
    # add 4 nodes to the game
    prob.add_node('A')
    prob.add_node('B')
    prob.add_node('C')
    prob.add_node('D')
    # set the number of players
    prob.set_player(2)
    
    # extract information from the input file
    model.load_game('game.txt', prob)
    
    model.print_nash(prob)