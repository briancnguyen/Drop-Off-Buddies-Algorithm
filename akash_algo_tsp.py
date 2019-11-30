from student_utils import *
from utils import *
import networkx as nx
from collections import defaultdict
from tspy import TSP
import scipy as sp
from tspy.solvers import TwoOpt_solver
import acopy
from JarvisPatrick_init import *

def compute_tour_paths(G, tour):
    rao_tour = []
    for tup in tour:
        path = shortest_path(G,tup[0],tup[1])
        for node in path:
            rao_tour.append(node)
    return rao_tour

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

def solve_tsp(file):
    num_loc, num_houses, list_loc, list_houses, start, adj_matrix, G, location_indices, house_indices, start_index = get_input_data(file)

    def distance(node_1, node_2):
        try:
            return nx.shortest_path_length(G,node_1,node_2,'weight')
        except nx.NetworkXNoPath:
            return 10e100
        except nx.NodeNotFound:
            return 10e100

    def find_centroid(cluster_nodes):
        cluster_dist = []
        for i in range(0,len(cluster_nodes)):
            node_dist = 0
            for j in range(0,len(cluster_nodes)):
                node_dist += distance(cluster_nodes[i],cluster_nodes[j])
            cluster_dist.append(node_dist)
        min_dist = min(cluster_dist)
        return cluster_nodes[cluster_dist.index(min_dist)]

    # Creates list of cluster_centers, these are where we drop drop_off
    # also does pruning to remove useless clusters
    def get_clusters_and_dropoff(clusters_dict):
        centers = []
        center_drop_off = {}
        for key in clusters_dict:
            drop_off = list(set(house_indices) & set(clusters_dict[key]))
            if start_index in clusters_dict[key]:
                centers.append(start_index)
                center_drop_off[start_index] = drop_off
            else:
                if(len(drop_off) == 0):
                    continue
                    center = find_centroid(clusters_dict[key])
                    centers.append(center)
                    center_drop_off[center] = drop_off
        return centers, center_drop_off

    def make_G_prime(cluster_centers):
        G_prime = nx.Graph()
        for node_1 in cluster_centers:
            for node_2 in cluster_centers:
                dist = distance(node_1,node_2)
                if(dist != 10e100):
                    G_prime.add_edge(node_1,node_2, weight=dist)
        return G_prime

    def tsp_solver_1(G_prime, G_prime_nodes, start_index):
        tsp = TSP()
        tsp.read_mat(nx.adjacency_matrix(G_prime).todense())
        two_opt = TwoOpt_solver(initial_tour='NN', iter_num=500)
        two_opt_tour = tsp.get_approx_solution(two_opt)
        best_tour = tsp.get_best_solution()
        center_tour = [G_prime_nodes[node] for node in best_tour]
        if(center_tour.count(start_index) == 1):
            start_loc = center_tour.index(start_index)
            center_tour = center_tour[start_loc:] + center_tour[:start_loc] + [start_index]
        tour = [(center_tour[i],center_tour[i+1]) for i in range(len(center_tour)-1)]
        rao_tour_1 = compute_tour_paths(G, tour)
        rao_tour_1 = [rao_tour_1[i] for i in range(len(rao_tour_1)-1) if rao_tour_1[i] != rao_tour_1[i+1]] + [start_index]
        cost_1 = cost_of_solution(G,rao_tour_1,cluster_center_drop_off)[0]
        return rao_tour_1, cost_1

    jp = JarvisPatrick(location_indices, distance)
    best_cost = 10e1000
    best_rao_tour = []
    best_drop_off = {}
    # k is the number of nearest neighbors around a node to consider
    # s is the number of shared neighbors between u and v for them to be put into 1 cluster
    k_max = int(num_loc/2)
    s_max = int(num_houses/4)
    for k in range(3,k_max):
        for s in range(2,s_max):
            try:
                print("--------")
                print("k=" + str(k) + " k_max=" + str(k_max) + " | " + " s=" + str(s) + " s_max=" + str(s_max))
                clusters_dict = jp(k, s)
                cluster_centers, cluster_center_drop_off = get_clusters_and_dropoff(clusters_dict)

                #G_prime is the graph of clusters
                G_prime = make_G_prime(cluster_centers)
                G_prime_nodes = {i : cluster_centers[i] for i in range(len(cluster_centers))}
                print("Made Graph G_prime ")
                # This the other TSP solver
                rao_tour_1, cost_1 = tsp_solver_1(G_prime,G_prime_nodes,start_index)
                print("**********")
                print("Computed TSP Tour")
                #Comparing Best Solution
                if(cost_1 < best_cost):
                    best_cost = cost_1
                    best_rao_tour = rao_tour_1
                    best_drop_off = cluster_center_drop_off
            except ZeroDivisionError:
                continue
            except ValueError:
                continue
            except OverflowError:
                continue
    return best_rao_tour, best_drop_off
    print("BEST COST: " + str(best_cost))


solve_tsp('inputs/2_100.in')
