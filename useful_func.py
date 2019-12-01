import networkx as nx
from student_utils import *
from utils import *

def compute_tour_paths(G, tour):
    rao_tour = []
    for tup in tour:
        path = shortest_path(G,tup[0],tup[1])
        for node in path:
            rao_tour.append(node)
    return rao_tour

def compare_cost(best_cost, best_tour, best_drop_off, best_k, best_s, curr_cost, curr_tour, curr_drop_off,k , s):
    #Comparing Best Solution
    ret_cost = best_cost
    ret_tour = best_tour
    ret_drop = best_drop_off
    ret_k = best_k
    ret_s = best_s
    if(curr_cost < best_cost):
        ret_cost = curr_cost
        ret_tour = curr_tour
        ret_drop = curr_drop_off
        ret_k = k
        ret_s = s
    return ret_cost, ret_tour, ret_drop, ret_k , ret_s

def shortest_path(G, node_1, node_2):
    try:
        return nx.shortest_path(G,node_1,node_2,'weight')
    except nx.NetworkXNoPath:
        return None
    except nx.NodeNotFound:
        return None

def get_input_data(file):
    input_data = read_file(file)
    num_loc, num_houses, list_loc, list_houses, start, adj_matrix = data_parser(input_data)
    G = adjacency_matrix_to_graph(adj_matrix)[0]
    location_indices = convert_locations_to_indices(list_loc,list_loc)
    house_indices = convert_locations_to_indices(list_houses,list_loc)
    start_index = list_loc.index(start)
    return num_loc, num_houses, list_loc, list_houses, start, adj_matrix, G, location_indices, house_indices, start_index
