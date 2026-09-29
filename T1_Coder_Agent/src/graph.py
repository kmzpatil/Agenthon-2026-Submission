from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import planner_node, coder_node, executor_node, reviewer_node, router

def build_quant_coder_graph():
    """
    Constructs the stateful LangGraph for the Plan-Execute-Verify loop.
    """
    # Initialize the graph with our TypedDict State
    workflow = StateGraph(AgentState)
    
    # Add the primary computational nodes
    workflow.add_node("planner_node", planner_node)
    workflow.add_node("coder_node", coder_node)
    workflow.add_node("executor_node", executor_node)
    workflow.add_node("reviewer_node", reviewer_node)
    
    # Set the starting point
    workflow.set_entry_point("planner_node")
    
    # Wire the deterministic linear edges
    workflow.add_edge("planner_node", "coder_node")
    workflow.add_edge("coder_node", "executor_node")
    workflow.add_edge("executor_node", "reviewer_node")
    
    # Wire the conditional reflection/retry edge
    # The router decides whether to send it back to the coder_node or terminate (END)
    workflow.add_conditional_edges(
        "reviewer_node",
        router,
        {
            "coder_node": "coder_node",
            "END": END
        }
    )
    
    # Compile the graph into an executable application
    return workflow.compile()
