from student_utils import *
from utils import *
from useful_func import *
import networkx as nx
import scipy as sp
import acopy
from JarvisPatrick_init import *

#USed http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.96.6751&rep=rep1&type=pdf for ant colony hyperparam

def solve_antcolony(file,k,s):
    num_loc, num_houses, list_loc, list_houses, start, adj_matrix, G, location_indices, house_indices, start_index = get_input_data(file)

    F_W_dict = nx.floyd_warshall(G)

    def faster_cost_soln(rao_tour, drop_off):
        rao_cost = 0
        walk_cost = 0
        for i in range(len(rao_tour)-1):
            rao_cost += F_W_dict[rao_tour[i]][rao_tour[i+1]]
        for key in drop_off:
            for target in drop_off[key]:
                walk_cost += F_W_dict[key][target]
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


    def antcolony_solver(G_prime, start_index, cluster_center_drop_off):
        #alpha = how much pheromone matters #beta = how much distance matters
        colony = acopy.Colony(alpha=0.6, beta=6)
        solver = acopy.Solver(rho=.6, q=1)
        ant_tour = solver.solve(G_prime, colony, limit=10)
        ant_tour_nodes = ant_tour.nodes
        cost = ant_tour.cost
        if(ant_tour_nodes.count(start_index)==1):
            ant_start = ant_tour_nodes.index(start_index)
            ant_tour_nodes = ant_tour_nodes[ant_start:] + ant_tour_nodes[:ant_start] + [start_index]
        tour_ant = [(ant_tour_nodes[i],ant_tour_nodes[i+1]) for i in range(len(ant_tour_nodes)-1)]
        rao_tour_2 = compute_tour_paths(G, tour_ant)
        rao_tour_2 = [rao_tour_2[i] for i in range(len(rao_tour_2)-1) if rao_tour_2[i] != rao_tour_2[i+1]] + [start_index]
        cost = faster_cost_soln(rao_tour_2, cluster_center_drop_off)
        return rao_tour_2, cost

    jp = JarvisPatrick(location_indices, distance)
    best_cost = 10e1000
    best_rao_tour = []
    best_drop_off = {}
    # k is the number of nearest neighbors around a node to consider
    try:
        clusters_dict = jp(k, s)
        cluster_centers, cluster_center_drop_off = get_clusters_and_dropoff(clusters_dict)
        print("Clusters found")
        if(len(cluster_center_drop_off) > 1):
            useless_count = 0
            #G_prime is the graph of clusters
            G_prime = make_G_prime(cluster_centers)
            print("Made Graph G_prime")
            #Ant colony technique
            rao_tour, cost = antcolony_solver(G_prime, start_index, cluster_center_drop_off)
            print("** Computed Ant Colony Tour **")
            best_cost, best_rao_tour, best_drop_off = compare_cost(best_cost,best_rao_tour,best_drop_off,k,s,
            cost,rao_tour,cluster_center_drop_off,k,s)

        else:
            soda_drop_flag = True
            rao_tour = [start_index]
            cost = faster_cost_soln(rao_tour,cluster_center_drop_off)
            best_cost, best_rao_tour, best_drop_off = compare_cost(best_cost, best_rao_tour, best_drop_off,k,s,
            cost, rao_tour, cluster_center_drop_off,k,s)
                # except ZeroDivisionError:
                #     continue
    except ValueError:
        print("VAL ERROR")
                # except OverflowError:
                #     continue

    #return best_rao_tour, best_drop_off
    print(best_cost)
k = 3
s= 2
solve_antcolony('inputs/2_200.in',k,s)
