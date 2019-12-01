from student_utils import *
from utils import *
from useful_func import *
import networkx as nx
from collections import defaultdict
from tspy import TSP
import scipy as sp
from tspy.solvers import TwoOpt_solver
import acopy
from JarvisPatrick_init import *

def solve_tsp(file):
    num_loc, num_houses, list_loc, list_houses, start, adj_matrix, G, location_indices, house_indices, start_index = get_input_data(file)

    F_W_dict = nx.floyd_warshall(G)
    def faster_cost_soln(rao_tour, drop_off):
        rao_cost = 0
        walk_cost = 0
        for i in range(len(rao_tour)-1):
            rao_cost += F_W_dict[rao_tour[i]][rao_tour[i+1]]

        for key in drop_off:
            for target in drop_off[key]:
                length = F_W_dict[key][target]
                walk_cost += length

        return (2/3)*rao_cost + walk_cost

    def distance(node_1, node_2):
        return F_W_dict[node_1][node_2]

    def find_centroid(cluster_nodes):
        cluster_dist = []
        for i in range(0,len(cluster_nodes)):
            node_dist = 0
            for j in range(0,len(cluster_nodes)):
                node_dist += distance(cluster_nodes[i],cluster_nodes[j])
            cluster_dist.append(node_dist)
        min_dist = min(cluster_dist)
        return cluster_nodes[cluster_dist.index(min_dist)]


    def make_G_prime(cluster_centers):
        G_prime = nx.Graph()
        for node_1 in cluster_centers:
            for node_2 in cluster_centers:
                if(node_1 == node_2):
                    continue
                else:
                    dist = distance(node_1,node_2)
                    G_prime.add_edge(node_1,node_2, weight=dist)
        return G_prime

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
                if(drop_off == []):
                    continue
                else:
                    center = find_centroid(clusters_dict[key])
                    centers.append(center)
                    center_drop_off[center] = drop_off
        return centers, center_drop_off


    def tsp_solver_1(G_prime, G_prime_nodes, start_index, cluster_center_drop_off):
        tsp = TSP()
        tsp.read_mat(nx.adjacency_matrix(G_prime).todense())
        two_opt = TwoOpt_solver(initial_tour='NN', iter_num=1000)
        best_tour = tsp.get_approx_solution(two_opt)
        center_tour = [G_prime_nodes[node] for node in best_tour]
        if(center_tour.count(start_index) == 1):
            start_loc = center_tour.index(start_index)
            center_tour = center_tour[start_loc:] + center_tour[:start_loc] + [start_index]
        tour = [(center_tour[i],center_tour[i+1]) for i in range(len(center_tour)-1)]
        rao_tour_1 = compute_tour_paths(G, tour)
        rao_tour_1 = [rao_tour_1[i] for i in range(len(rao_tour_1)-1) if rao_tour_1[i] != rao_tour_1[i+1]] + [start_index]
        cost_1 = faster_cost_soln(rao_tour_1,cluster_center_drop_off)
        return rao_tour_1, cost_1


    jp = JarvisPatrick(location_indices, distance)
    best_cost = 10e1000
    best_rao_tour = []
    best_k = 0
    best_drop_off = {}
    best_s = 0
    # k is the number of nearest neighbors around a node to consider
    # s is the number of shared neighbors between u and v for them to be put into 1 cluster
    k_max = num_loc
    s_max = min(30,num_houses/2)
    soda_drop_flag = False
    useless_count = 0
    for k in range(1,k_max):
        for s in range(1,s_max):
            try:
                if(useless_count < int(num_loc/4)):
                    print("--------")
                    print("k=" + str(k) + " k_max=" + str(k_max) + " | " + " s=" + str(s) + " s_max=" + str(s_max))
                    clusters_dict = jp(k, s)
                    cluster_centers, cluster_center_drop_off = get_clusters_and_dropoff(clusters_dict)
                    if(len(cluster_center_drop_off) > 1):
                        useless_count = 0
                        #G_prime is the graph of clusters
                        G_prime = make_G_prime(cluster_centers)
                        G_prime_nodes = {i : cluster_centers[i] for i in range(len(cluster_centers))}
                        print("Made Graph G_prime")
                        #Ant colony technique
                        rao_tour, cost = tsp_solver_1(G_prime,G_prime_nodes, start_index, cluster_center_drop_off)
                        print("** Computed TSP Tour **")
                        best_cost, best_rao_tour, best_drop_off,best_k,best_s = compare_cost(best_cost, best_rao_tour, best_drop_off,best_k,best_s,
                                                                                cost, rao_tour, cluster_center_drop_off,k,s)
                    else:
                        useless_count += 1
                        if(not soda_drop_flag):
                            soda_drop_flag = True
                            rao_tour = [start_index]
                            cost = faster_cost_soln(rao_tour,cluster_center_drop_off)
                            best_cost, best_rao_tour, best_drop_off,best_k,best_s = compare_cost(best_cost, best_rao_tour, best_drop_off,best_k,best_s,
                                                                                    cost, rao_tour, cluster_center_drop_off,k,s)


            # except ZeroDivisionError:
            #     continue
            except ValueError:
                continue
            # except OverflowError:
            #     continue
    #return best_rao_tour, best_drop_off
    print("BEST COST: " + str(best_cost))


solve_tsp('inputs/2_200.in')
