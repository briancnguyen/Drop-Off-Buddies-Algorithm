from student_utils import *
from utils import *
from algorithms.JarvisPatrickClustering import *
from collections import defaultdict
from tspy import TSP
from tspy.solvers import TwoOpt_solver
import networkx as nx
import scipy as sp
import acopy

class Reduction:
    def __init__(self, num_of_locations, num_houses, list_of_locations, list_of_houses, starting_car_location, adjacency_matrix):
        self.number_of_locations = num_of_locations
        self.number_of_homes = num_houses
        self.list_of_locations = list_of_locations
        self.list_of_houses = list_of_houses
        self.starting_car_location = starting_car_location
        self.adjacency_matrix = adjacency_matrix
        self.G = adjacency_matrix_to_graph(self.adjacency_matrix)[0]
        self.F_W_dict = nx.floyd_warshall(self.G)
        self.location_indices = convert_locations_to_indices(self.list_of_locations, self.list_of_locations)
        self.house_indices = convert_locations_to_indices(self.list_of_houses, self.list_of_locations)
        self.start_index = self.list_of_locations.index(self.starting_car_location)
        self.JP = JarvisPatrickClustering(self.location_indices, self.distance)

    def faster_cost_solution(self, rao_tour, drop_off):
        rao_cost = 0
        walk_cost = 0
        for i in range(len(rao_tour) - 1):
            rao_cost += self.F_W_dict[rao_tour[i]][rao_tour[i + 1]]
        for key in drop_off:
            for target in drop_off[key]:
                length = self.F_W_dict[key][target]
                walk_cost += length
        return (2/3) * rao_cost + walk_cost

    def distance(self, node_1, node_2):
        return self.F_W_dict[node_1][node_2]

    def find_centroid(self, cluster_nodes):
        cluster_dist = []
        for i in range(0, len(cluster_nodes)):
            node_dist = 0
            for j in range(0, len(cluster_nodes)):
                node_dist += self.distance(cluster_nodes[i], cluster_nodes[j])
            cluster_dist.append(node_dist)
        min_dist = min(cluster_dist)
        return cluster_nodes[cluster_dist.index(min_dist)]

    def make_G_prime(self, cluster_centers):
        G_prime = nx.Graph()
        for node_1 in cluster_centers:
            for node_2 in cluster_centers:
                if(node_1 == node_2):
                    continue
                else:
                    dist = self.distance(node_1, node_2)
                    G_prime.add_edge(node_1, node_2, weight=dist)
        return G_prime

    # Creates list of cluster_centers, these are where we drop drop_off
    # also does pruning to remove useless clusters
    def get_clusters_and_dropoff(self, clusters_dict):
        centers = []
        center_drop_off = {}
        for key in clusters_dict:
            drop_off = list(set(self.house_indices) & set(clusters_dict[key]))
            if self.start_index in clusters_dict[key]:
                centers.append(self.start_index)
                center_drop_off[self.start_index] = drop_off
            else:
                if drop_off == []:
                    continue
                else:
                    center = self.find_centroid(clusters_dict[key])
                    centers.append(center)
                    center_drop_off[center] = drop_off
        return centers, center_drop_off

    def Two_Opt_solver(self, G_prime, G_prime_nodes, start_index, cluster_center_drop_off):
        tsp = TSP()
        tsp.read_mat(nx.adjacency_matrix(G_prime).todense())
        two_opt = TwoOpt_solver(initial_tour='NN', iter_num=500)
        best_tour = tsp.get_approx_solution(two_opt)
        center_tour = [G_prime_nodes[node] for node in best_tour]
        if(center_tour.count(start_index) == 1):
            start_loc = center_tour.index(start_index)
            center_tour = center_tour[start_loc:] + center_tour[:start_loc] + [start_index]
        tour = [(center_tour[i], center_tour[i+1]) for i in range(len(center_tour) -1 )]
        rao_tour_1 = compute_tour_paths(self.G, tour)
        rao_tour_1 = [rao_tour_1[i] for i in range(len(rao_tour_1) - 1) if rao_tour_1[i] != rao_tour_1[i + 1]] + [start_index]
        cost_1 = self.faster_cost_solution(rao_tour_1, cluster_center_drop_off)
        return rao_tour_1, cost_1

    def Two_Opt_solve(self):
        best_cost = 10e1000
        best_rao_tour = []
        best_drop_off = {}
        best_k = 0
        best_s = 0
        # k is the number of nearest neighbors around a node to consider
        # s is the number of shared neighbors between u and v for them to be put into 1 cluster
        k_max = min(25,int(self.number_of_locations/2))
        k_range = range(1,k_max,3)
        s_max = min(15, int(self.number_of_homes/2))
        s_range = range(1,s_max,3)
        if(self.number_of_locations <= 100):
            k_range = range(1,self.number_of_locations)
            s_max = range(1,20)
        soda_drop_flag = False
        useless_count = 0
        for k in k_range:
            for s in s_range:
                try:
                    if (useless_count < 35):
                        print("--------")
                        print("k=" + str(k) + " k_max=" + str(k_max) + " | " + " s=" + str(s) + " s_max=" + str(s_max))
                        clusters_dict = self.JP(k, s)
                        cluster_centers, cluster_center_drop_off = self.get_clusters_and_dropoff(clusters_dict)
                        if (len(cluster_center_drop_off) > 1):
                            useless_count = 0
                            # G_prime is the graph of clusters
                            G_prime = self.make_G_prime(cluster_centers)
                            G_prime_nodes = {i : cluster_centers[i] for i in range(len(cluster_centers))}
                            print("Made Graph G_prime")
                            # 2-OPT TSP Solver
                            rao_tour, cost = self.Two_Opt_solver(G_prime, G_prime_nodes, self.start_index, cluster_center_drop_off)
                            print("** Computed TSP Tour **")
                            best_cost, best_rao_tour, best_drop_off,best_k,best_s = compare_cost(best_cost, best_rao_tour, best_drop_off,best_k,best_s,
                                                                                cost, rao_tour, cluster_center_drop_off,k,s)
                        else:
                            useless_count += 1
                            if(not soda_drop_flag):
                                soda_drop_flag = True
                                rao_tour = [self.start_index]
                                cost = self.faster_cost_solution(rao_tour, cluster_center_drop_off)
                                best_cost, best_rao_tour, best_drop_off,best_k,best_s = compare_cost(best_cost, best_rao_tour, best_drop_off,best_k,best_s,
                                                                                    cost, rao_tour, cluster_center_drop_off,k,s)
                # except ZeroDivisionError:
                #     continue
                except ValueError:
                    s_max = s
                    continue
                # except OverflowError:
                #     continue
        print("BEST COST: " + str(best_cost))
        return best_rao_tour, best_drop_off, best_k, best_s, best_cost

    # Used http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.96.6751&rep=rep1&type=pdf for ant colony hyperparam
    def Ant_Colony_solver(self, G_prime, start_index, cluster_center_drop_off):
        # alpha = how much pheromone matters
        # beta = how much distance matters
        colony = acopy.Colony(alpha=0.6, beta=6)
        solver = acopy.Solver(rho=.6, q=1)
        ant_tour = solver.solve(G_prime, colony, limit=10)
        ant_tour_nodes = ant_tour.nodes
        cost = ant_tour.cost
        if(ant_tour_nodes.count(start_index)==1):
            ant_start = ant_tour_nodes.index(start_index)
            ant_tour_nodes = ant_tour_nodes[ant_start:] + ant_tour_nodes[:ant_start] + [start_index]
        tour_ant = [(ant_tour_nodes[i],ant_tour_nodes[i+1]) for i in range(len(ant_tour_nodes)-1)]
        rao_tour_2 = compute_tour_paths(self.G, tour_ant)
        rao_tour_2 = [rao_tour_2[i] for i in range(len(rao_tour_2)-1) if rao_tour_2[i] != rao_tour_2[i+1]] + [start_index]
        cost = self.faster_cost_solution(rao_tour_2, cluster_center_drop_off)
        return rao_tour_2, cost

    def Ant_Colony_solve(self, k=5, s=4):
        best_cost = 10e1000
        best_rao_tour = []
        best_k = 0
        best_s = 0
        best_drop_off = {}
        soda_drop_flag = False
        # k is the number of nearest neighbors around a node to consider
        k_max = min(25,int(self.number_of_locations/2))
        k_range = range(1,k_max,3)
        s_max = min(15, int(self.number_of_homes/2))
        s_range = range(1,s_max,3)

        if self.number_of_locations <= 100:
            k_range = range(1, self.number_of_locations)
            s_range = range(1, 20)

        for k in range(1, 50):
            for s in range(1, 20):
                try:
                    clusters_dict = self.JP(k, s)
                    cluster_centers, cluster_center_drop_off = self.get_clusters_and_dropoff(clusters_dict)
                    print("Clusters found")
                    if(len(cluster_center_drop_off) > 1):
                        useless_count = 0
                        # G_prime is the graph of clusters
                        G_prime = self.make_G_prime(cluster_centers)
                        print("Made Graph G_prime")
                        # Ant Colony Technique
                        rao_tour, cost = self.Ant_Colony_solver(G_prime, self.start_index, cluster_center_drop_off)
                        print("COST: " + str(cost))
                        print("BEST COST: " + str(best_cost))
                        print("** Computed Ant Colony Tour **")
                        best_cost, best_rao_tour, best_drop_off, best_k, best_s = compare_cost(best_cost,best_rao_tour,best_drop_off,k,s,
                                                                    cost,rao_tour,cluster_center_drop_off,k,s)
                    else:
                        if not soda_drop_flag:
                            
                            soda_drop_flag = True
                            rao_tour = [self.start_index]
                            cost = self.faster_cost_solution(rao_tour, cluster_center_drop_off)
                            best_cost, best_rao_tour, best_drop_off,best_k, best_s = compare_cost(best_cost, best_rao_tour, best_drop_off,k,s,
                                                                             cost, rao_tour, cluster_center_drop_off,k,s)
                            # except ZeroDivisionError:
                            #     continue
                except ValueError:
                    # print("VAL ERROR")
                    continue
                            # except OverflowError:
                            #     continue
        print("Best Cost", best_cost)
        return best_rao_tour, best_drop_off, best_k, best_s, best_cost
