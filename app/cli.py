import argparse
import json
import sys
from app.core.agent import JuniorDevAgent

def main():
    parser = argparse.ArgumentParser(description="Junior Dev Agent CLI Workstation")
    parser.add_argument("--repo", required=True, help="Path to target repository")
    parser.add_argument("--mode", default="investigate", choices=["investigate", "debug", "review", "test", "implement"], help="Agent mode")
    parser.add_argument("--task", required=True, help="Task prompt or bug report description")
    parser.add_argument("--approve", action="store_true", help="Approve code modification plan in implement mode")

    args = parser.parse_args()

    agent = JuniorDevAgent(args.repo)
    print(f"🤖 Junior Dev Agent running in [{args.mode.upper()}] mode against '{args.repo}'...")
    
    res = agent.run_task(
        mode=args.mode,
        task_prompt=args.task,
        user_approved=args.approve
    )

    print("\n=== AGENT RESPONSE REPORT ===")
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
