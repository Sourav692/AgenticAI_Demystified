from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Define the state structure
class State(TypedDict):
    input: str
    modified_input: str

# Define node functions
def step_1(state: State):
    print(f"Original input: {state['input']}")
    return state

def modify_state(state: State):
    # Allow the user to modify the state
    return state

def step_3(state: State):
    print(f"Modified input: {state['modified_input']}")
    return state

# Build the graph
builder = StateGraph(State)
builder.add_node("step_1", step_1)
builder.add_node("modify_state", modify_state)
builder.add_node("step_3", step_3)

# Define the flow
builder.add_edge(START, "step_1")
builder.add_edge("step_1", "modify_state")
builder.add_edge("modify_state", "step_3")
builder.add_edge("step_3", END)

# Set up memory and breakpoints
memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["modify_state"])

# Run the graph
initial_input = {"input": "Initial Input"}
config = {"configurable": {"thread_id": "thread-1"}}

for event in graph.stream(initial_input, config):
    print(event)

# Ask user to modify the state
modified_value = input("Enter the modified input: ")
graph.update_state(config, {"modified_input": modified_value})

# Continue the graph execution
for event in graph.stream(None, config):
    print(event)
