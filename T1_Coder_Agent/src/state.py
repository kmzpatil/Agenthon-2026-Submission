import operator
from typing import TypedDict, Annotated, List, Any
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Graph state for the Plan-Execute-Verify Loop.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    task_description: str
    logic_plan: str
    generated_code: str
    
    # Subprocess execution results
    test_results: str
    tests_passed: bool
    
    # Advanced reflection state
    last_traceback: str
    last_error_signature: str
    stuck_loop: bool
    
    # State counters for the retry budget
    retry_count: int
    max_retries: int
