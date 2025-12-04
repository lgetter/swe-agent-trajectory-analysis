import json
import sys
from pathlib import Path

id_to_path_map = {
    "18698": ".\\trajs\\sympy__sympy-18698.traj",
    "23950": ".\\trajs\\sympy__sympy-23950.traj",
    "16950": ".\\trajs\\django__django-16950.traj",
    "9461": ".\\trajs\\sphinx-doc__sphinx-9461.traj",
    "14976": ".\\trajs\\sympy__sympy-14976.traj",
    "10554": ".\\trajs\\django__django-10554.traj",
    "4687": ".\\trajs\\pydata__xarray-4687.traj",
    "16631": ".\\trajs\\django__django-16631.traj",
    "4970": ".\\trajs\\pylint-dev__pylint-4970.traj",
    "15127": ".\\trajs\\django__django-15127.traj",
    "11138": ".\\trajs\\django__django-11138.traj",
    "15100": ".\\trajs\\scikit-learn__scikit-learn-15100.traj",
    "22080": ".\\trajs\\sympy__sympy-22080.traj",
    "6938": ".\\trajs\\pydata__xarray-6938.traj",
    "21612": ".\\trajs\\sympy__sympy-21612.traj",
    "26113": ".\\trajs\\matplotlib__matplotlib-26113.traj",
    "21379": ".\\trajs\\sympy__sympy-21379.traj",
    "2931": ".\\trajs\\psf__requests-2931.traj",
    "7454": ".\\trajs\\sphinx-doc__sphinx-7454.traj",
    "16792": ".\\trajs\\sympy__sympy-16792.traj"
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
                repro_steps.append(i+1)
                print(f"Found reproduction code at step {i+1} for ID {id}")
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
            search_steps.append(i+1)
            print(f"Found search action at step {i+1} for ID {id}")
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
                print(f"Found tool '{tool.strip()}' usage at step {i+1} for ID {id}")

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
    traj_filename = f"{id_to_path_map[id]}"
    traj_path = Path(traj_filename)

    with open(traj_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data["trajectory"]

def print_trajectory_steps(trajectory, output_file='trajectory_steps.txt'):
    with open(output_file, 'w', encoding='utf-8') as f:
        for (i, step) in enumerate(trajectory):
            action_first_line = step["action"].split("\n")[0]
            f.write(f"\n{'-'*80}\n")
            f.write(f"Step {i}:\n")
            f.write(f"Thought: {step['thought']}\n")
            f.write(f"Action: {action_first_line}\n")
            # f.write(f"Full Action: {step['action']}\n")
            # f.write(f"Observation: {step['observation']}\n")
        f.write(f"\nTotal steps: {len(trajectory)}\n")
    
    print(f"Trajectory saved to {output_file} with {len(trajectory)} steps")


id = "23950"
print(f"\nProcessing ID: {id}")
repro_steps = locate_reproduction_code(id)
print(f"Steps with reproduction code => {repro_steps}")
search_steps = locate_search(id)
print(f"Steps with search actions => {search_steps}")
tool_usage = locate_tool_usage(id)
print(f"Tool usage frequency map => {tool_usage}")
# print_trajectory_steps(load_trajectory(id))