import json
import sys
from pathlib import Path

id_to_path_map = {
    "18698": "20250522_sweagent_claude-4-sonnet-20250514\\trajs\\sympy__sympy-18698",
    "23950": "20250522_sweagent_claude-4-sonnet-20250514\\trajs\\sympy__sympy-23950",
    "16950": "20250522_sweagent_claude-4-sonnet-20250514\\trajs\\django__django-16950",
    "9461": "20250522_sweagent_claude-4-sonnet-20250514\\trajs\\sphinx-doc__sphinx-9461",
    "14976": "20250522_sweagent_claude-4-sonnet-20250514\\trajs\\sympy__sympy-14976",
    "10554": "20250511_sweagent_lm_32b\\trajs\\django__django-10554",
    "4687": "20250511_sweagent_lm_32b\\trajs\\pydata__xarray-4687",
    "16631": "20250511_sweagent_lm_32b\\trajs\\django__django-16631",
    "4970": "20250511_sweagent_lm_32b\\trajs\\pylint-dev__pylint-4970",
    "15127": "20250511_sweagent_lm_32b\\trajs\\django__django-15127",
    "11138": "20250511_sweagent_lm_32b\\trajs\\django__django-11138",
    "15100": "20250511_sweagent_lm_32b\\trajs\\scikit-learn__scikit-learn-15100",
    "22080": "20250511_sweagent_lm_32b\\trajs\\sympy__sympy-22080",
    "6938": "20250511_sweagent_lm_32b\\trajs\\pydata__xarray-6938",
    "21612": "20250511_sweagent_lm_32b\\trajs\\sympy__sympy-21612",
    "26113": "20250511_sweagent_lm_32b\\trajs\\matplotlib__matplotlib-26113",
    "21379": "20250511_sweagent_lm_32b\\trajs\\sympy__sympy-21379",
    "2931": "20250511_sweagent_lm_32b\\trajs\\psf__requests-2931",
    "7454": "20250511_sweagent_lm_32b\\trajs\\sphinx-doc__sphinx-7454",
    "16792": "20250511_sweagent_lm_32b\\trajs\\sympy__sympy-16792"
}

def locate_reproduction_code(id: str):
    trajectory = load_trajectory(id)

    log_file = open('locate_reproduction_code.log', 'a', encoding='utf-8')
    original_stdout = sys.stdout
    sys.stdout = log_file
    
    print(f"\n{'='*80}")
    print(f"ID: {id}")
    print(f"{'='*80}")

    repro_steps = []
    for i, step in enumerate(trajectory):
        observation = step["observation"]
        
        # check if observation contains "created successfully"
        if "created successfully" in observation:
            observation_lower = observation.lower()
            action = step["action"]
            
            # check if observation contains "reproduce"
            if "reproduce" in observation_lower and len(observation_lower) < 200:
                repro_steps.append(i)
                print(f"Found reproduction code at step {i} for ID {id}")
                print(f"Observation: {observation}")
                print(f"Action: {action}")
                print("-" * 80)
    
    print(f"Result: {repro_steps}")
    sys.stdout = original_stdout
    log_file.close()
    
    return repro_steps

def locate_search():
    return

def locate_tool_usage():
    return

def print_trajectory_steps(trajectory):
    for (i, step) in enumerate(trajectory):
        print(str(i+1) + ": " + step["thought"])
        print(">> " + step["action"])
        print(step["observation"])
        print(step["action"])
        print('-' * 80)

    print("Finished in " + str(len(trajectory)) + " steps")

def load_trajectory(id: str):
    dir_path = id_to_path_map[id]
    folder_name = Path(dir_path).name
    traj_filename = f"{folder_name}.traj"
    traj_path = Path(dir_path) / traj_filename

    with open(traj_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data["trajectory"]

for id in id_to_path_map.keys():
    result = locate_reproduction_code(id)
    print(f"{id} => {result}")