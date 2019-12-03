# Drop Off Buddies Algorithm

## Problem Statement
Brian, Akash, and their buddies are chilling at Brian's home late at night. Brian offers to drive and drop his buddies off closer to their homes so that they can get back home safe. Since the roads are long in his area, Brian would also like to get back home as soon as as he can. Can you plan transportation so that everyone can get home as efficiently as possible?

## Output Commands

### Command Layout
- python3 solver.py `path_to_input_file` `directory_to_outputs` `algorithm` `input_file_size`
- python3 solver.py --all `directory_to_inputs` `directory_to_outputs` `algorithm` `input_file_size`

### Argument Values
- algorithm = ILP, Ant, TwoOpt
- input_file_size = 50, 100, 200, all

### Example
- `python3 solver.py inputs/text.in outputs TwoOpt 200`
- `python3 solver.py --all inputs outputs TwoOpt 200`