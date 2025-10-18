import sys
import os
import subprocess

BASE_DIR = os.path.dirname(__file__)

AGENTS = {
    "1": {
        "name": "Insert Agent 1 (Add Patient)",
        "cwd": os.path.join(BASE_DIR, "agent1"),
        "cmd": [sys.executable, "main.py"],
    },
    "2": {
        "name": "Insert Agent 2 (Fast Add Patient)",
        "cwd": os.path.join(BASE_DIR, "agent2"),
        "cmd": [sys.executable, "main.py"],
    },
    "3": {
        "name": "Insert Agent 3 (AutoHotkey Runner)",
        "cwd": os.path.join(BASE_DIR, "agent3"),
        "cmd": [sys.executable, "agent3_runner.py"],
    },
}


def choose_agent():
    print("Select an Insert agent:")
    for k, meta in sorted(AGENTS.items()):
        print(f"  {k}) {meta['name']}")
    choice = input("Enter choice: ").strip()
    return AGENTS.get(choice)


def main():
    agent = choose_agent()
    if not agent:
        print("Invalid choice.")
        sys.exit(1)
    print(f"Launching: {agent['name']}")
    cwd = agent.get("cwd", BASE_DIR)
    sys.exit(subprocess.call(agent["cmd"], cwd=cwd))


if __name__ == "__main__":
    main()


