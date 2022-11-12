# Congestion_game
- compute a Nash equilibrium of a congestion game

# Steps:
- The first step is extract all the information from the input file `load_game`
  - to make sure the function can precisely extract all the information, the function uses the string `split` method and `strp` method.
- The second step is generate all possible paths for each player and its travel requirments
  - this is acheived by a simple recurrsive function `printAllPathsUtil`
- The third step is calculate a nash equilibrium, below is the general idea of the function
  - before we start calculate the cost of the possible routes of each player, we need to check the number of players on each edge so that we can get a accurate number
  - then we can start calculate cost of each route by `route_cost_calculation`. The idea is for each edge in the route, we increase the number of players on that route and then calculate the cost by `num_of_edge * linear rate + flat rate`. After that we need to return the number to the original one because we need to calculate the cost of next possible route of the player, which will have different combinations of edges.
  - Then, whenever the cost of a new route is lower than the current route, the player will change its route and also set the signal to be false.
  - The `while` loop will iterate until no player can decrease its cost by change to another route, which is also ther requirement of a nash equilibrium
- Finally, we find a nash equibrium successfully