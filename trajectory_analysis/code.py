import json
import sys
from pathlib import Path

# Folder that contains all the .traj files
BASE_DIR = Path("trajectories")

# Map from numeric ID to actual .traj filename
id_to_filename = {
    # YOUR 10 (you analyse these)
    "10554": "django__django-10554.traj",
    "11138": "django__django-11138.traj",
    "12308": "django__django-12308.traj",
    "12774": "django__django-12774.traj",
    "15127": "django__django-15127.traj",
    "16631": "django__django-16631.traj",
    "16950": "django__django-16950.traj",
    "26113": "matplotlib__matplotlib-26113.traj",
    "4687":  "pydata__xarray-4687.traj",
    "6938":  "pydata__xarray-6938.traj",

    # Lukas's 10 (11–20) – fine to leave here
    "4970":  "pylint-dev__pylint-4970.traj",
    "8898":  "pylint-dev__pylint-8898.traj",
    "15100": "scikit-learn__scikit-learn-15100.traj",
    "9461":  "sphinx-doc__sphinx-9461.traj",
    "14976": "sympy__sympy-14976.traj",
    "18698": "sympy__sympy-18698.traj",
    "21379": "sympy__sympy-21379.traj",
    "21612": "sympy__sympy-21612.traj",
    "22080": "sympy__sympy-22080.traj",
    "23950": "sympy__sympy-23950.traj",
}

# -------------------------------------------------------------------
# Helper: load trajectory from .traj file
# -------------------------------------------------------------------
def load_trajectory(id: str):
    filename = id_to_filename[id]
    traj_path = BASE_DIR / filename
    print("Loading:", traj_path) 
    with open(traj_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["trajectory"]

# -------------------------------------------------------------------
# Helper: nicely print a trajectory (for manual reading)
# -------------------------------------------------------------------
def print_trajectory_steps(trajectory):
    for i, step in enumerate(trajectory):
        print(f"{i+1}: {step['thought']}")
        action = step["action"].split("\n")[0]
        print(">> " + action)
        print(step["observation"])
        print("-" * 80)

    print("Finished in " + str(len(trajectory)) + " steps")

# -------------------------------------------------------------------
# 1) Locate reproduction code
# -------------------------------------------------------------------
def locate_reproduction_code(id: str):
    trajectory = load_trajectory(id)

    log_file = open("locate_reproduction_code.log", "a", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = log_file

    print(f"\n{'='*80}")
    print(f"ID: {id}")
    print(f"{'='*80}")

    repro_steps = []
    for i, step in enumerate(trajectory):
        observation = step["observation"]

        if "created successfully" in observation:
            observation_lower = observation.lower()
            action = step["action"]

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

# -------------------------------------------------------------------
# 2) Locate search actions
# -------------------------------------------------------------------
def locate_search(id: str):
    trajectory = load_trajectory(id)

    log_file = open("locate_search.log", "a", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = log_file

    print(f"\n{'='*80}")
    print(f"ID: {id}")
    print(f"{'='*80}")

    search_steps = []
    keywords = ["find_file", "search_file", "search_dir",
                "grep ", "cat ", "ls ", "cd "]

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

# -------------------------------------------------------------------
# 3) Count tool usage
# -------------------------------------------------------------------
def locate_tool_usage(id: str):
    trajectory = load_trajectory(id)

    log_file = open("locate_tool_use.log", "a", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = log_file

    print(f"\n{'='*80}")
    print(f"ID: {id}")
    print(f"{'='*80}")

    tool_map = {}
    tools = [
        "str_replace_editor", "filemap ", "exit_forfeit", "view_image ",
        "submit", "find_file ", "goto ", "open ", "create ", "scroll_up",
        "scroll_down", "edit ", "insert ", "search_dir ", "search_file ",
        "end_of_edit", "grep ", "ls ", "cd ", "find ", "python ", "do_nothing"
    ]

    for tool in tools:
        tool_map[tool.strip()] = 0

    for i, step in enumerate(trajectory):
        action = step["action"].split("\n")[0]
        print(f"Action: {action}")
        for tool in tools:
            if tool in action:
                if tool == "create " and "str_replace_editor " in action:
                    continue
                tool_map[tool.strip()] += 1
                print(f"Found tool '{tool.strip()}' usage at step {i} for ID {id}")
        print("-" * 80)

    # remove tools never used
    tool_map = {k: v for k, v in tool_map.items() if v > 0}

    print(f"Result: {tool_map}")
    sys.stdout = original_stdout
    log_file.close()

    return tool_map
# -------------------------------------------------------------------
# Optional: Pretty-print all 10 trajectories into readable .txt files
# -------------------------------------------------------------------
def export_pretty_trajs():
    print("Exporting pretty trajectory files...")

    for tid in ids_you_analyze:  # uses the IDs already defined below
        filename = id_to_filename[tid]
        traj_path = BASE_DIR / filename

        # Load JSON
        with open(traj_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        trajectory = data["trajectory"]

        # Output file
        out_path = f"{tid}_pretty.txt"

        with open(out_path, "w", encoding="utf-8") as out:
            original_stdout = sys.stdout
            sys.stdout = out

            print_trajectory_steps(trajectory)

            sys.stdout = original_stdout

        print(f"Saved: {out_path}")

# -------------------------------------------------------------------
# Main: run analysis for YOUR 10 trajectories
# -------------------------------------------------------------------
if __name__ == "__main__":
    ids_you_analyze = [
        "10554", "11138", "12308", "12774", "15127",
        "16631", "16950", "26113", "4687", "6938",
    ]
    export_pretty_trajs()
    
    for id in ids_you_analyze:
        print(f"\nProcessing ID: {id}")
        repro_steps = locate_reproduction_code(id)
        print(f"Steps with reproduction code => {repro_steps}")
        search_steps = locate_search(id)
        print(f"Steps with search actions => {search_steps}")
        tool_usage = locate_tool_usage(id)
        print(f"Tool usage frequency map => {tool_usage}")
