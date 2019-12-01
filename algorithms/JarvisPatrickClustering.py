from collections import defaultdict

# Imported JarvisPatrick init.py file because there is a bug in the code
class JarvisPatrickClustering:
    def __init__(self, dataset_elements, distance_function):
        # Initially each element is a cluster of 1 element
        self.dataset_elements = dataset_elements
        self.distance_function = distance_function
        
    def __call__(self, number_of_neighbors, threshold_number_of_common_neighbors):
        self.cluster = {element: cluster_index for cluster_index, element in enumerate(self.dataset_elements)}
        if threshold_number_of_common_neighbors > number_of_neighbors:
            raise ValueError('Asked for more common neighbors than number of neighbors')
        neighbors_list = {}
        for element in self.dataset_elements:
            neighbors_list[element] = self.calculate_k_nearest_elements(element, number_of_neighbors)[:number_of_neighbors]
        for element, neighbors in neighbors_list.items():
            for other_element, other_neighbors in neighbors_list.items():
                if element != other_element:
                    # We check both sides since the relation is not symmetric
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
            # We keep the lowest index
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
