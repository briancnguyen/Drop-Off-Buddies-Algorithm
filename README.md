# Drop Off Buddies Algorithm

## Python Packages Installation Process
- `pip3 install -r requirements.txt`

## Run this Short Command to Generate Every Output
### Command Layout
- python3 shortcut.py `directory_to_inputs` `directory_to_outputs`

### Example
- `python3 shortcut.py inputs outputs`

## Solver Commands (Advanced)
### Command Layout
- python3 solver.py `path_to_input_file` `directory_to_outputs` `algorithm` `input_file_size`
- python3 solver.py --all `directory_to_inputs` `directory_to_outputs` `algorithm` `input_file_size`

### Argument Values
- algorithm = ILP, ANT, TSP
- input_file_size = 50, 100, 200, ALL

### Example
- `python3 solver.py inputs/text.in outputs TSP 200`
- `python3 solver.py --all inputs outputs TSP 200`