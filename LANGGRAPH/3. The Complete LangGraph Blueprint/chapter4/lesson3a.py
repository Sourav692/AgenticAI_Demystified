from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class HelloWorldState(TypedDict):
    """The state"""
    message: str  # This state key will store the message

def hello_world_node(state: HelloWorldState):
    """The node function"""
    state["message"] += "Hello World"
    return state

# Initialize the graph
graph_builder = StateGraph(HelloWorldState)

#Define the nodes
graph_builder.add_node("hello_world", hello_world_node)

# Define the flow of execution using edges
"""The edges"""
graph_builder.add_edge(START, "hello_world")  # Connect START to the "greet" node
graph_builder.add_edge("hello_world", END)    # Connect the "greet" node to END

# Compile and run the graph
"""The graph"""
graph = graph_builder.compile()
result = graph.invoke({"message": "Hi! "})
# Output the result
print(result)
# Output: {'greeting': 'Hi! Hello World'}
