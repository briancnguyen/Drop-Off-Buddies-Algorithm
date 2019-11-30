from student_utils import *
from utils import *
import networkx as nx
from collections import defaultdict
from tspy import TSP
import scipy as sp
from tspy.solvers import TwoOpt_solver

# Imported JarvisPatrick init.py file b/c there is a bug that i needed to fix
class JarvisPatrick(object):

    def __init__(self, dataset_elements, distance_function):
        self.dataset_elements = dataset_elements
        self.distance_function = distance_function
        # initially each element is a cluster of 1 element

    def __call__(self, number_of_neighbors, threshold_number_of_common_neighbors):
        """
        """
        self.cluster = {element: cluster_index for cluster_index, element in enumerate(self.dataset_elements)}
        if threshold_number_of_common_neighbors > number_of_neighbors:
            raise ValueError('Asked for more common neighbors than number of neighbors')
        neighbors_list = {}
        for element in self.dataset_elements:
            neighbors_list[element] = self.calculate_k_nearest_elements(element, number_of_neighbors)[:number_of_neighbors]
        for element, neighbors in neighbors_list.items():
            for other_element, other_neighbors in neighbors_list.items():
                if element != other_element:
                    # we check both sides since the relation is not symmetric
                    if element in other_neighbors and other_element in neighbors:
                        number_of_common_neighbors = len(set(neighbors).intersection(other_neighbors))
                        if number_of_common_neighbors >= threshold_number_of_common_neighbors:
                            self.reconfigure_clusters(element, other_element)
        result = defaultdict(list)
        for element, cluster_nro in self.cluster.items():
            result[cluster_nro].append(element)

        return result

    def reconfigure_clusters(self, element, other_element):
        if self.cluster[element] != self.cluster[other_element]:
            # we keep the lowest index
            if self.cluster[other_element] > self.cluster[element]:
                for cluster_element in self.dataset_elements:
                    if cluster_element != other_element and self.cluster[cluster_element] == self.cluster[other_element]:
                        self.cluster[cluster_element] = self.cluster[element]
                self.cluster[other_element] = self.cluster[element]
            else:
                for cluster_element in self.dataset_elements:
                    if cluster_element != element and self.cluster[cluster_element] == self.cluster[element]:
                        self.cluster[cluster_element] = self.cluster[other_element]
                self.cluster[element] = self.cluster[other_element]

    def calculate_k_nearest_elements(self, element, k_value):
        res = []
        for neighbor in self.dataset_elements:
            if neighbor == element:
                continue
            distance = self.distance_function(element, neighbor)
            if distance < 0:
                raise Exception('Distance function must return positive number')
            res.append((neighbor, distance))
        res = sorted(res, key=lambda neighbor_tuple: neighbor_tuple[1])
        return [element] + list(map(lambda element: element[0], res))

def main():
    input_data = read_file('inputs/2_50.in')
    num_loc, num_houses, list_loc, list_houses, start, adj_matrix = data_parser(input_data)
    G = adjacency_matrix_to_graph(adj_matrix)[0]
    location_indices = convert_locations_to_indices(list_loc,list_loc)
    house_indices = convert_locations_to_indices(list_houses,list_loc)
    start_index = list_loc.index(start)
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
    for k in range(1,int(num_loc/2)):
        for s in range(2,int(num_loc/5)):
            try:
                clusters_dict = jp(k, s)
                cluster_centers = []
                cluster_center_drop_off = {}
                for key in clusters_dict:
                    drop_off = list(set(house_indices) & set(clusters_dict[key]))
                    if start_index in clusters_dict[key]:
                        cluster_centers.append(start_index)
                        cluster_center_drop_off[start_index] = drop_off
                    else:
                        center = find_centroid(clusters_dict[key])
                        cluster_centers.append(center)
                        cluster_center_drop_off[center] = drop_off
                G_prime = nx.Graph()
                for node_1 in cluster_centers:
                    for node_2 in cluster_centers:
                        dist = distance(node_1,node_2)
                        if(dist != 10e100):
                            G_prime.add_edge(node_1,node_2, weight=dist)
                G_prime_nodes = {i : cluster_centers[i] for i in range(len(cluster_centers))}
                tsp = TSP()
                tsp.read_mat(nx.adjacency_matrix(G_prime).todense())
                two_opt = TwoOpt_solver(initial_tour='NN', iter_num=2000)
                two_opt_tour = tsp.get_approx_solution(two_opt)
                best_tour = tsp.get_best_solution()
                center_tour = [G_prime_nodes[node] for node in best_tour]
                if(center_tour.count(start_index) == 1):
                    start_loc = center_tour.index(start_index)
                    center_tour = center_tour[start_loc:] + center_tour[:start_loc] + [start_index]
                tour = [(center_tour[i],center_tour[i+1]) for i in range(len(center_tour)-1)]
                rao_tour = []
                for tup in tour:
                    path = shortest_path(G,tup[0],tup[1])
                    for node in path:
                        rao_tour.append(node)
                rao_tour = [rao_tour[i] for i in range(len(rao_tour)-1) if rao_tour[i] != rao_tour[i+1]] + [start_index]
                cost = cost_of_solution(G,rao_tour,cluster_center_drop_off)[0]
                if(cost < best_cost):
                    best_cost = cost
                    best_rao_tour = rao_tour
                    best_drop_off = cluster_center_drop_off
            except ValueError:
                continue
            except OverflowError:
                continue
    print(best_cost)
main()
