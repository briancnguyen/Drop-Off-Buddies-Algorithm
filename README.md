# Drop-Off Buddies Algorithm

## Problem Statement
Brian, Akash, and their friends are chilling at Brian's home late at night. Brian offers to drive and drop his friends off closer to their homes so that they can get back home safe. Since the roads are long in his area, Brian would also like to get back home as soon as as he can. Can you plan transportation so that everyone can get home as efficiently as possible?

## Output Commands

### Command Layout
python3 solver.py `path_to_input_file` `directory_to_outputs` `algorithm` `input_file_size` `num_iterations_for_TwoOpt`
python3 solver.py --all `directory_to_inputs` `directory_to_outputs` `algorithm` `input_file_size` `num_iterations_for_TwoOpt`

### Argument Values
- algorithm = ILP, Ant, TwoOpt
- input_file_size = 50, 100, 200, all
- num_iterations_for_TwoOpt = 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000

### Example
`python3 solver.py inputs/text.in outputs_two_opt TwoOpt 200 100`
`python3 solver.py --all inputs outputs_two_opt TwoOpt 200 100`