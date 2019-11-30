from student_utils import *
from utils import *
import networkx as nx
import scipy as sp
import acopy

def main(file):
    input_data = read_file(file)
    num_loc, num_houses, list_loc, list_houses, start, adj_matrix = data_parser(input_data)
    G = adjacency_matrix_to_graph(adj_matrix)[0]
    location_indices = convert_locations_to_indices(list_loc,list_loc)
    house_indices = convert_locations_to_indices(list_houses,list_loc)
    start_index = list_loc.index(start)

    def compute_tour_paths(tour):
        rao_tour = []
        for tup in tour:
            path = shortest_path(G,tup[0],tup[1])
            for node in path:
                rao_tour.append(node)
        return rao_tour
    #Trying clustering using Jarvis Patrick
    def distance(node_1, node_2):
        try:
            return nx.shortest_path_length(G,node_1,node_2,'weight')
        except nx.NetworkXNoPath:
            return 10e100
        except nx.NodeNotFound:
            return 10e100

    def shortest_path(G, node_1, node_2):
        try:
            return nx.shortest_path(G,node_1,node_2,'weight')
        except nx.NetworkXNoPath:
            return None
        except nx.NodeNotFound:
            return None

    def find_centroid(cluster_nodes):
        cluster_dist = []
        for i in range(0,len(cluster_nodes)):
            node_dist = 0
            for j in range(0,len(cluster_nodes)):
                node_dist += distance(cluster_nodes[i],cluster_nodes[j])
            cluster_dist.append(node_dist)
        min_dist = min(cluster_dist)
        return cluster_nodes[cluster_dist.index(min_dist)]

    jp = JarvisPatrick(location_indices, distance)
    best_cost = 10e1000
    best_rao_tour = []
    best_drop_off = {}
    # k is the number of nearest neighbors around a node to consider
    # s is the number of shared neighbors between u and v for them to be put into 1 cluster
    for k in range(1,int(num_loc/2),5):
        for s in range(2,int(num_houses/4),2):
            try:
                clusters_dict = jp(k, s)
                cluster_centers = []
                cluster_center_drop_off = {}
                # Creates list of cluster_centers, these are where we drop drop_off
                # also does pruning to remove useless clusters
                for key in clusters_dict:
                    drop_off = list(set(house_indices) & set(clusters_dict[key]))
                    if start_index in clusters_dict[key]:
                        cluster_centers.append(start_index)
                        cluster_center_drop_off[start_index] = drop_off
                    else:
                        if(len(drop_off) == 0):
                            continue
                        center = find_centroid(clusters_dict[key])
                        cluster_centers.append(center)
                        cluster_center_drop_off[center] = drop_off

                #G_prime is the graph of clusters
                G_prime = nx.Graph()
                for node_1 in cluster_centers:
                    for node_2 in cluster_centers:
                        dist = distance(node_1,node_2)
                        if(dist != 10e100):
                            G_prime.add_edge(node_1,node_2, weight=dist)
                G_prime_nodes = {i : cluster_centers[i] for i in range(len(cluster_centers))}
                #Ant colony technique
                solver = acopy.Solver(rho=.05, q=1)
                colony = acopy.Colony(alpha=5, beta=10)
                ant_tour = solver.solve(G_prime, colony, limit=100)
                ant_tour_nodes = ant_tour.nodes
                if(ant_tour_nodes.count(start_index)==1):
                    ant_start = ant_tour_nodes.index(start_index)
                    ant_tour_nodes = ant_tour_nodes[ant_start:] + ant_tour_nodes[:ant_start] + [start_index]
                tour_ant = [(ant_tour_nodes[i],ant_tour_nodes[i+1]) for i in range(len(ant_tour_nodes)-1)]
                rao_tour_2 = compute_tour_paths(tour_ant)
                rao_tour_2 = [rao_tour_2[i] for i in range(len(rao_tour_2)-1) if rao_tour_2[i] != rao_tour_2[i+1]] + [start_index]
                # # This the other TSP solver
                # tsp = TSP()
                # tsp.read_mat(nx.adjacency_matrix(G_prime).todense())
                # two_opt = TwoOpt_solver(initial_tour='NN', iter_num=500)
                # two_opt_tour = tsp.get_approx_solution(two_opt)
                # best_tour = tsp.get_best_solution()
                # center_tour = [G_prime_nodes[node] for node in best_tour]
                # if(center_tour.count(start_index) == 1):
                #     start_loc = center_tour.index(start_index)
                #     center_tour = center_tour[start_loc:] + center_tour[:start_loc] + [start_index]
                # tour = [(center_tour[i],center_tour[i+1]) for i in range(len(center_tour)-1)]
                # rao_tour_1 = compute_tour_paths(tour)
                # rao_tour_1 = [rao_tour_1[i] for i in range(len(rao_tour_1)-1) if rao_tour_1[i] != rao_tour_1[i+1]] + [start_index]
                # cost_1 = cost_of_solution(G,rao_tour_1,cluster_center_drop_off)[0]
                cost_2 = cost_of_solution(G,rao_tour_2,cluster_center_drop_off)[0]
                #Comparing Best Solution
                # if(cost_1 < best_cost):
                #     best_cost = cost_1
                #     best_rao_tour = rao_tour_1
                #     best_drop_off = cluster_center_drop_off
                if(cost_2 < best_cost):
                    best_cost = cost_2
                    best_rao_tour = rao_tour_2
                    best_drop_off = cluster_center_drop_off
            except ZeroDivisionError:
                continue
            except ValueError:
                continue
            except OverflowError:
                continue
    print(best_cost)
main('inputs/2_100.in')
