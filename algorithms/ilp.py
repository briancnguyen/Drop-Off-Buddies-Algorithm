from utils import read_file
from student_utils import data_parser, adjacency_matrix_to_graph, convert_locations_to_indices
import gurobipy as grb
import networkx as nx
import numpy as np

"""A class that performs data preprocessing and integer linear programming"""
class ILP:
    def __init__(self, num_of_locations, num_houses, list_of_locations, list_of_houses, starting_car_location, adjacency_matrix):
        self.number_of_locations = num_of_locations
        self.number_of_homes = num_houses
        self.list_of_locations = list_of_locations 
        self.list_of_houses = list_of_houses 
        self.starting_car_location = starting_car_location
        self.adjacency_matrix = adjacency_matrix
        self.G = adjacency_matrix_to_graph(self.adjacency_matrix)[0]
            
    def __arrangement_matrix(self):
        arrangement_matrix = []
        for r in range(self.number_of_locations):
            row = []
            for c in range(self.number_of_homes + 2):
                row.append(self.model.addVar(vtype=grb.GRB.BINARY, name="A_" + str(r) + "_" + str(c)))
                self.model.update()
            arrangement_matrix.append(row)
        return np.array(arrangement_matrix)
        
    def __arrangement_constraints(self):
        # Get the index number of where Soda is
        soda = self.list_of_locations.index(self.starting_car_location)
        # Check that we start at Soda
        self.model.addConstr(self.arrangement_matrix[soda][0] == 1)
        # Check that we end at Soda
        self.model.addConstr(self.arrangement_matrix[soda][self.number_of_homes + 1] == 1)
        # Check that each column of arrangement_matrix sums up to 1
        for c in range(self.arrangement_matrix.shape[1]):
            self.model.addConstr(grb.quicksum(self.arrangement_matrix[:, c]) == 1)
            
    def __walking_matrix(self):
        walking_matrix = []
        for r in range(self.number_of_locations):
            row = []
            for c in range(self.number_of_locations):
                row.append(self.model.addVar(vtype=grb.GRB.BINARY, name="W_" + str(r) + "_" + str(c)))
                self.model.update()
            walking_matrix.append(row)
        return np.array(walking_matrix)
        
    def __walking_constraints(self):
        # Boolean array of whether or not a location is a home by index
        H = (np.array(convert_locations_to_indices(self.list_of_locations, self.list_of_houses)) != None).astype(int)
        # Check that each column i of walking_matrix sums up to H[i]
        for i in range(self.walking_matrix.shape[1]):
            self.model.addConstr(grb.quicksum(self.walking_matrix[:, i]) == H[i])
        # Check that we matched correct homes
        for vertex in range(len(self.walking_matrix)):
            self.model.addConstr(grb.quicksum(self.walking_matrix[vertex, :]) == grb.quicksum(self.arrangement_matrix[vertex, 1:self.arrangement_matrix.shape[1] - 1]))
            
    def __cost_function(self):
        """ Driving Cost Function """
        distances = nx.floyd_warshall_numpy(self.G)
        driving_cost_function = []
        for c in range(self.number_of_homes + 1):
            summation = []
            for i in range(self.number_of_locations):
                for j in range(self.number_of_locations):
                    summation.append(grb.QuadExpr(self.arrangement_matrix[i][c] * distances.item((i, j)) * self.arrangement_matrix[j][c + 1]))
                    self.model.update()
            driving_cost_function.append(grb.quicksum(summation))
            
        """ Walking Cost Function """
        walking_cost_function = []
        for row in range(self.number_of_locations):
            for col in range(self.number_of_locations):
                walking_cost_function.append(grb.LinExpr(self.walking_matrix[row][col] * distances.item((row, col))))
                self.model.update()

        """ Set Objective Function """
        cost_function = driving_cost_function + walking_cost_function
        self.model.setObjective(grb.quicksum(cost_function), grb.GRB.MINIMIZE)

    def __optimal_A(self):
        A = []
        for v in self.model.getVars():
            if v.VarName[0] == 'A':
                A.append(v.x)
        return np.array(A).reshape((self.number_of_locations, self.number_of_homes + 2))
    
    def __optimal_W(self):
        W = []
        for v in self.model.getVars():
            if v.VarName[0] == 'W':
                W.append(v.x)
        return np.array(W).reshape((self.number_of_locations, self.number_of_locations))

    def __car_path(self):
        def path_compression(path):
            locations = []
            previous = None
            for location in path:
                if location != previous:
                    locations.append(location)
                previous = location
            return locations
        path, A = [], self.__optimal_A()
        for c in range(A.shape[1]):
            drop_off_vertex = np.where(A[:, c] == 1)[0][0]
            path.append(drop_off_vertex)
        return path_compression(path)

    def __drop_offs(self):
        TAs, D, W, homes_set = [], {}, self.__optimal_W(), set(self.list_of_houses)
        for node in range(self.number_of_locations):
            if self.list_of_locations[node] in homes_set:
                TAs.append(node)
        for node in TAs:
            drop_off_vertex = np.where(W[:, node] == 1)[0][0]
            if drop_off_vertex not in D:
                D[drop_off_vertex] = [node,]
            else:
                D.get(drop_off_vertex).append(node)
        return D

    def solve(self):
        self.model = grb.Model()
        self.arrangement_matrix = self.__arrangement_matrix()
        self.walking_matrix = self.__walking_matrix()
        self.__arrangement_constraints()
        self.__walking_constraints()
        self.__cost_function()
        self.model.optimize()
        return self.__car_path(), self.__drop_offs()
    