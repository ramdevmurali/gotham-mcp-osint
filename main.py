import sys
from src.agent import run_agent

def main():
    print("🦇 PROJECT GOTHAM: Autonomous Agent Activated")
    print("---------------------------------------------")
    
    # Check if user provided a prompt via command line
    if len(sys.argv) > 1:
        mission = " ".join(sys.argv[1:])
    else:
        mission = "Find out who is the CEO of Anthropic, what other companies they founded, and save it to the graph."
    
    run_agent(mission)

if __name__ == "__main__":
    main()