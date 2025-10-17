from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# Define the input, output, and overall state structures
from typing_extensions import TypedDict

class OverallState(TypedDict):
    partial_message: str
    user_input: str
    message_output: str

class InputState(TypedDict):
    user_input: str

class OutputState(TypedDict):
    message_output: str

class PrivateState(TypedDict):
    private_message: str

# Define nodes (functions) that operate on the states
def add_world(state: InputState) -> OverallState:
    partial_message = state["user_input"] + " World"
    print(f"Node 1 - add_world: Transformed '{state['user_input']}' to '{partial_message}'")
    return {"partial_message": partial_message, "user_input": state["user_input"], "message_output": ""}


def add_exclamation(state: OverallState) -> PrivateState:
    private_message = state["partial_message"] + "!"
    print(f"Node 2 - add_exclamation: Transformed '{state['partial_message']}' to '{private_message}'")
    return {"private_message": private_message}


def finalize_message(state: PrivateState) -> OutputState:
    message_output = state["private_message"]
    print(f"Node 3 - finalize_message: Finalized message to '{message_output}'")
    return {"message_output": message_output}

# Create the graph builder with nodes and edges
builder = StateGraph(OverallState, input=InputState, output=OutputState)
builder.add_node("add_world", add_world)
builder.add_node("add_exclamation", add_exclamation)
builder.add_node("finalize_message", finalize_message)


# Define the edges between nodes
builder.add_edge(START, "add_world")
builder.add_edge("add_world", "add_exclamation")
builder.add_edge("add_exclamation", "finalize_message")
builder.add_edge("finalize_message", END)


# Compile and run the graph
graph = builder.compile()
result = graph.invoke({"user_input": "Hello"})
print(result)  # Output: {'message_output': 'Hello World!'}



