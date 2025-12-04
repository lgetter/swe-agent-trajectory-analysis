#!/usr/bin/env python3
"""
Script to format .traj files into a readable format for following 
the agent's debugging and bug resolving process.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def format_trajectory(traj_file_path, output_file=None):
    """
    Format a .traj file into a human-readable format.
    
    Args:
        traj_file_path: Path to the .traj file
        output_file: Optional output file path. If None, prints to stdout.
    """
    # Load the trajectory file
    with open(traj_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    trajectory = data.get("trajectory", [])
    
    # Prepare output
    lines = []
    lines.append("=" * 100)
    lines.append(f"TRAJECTORY ANALYSIS: {Path(traj_file_path).name}")
    lines.append("=" * 100)
    lines.append(f"Total Steps: {len(trajectory)}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 100)
    lines.append("")
    
    # Extract and display initial system messages from first step
    if trajectory and len(trajectory) > 0:
        first_step = trajectory[0]
        messages = first_step.get("messages", [])
        
        if messages:
            lines.append("")
            lines.append("╔" + "═" * 98 + "╗")
            lines.append("║" + " " * 35 + "INITIAL CONTEXT" + " " * 48 + "║")
            lines.append("╚" + "═" * 98 + "╝")
            lines.append("")
            
            # Find and display system_prompt and first observation
            system_prompt_msg = None
            observation_msg = None
            
            for msg in messages:
                msg_type = msg.get("message_type", "")
                if msg_type == "system_prompt" and not system_prompt_msg:
                    system_prompt_msg = msg
                elif msg_type == "observation" and not observation_msg:
                    observation_msg = msg
            
            # Display system prompt
            if system_prompt_msg:
                lines.append("┌" + "─" * 98 + "┐")
                lines.append("│ 🔧 SYSTEM PROMPT" + " " * 80 + "│")
                lines.append("└" + "─" * 98 + "┘")
                lines.append("")
                
                content = system_prompt_msg.get("content", "")
                if len(content) > 5000:
                    lines.append(content[:5000])
                    lines.append(f"\n... [Content truncated - {len(content)} total characters] ...\n")
                else:
                    lines.append(content)
                lines.append("")
            
            # Display observation (problem description)
            if observation_msg:
                lines.append("┌" + "─" * 98 + "┐")
                lines.append("│ 📋 PROBLEM DESCRIPTION / INITIAL OBSERVATION" + " " * 52 + "│")
                lines.append("└" + "─" * 98 + "┘")
                lines.append("")
                
                content = observation_msg.get("content", "")
                if len(content) > 3000:
                    lines.append(content[:3000])
                    lines.append(f"\n... [Content truncated - {len(content)} total characters] ...\n")
                else:
                    lines.append(content)
                lines.append("")
            
            lines.append("=" * 100)
            lines.append("")
    
    # Process each step
    for i, step in enumerate(trajectory, 1):
        lines.append("")
        lines.append("█" * 100)
        lines.append(f"STEP {i} of {len(trajectory)}")
        lines.append("█" * 100)
        
        # Thought process
        thought = step.get("thought", "No thought recorded")
        lines.append("")
        lines.append("💭 AGENT'S THOUGHT PROCESS:")
        lines.append("-" * 100)
        lines.append(thought)
        lines.append("")
        
        # Action taken
        action = step.get("action", "No action recorded")
        action_lines = action.split('\n')
        action_summary = action_lines[0] if action_lines else action
        
        lines.append("⚡ ACTION TAKEN:")
        lines.append("-" * 100)
        lines.append(f"Command: {action_summary}")
        
        # Show full action if it's multi-line
        if len(action_lines) > 1:
            lines.append("")
            lines.append("Full Action:")
            for line in action_lines:
                lines.append(f"  {line}")
        lines.append("")
        
        # Observation/Result
        observation = step.get("observation", "No observation recorded")
        lines.append("👁️  OBSERVATION/RESULT:")
        lines.append("-" * 100)
        
        # Truncate very long observations
        if len(observation) > 2000:
            lines.append(observation[:2000])
            lines.append("")
            lines.append(f"... [Output truncated - {len(observation)} total characters] ...")
        else:
            lines.append(observation)
        
        lines.append("")
        
        # Extract key information
        response = step.get("response", "")
        if response and response != thought:
            lines.append("📝 AGENT'S RESPONSE:")
            lines.append("-" * 100)
            if len(response) > 1000:
                lines.append(response[:1000])
                lines.append(f"... [Response truncated - {len(response)} total characters] ...")
            else:
                lines.append(response)
            lines.append("")
        
        # Execution time if available
        exec_time = step.get("execution_time")
        if exec_time:
            lines.append(f"⏱️  Execution Time: {exec_time:.4f} seconds")
            lines.append("")
        
        # Working directory if available
        state = step.get("state", {})
        working_dir = state.get("working_dir")
        if working_dir:
            lines.append(f"📁 Working Directory: {working_dir}")
            lines.append("")
    
    # Summary at the end
    lines.append("")
    lines.append("=" * 100)
    lines.append("TRAJECTORY SUMMARY")
    lines.append("=" * 100)
    lines.append(f"Total Steps Executed: {len(trajectory)}")
    
    # Count action types
    action_types = {}
    for step in trajectory:
        action = step.get("action", "")
        # Extract command type (first word typically)
        cmd = action.split()[0] if action.split() else "unknown"
        action_types[cmd] = action_types.get(cmd, 0) + 1
    
    lines.append("")
    lines.append("Action Type Distribution:")
    for cmd, count in sorted(action_types.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  {cmd}: {count}")
    
    lines.append("")
    lines.append("=" * 100)
    lines.append("END OF TRAJECTORY")
    lines.append("=" * 100)
    
    # Output results
    output_text = '\n'.join(lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"✅ Trajectory formatted and saved to: {output_file}")
        print(f"   Total steps: {len(trajectory)}")
    else:
        print(output_text)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python format_trajectory.py <path_to_traj_file> [output_file]")
        print("\nExample:")
        print("  python format_trajectory.py trajectory.traj")
        print("  python format_trajectory.py trajectory.traj output.txt")
        sys.exit(1)
    
    traj_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(traj_file).exists():
        print(f"❌ Error: File not found: {traj_file}")
        sys.exit(1)
    
    try:
        format_trajectory(traj_file, output_file)
    except Exception as e:
        print(f"❌ Error processing trajectory file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
