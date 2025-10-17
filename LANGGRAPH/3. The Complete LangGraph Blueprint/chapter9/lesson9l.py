from langgraph.errors import NodeInterrupt
import os
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

from display_graph import display_graph

class State(TypedDict):
    input: str

builder = StateGraph(State)

def step_with_dynamic_interrupt(state: State):
    input_length = len(state["input"])
    if input_length > 10:
        raise NodeInterrupt("Input length {input_length} exceeds threshold of 10.")
    return state

builder.add_node("step_with_dynamic_interrupt", step_with_dynamic_interrupt)
builder.add_edge(START, "step_with_dynamic_interrupt")
builder.add_edge("step_with_dynamic_interrupt", END)

graph = builder.compile()
# Display the graph
display_graph(graph, file_name=os.path.basename(__file__))

initial_input = {"input": "This is a long input"}
for event in graph.stream(initial_input):
    print(event)
