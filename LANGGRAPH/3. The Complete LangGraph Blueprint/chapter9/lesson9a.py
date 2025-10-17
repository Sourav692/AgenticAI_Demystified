import os
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from display_graph import display_graph

# Define the state structure
class State(TypedDict):
    input: str

# Define node functions
def step_1(state: State):
    print("--- Step 1 ---")
    return state

def step_2(state: State):
    print("--- Step 2 ---")
    return state

# Build the graph
builder = StateGraph(State)
builder.add_node("step_1", step_1)
builder.add_node("step_2", step_2)

# Define flow
builder.add_edge(START, "step_1")
builder.add_edge("step_1", "step_2")
builder.add_edge("step_2", END)

# Set up memory and breakpoints
memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["step_2"])

# Display the graph
display_graph(graph, file_name=os.path.basename(__file__))

# Run the graph
config = {"configurable": {"thread_id": "thread-1"}}

initial_input = {"input": "Hello, LangGraph!"}
thread = {"configurable": {"thread_id": "1"}}

for event in graph.stream(initial_input, thread, stream_mode="values"):
    print(event)

user_approval = input("Do you approve to continue to Step 2? (yes/no): ")

if user_approval.lower() == "yes":
    for event in graph.stream(None, thread, stream_mode="values"):
        print(event)
else:
    print("Execution halted by user.")
