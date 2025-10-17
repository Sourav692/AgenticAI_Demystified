from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

from display_graph import display_graph


# Define the state structure
class GreetingState(TypedDict):
    greeting: str

# Define a preprocessing node to normalize the greeting
def normalize_greeting_node(state):
    # Transform the greeting to lowercase
    state["greeting"] = state["greeting"].lower()
    return state  # Return the updated state dictionary

# Define a node for the "Hi" greeting
def hi_greeting_node(state):
    state["greeting"] = "Hi there, " + state["greeting"]
    return state  # Return the updated state dictionary

# Define a node for a standard greeting
def regular_greeting_node(state):
    state["greeting"] = "Hello, " + state["greeting"]
    return state  # Return the updated state dictionary

# Define the conditional function to choose the appropriate greeting 
def choose_greeting_node(state):
    # Choose the node based on whether "hi" is in the normalized greeting
    return "hi_greeting" if "hi" in state["greeting"] else "regular_greeting"

# Initialize the StateGraph
builder = StateGraph(GreetingState)
builder.add_node("normalize_greeting", normalize_greeting_node)
builder.add_node("hi_greeting", hi_greeting_node)
builder.add_node("regular_greeting", regular_greeting_node)

# Add the START to normalization node, then conditionally branch based on the transformed greeting
builder.add_edge(START, "normalize_greeting")
builder.add_conditional_edges(
    "normalize_greeting", choose_greeting_node, ["hi_greeting", "regular_greeting"]
)
builder.add_edge("hi_greeting", END)
builder.add_edge("regular_greeting", END)

# Compile and run the graph
graph = builder.compile()

#Display the graph
display_graph(graph)

# Test with a greeting containing "Hi" in various forms (e.g., uppercase, mixed case)
result = graph.invoke({"greeting": "HI THERe!"})
print(result)  # Expected Output: {'greeting': 'Hi there, hi there!'}

# Test with a greeting not containing "Hi"
result = graph.invoke({"greeting": "Good morning!"})
print(result)  # Expected Output: {'greeting': 'Hello, good morning!'}


