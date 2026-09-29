import os
from src.graph import build_quant_coder_graph
from dotenv import load_dotenv

load_dotenv()

def run_agent(task_description: str):
    """
    Kicks off the stateful Plan-Execute-Verify LangGraph loop.
    """
    graph = build_quant_coder_graph()
    
    initial_state = {
        "messages": [],
        "task_description": task_description,
        "logic_plan": "",
        "generated_code": "",
        "test_results": "",
        "tests_passed": False,
        "retry_count": 0,
        "max_retries": 3
    }
    
    print(f"--- STARTING T1 QUANT CODER AGENT ---")
    print(f"TASK: {task_description}\n")
    
    # Depending on LangGraph version, we use stream to watch the state transition
    try:
        for output in graph.stream(initial_state):
            for key, value in output.items():
                print(f"Finished Node: {key}")
                if key == "executor_node":
                    print(f"  Tests Passed: {value.get('tests_passed')}")
                elif key == "reviewer_node":
                    print(f"  Current Retry Count: {value.get('retry_count', 0)}")
                print("---------------------------------")
        
        print("\n--- FINAL STATE ---")
        # To get final state cleanly, we invoke it fully (or track from stream).
        # We'll just display a completion message.
        print("Execution pipeline completed. Check artifacts for generated code.")
        
    except Exception as e:
        print(f"Graph execution failed: {e}")

if __name__ == "__main__":
    # Agenthon G0 Gate mockup
    task = '''
Write a python function `def calculate_sharpe(returns: list[float], risk_free_rate: float)` that returns the annualized Sharpe Ratio. 
Assume daily returns (252 trading days). 
Include a robust pytest block at the bottom of the file with assertions for basic edge cases (like zero variance).
    '''
    
    # We require an API key to execute the LLM nodes.
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY is not set. You must provide an API key in a .env file to actually run the LLM nodes.")
        print("The scaffolding is complete, but LLM invocation will fail without credentials.")
    else:
        run_agent(task)
