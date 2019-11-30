import numpy as np
import random
 #Used https://towardsdatascience.com/evolution-of-a-salesman-a-complete-genetic-algorithm-tutorial-for-python-6fe5d2b3ca35

num_loc, num_houses, list_loc, list_houses, start, adj_matrix = data_parser(input_data#INPUT!!!)
G = nx.adjacency_matrix_to_graph(adj_matrix)
location_indices = convert_locations_to_indices(list_loc,list_loc)
house_indices = convert_locations_to_indices(list_houses,list_loc)
start_index = convert_locations_to_indices([start],list_loc)
