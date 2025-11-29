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

    log_file = open('locate_reproduction_code.log', 'w', encoding='utf-8')
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

def locate_search(id: str):
    trajectory = load_trajectory(id)

    log_file = open('locate_search.log', 'w', encoding='utf-8')
    original_stdout = sys.stdout
    sys.stdout = log_file

    print(f"\n{'='*80}")
    print(f"ID: {id}")
    print(f"{'='*80}")

    search_steps = []
    keywords = ["find_file", "search_file", "search_dir", "grep ", "cat ", "ls ", "cd "]
    for i, step in enumerate(trajectory):
        action = step["action"].split("\n")[0]
        if any(keyword in action for keyword in keywords):
            search_steps.append(i)
            print(f"Found search action at step {i} for ID {id}")
            print(f"Action: {action}")
            print("-" * 80)

    print(f"Result: {search_steps}")
    sys.stdout = original_stdout
    log_file.close()
    
    return search_steps

def locate_tool_usage(id: str):
    trajectory = load_trajectory(id)

    log_file = open('locate_tool_use.log', 'w', encoding='utf-8')
    original_stdout = sys.stdout
    sys.stdout = log_file

    print(f"\n{'='*80}")
    print(f"ID: {id}")
    print(f"{'='*80}")

    tool_map = {}
    tools = ["str_replace_editor", "filemap ", "exit_forfeit", "view_image ", "submit", "find_file ", 
             "goto ", "open ", "create ", "scroll_up", "scroll_down", "edit ", "insert ", "search_dir ", 
             "search_file ", "end_of_edit", "grep ", "ls ", "cd ", "find ", "python ", "do_nothing"]
    
    for tool in tools:
        tool_map[tool.strip()] = 0

    for i, step in enumerate(trajectory):
        action = step["action"].split("\n")[0]
        print(f"Action: {action}")
        for tool in tools:
            if tool in action:
                if tool == "create " and "str_replace_editor " in action:
                    continue  # skip str_replace_editor command option

                tool_map[tool.strip()] += 1
                print(f"Found tool '{tool.strip()}' usage at step {i} for ID {id}")

        print("-" * 80)

    for tool in list(tool_map.keys()):
        if tool_map[tool] == 0:
            del tool_map[tool]

    print(f"Result: {tool_map}")
    sys.stdout = original_stdout
    log_file.close()
    
    return tool_map

# helper function to load trajectory array from file
def load_trajectory(id: str):
    dir_path = id_to_path_map[id]
    folder_name = Path(dir_path).name
    traj_filename = f"{folder_name}.traj"
    traj_path = Path(dir_path) / traj_filename

    with open(traj_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data["trajectory"]

# helper function to print trajectory steps
def print_trajectory_steps(trajectory):
    for (i, step) in enumerate(trajectory):
        print(str(i+1) + ": " + step["thought"])
        action = step["action"].split("\n")[0]
        print(">> " + action)
        print(step["observation"])
        print('-' * 80)

    print("Finished in " + str(len(trajectory)) + " steps")

for id in id_to_path_map.keys():
    print(f"\nProcessing ID: {id}")
    repro_steps = locate_reproduction_code(id)
    print(f"Steps with reproduction code => {repro_steps}")
    search_steps = locate_search(id)
    print(f"Steps with search actions => {search_steps}")
    tool_usage = locate_tool_usage(id)
    print(f"Tool usage frequency map => {tool_usage}")