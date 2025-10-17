import os
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from display_graph import display_graph

class State(TypedDict):
    title: str

def generate_report(state: State):
    """
    Generate a financial report based on the provided title.
    """
    print(f"Generating report with title: {state['title']}")
    return state

builder = StateGraph(State)
builder.add_node("generate_report", generate_report)
builder.add_edge(START, "generate_report")
builder.add_edge("generate_report", END)

graph = builder.compile(interrupt_before=["generate_report"], checkpointer=MemorySaver())

# Display the graph
display_graph(graph, file_name=os.path.basename(__file__))

initial_input = {"title": "Annual Financial Report"}
config = {"configurable": {"thread_id": "thread-1"}}

for event in graph.stream(initial_input, config):
    print(event)

approval = input("Approve report generation? (yes/no): ")
if approval.lower() == "yes":
    for event in graph.stream(None, config):
        if event:
            print(event)
else:
    print("Report generation cancelled.")
