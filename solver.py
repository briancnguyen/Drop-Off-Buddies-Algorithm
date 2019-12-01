import os
import sys
sys.path.append('..')
sys.path.append('../..')
import argparse
import utils

from student_utils import *
#from algorithms.ilp import *
from algorithms.reduction import *


def solve(input_file, num_of_locations, num_houses, list_of_locations, list_of_houses, starting_car_location, adjacency_matrix, params=[]):
    """
    Input:
        list_of_locations: A list of locations such that node i of the graph corresponds to name at index i of the list
        list_of_homes: A list of homes
        starting_car_location: The name of the starting location for the car
        adjacency_matrix: The adjacency matrix from the input file
    Output:
        A list of locations representing the car path
        A dictionary mapping drop-off location to a list of homes of TAs that got off at that particular location
        NOTE: both outputs should be in terms of indices not the names of the locations themselves
    """
    if params[1] != "all" and params[1] not in input_file:
        return None, None
        
    if params[0] == "ILP":
        ilp = ILP(num_of_locations, num_houses, list_of_locations, list_of_houses, starting_car_location, adjacency_matrix)
        car_path, drop_off = ilp.solve()
        return car_path, drop_off
    else:
        r = Reduction(num_of_locations, num_houses, list_of_locations, list_of_houses, starting_car_location, adjacency_matrix)
        if params[0] == "Ant":
            car_path, drop_off = r.Ant_Colony_solve()
            return car_path, drop_off
        else:
            car_path, drop_off, best_k, best_s = r.Two_Opt_solve()
            # Write best_k and best_s to a file
            with open('best_k_and_s.txt', 'a+') as f:
                f.write('%s %s \n' % (best_k, best_s))
            return car_path, drop_off

"""
Convert solution with path and dropoff_mapping in terms of indices
and write solution output in terms of names to path_to_file + file_number + '.out'
"""
def convertToFile(path, dropoff_mapping, path_to_file, list_locs):
    string = ''
    for node in path:
        string += list_locs[node] + ' '
    string = string.strip()
    string += '\n'

    dropoffNumber = len(dropoff_mapping.keys())
    string += str(dropoffNumber) + '\n'
    for dropoff in dropoff_mapping.keys():
        strDrop = list_locs[dropoff] + ' '
        for node in dropoff_mapping[dropoff]:
            strDrop += list_locs[node] + ' '
        strDrop = strDrop.strip()
        strDrop += '\n'
        string += strDrop
    utils.write_to_file(path_to_file, string)

def solve_from_file(input_file, output_directory, params=[]):
    print('Processing', input_file)

    input_data = utils.read_file(input_file)
    num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix = data_parser(input_data)
    car_path, drop_offs = solve(input_file, num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix, params=params)

    if car_path is None and drop_offs is None:
        return 

    basename, filename = os.path.split(input_file)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file = utils.input_to_output(input_file, output_directory)

    convertToFile(car_path, drop_offs, output_file, list_locations)


def solve_all(input_directory, output_directory, params=[]):
    input_files = utils.get_files_with_extension(input_directory, 'in')
    for input_file in input_files:
        solve_from_file(input_file, output_directory, params=params)
    

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Parsing arguments')
    parser.add_argument('--all', action='store_true', help='If specified, the solver is run on all files in the input directory. Else, it is run on just the given input file')
    parser.add_argument('input', type=str, help='The path to the input file or directory')
    parser.add_argument('output_directory', type=str, nargs='?', default='.', help='The path to the directory where the output should be written')
    parser.add_argument('params', nargs=argparse.REMAINDER, help='Extra arguments passed in')
    args = parser.parse_args()
    output_directory = args.output_directory
    if args.all:
        input_directory = args.input
        solve_all(input_directory, output_directory, params=args.params)
    else:
        input_file = args.input
        solve_from_file(input_file, output_directory, params=args.params)
