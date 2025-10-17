import os
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from display_graph import display_graph

class State(TypedDict):
    data: str

def delete_data(state: State):
    print(f"Data to be deleted: {state['data']}")
    return state

builder = StateGraph(State)
builder.add_node("delete_data", delete_data)
builder.add_edge(START, "delete_data")
builder.add_edge("delete_data", END)

graph = builder.compile(interrupt_before=["delete_data"], checkpointer=MemorySaver())

# Display the graph
display_graph(graph, file_name=os.path.basename(__file__))

initial_input = {"data": "Sensitive Information"}
config = {"configurable": {"thread_id": "thread-1"}}

for event in graph.stream(initial_input, config):
    print(event)

approval = input("Approve data deletion? (yes/no): ")
if approval.lower() == "yes":
    for event in graph.stream(None, config):
        print(event)
else:
    print("Data deletion cancelled.")
