import os
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from display_graph import display_graph

class State(TypedDict):
    input: str

def step_a(state: State):
    print("Executing Step A")
    return state

def step_b(state: State):
    print("Executing Step B")
    return state

builder = StateGraph(State)
builder.add_node("step_a", step_a)
builder.add_node("step_b", step_b)

builder.add_edge(START, "step_a")
builder.add_edge("step_a", "step_b")
builder.add_edge("step_b", END)

graph = builder.compile(interrupt_before=["step_b"], checkpointer=MemorySaver())

# Display the graph
display_graph(graph, file_name=os.path.basename(__file__))

initial_input = {"input": "Starting workflow"}
config = {"configurable": {"thread_id": "thread-1"}}

for event in graph.stream(initial_input, config):
    print(event)

approval = input("Proceed to Step B? (yes/no): ")
if approval.lower() == "yes":
    for event in graph.stream(None, config):
        print(event)
else:
    print("Workflow halted before Step B.")
