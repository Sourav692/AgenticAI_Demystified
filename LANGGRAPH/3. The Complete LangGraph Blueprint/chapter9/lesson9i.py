import os
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool

from display_graph import display_graph

class State(TypedDict):
    query: str

@tool
def perform_query(query: str):
    """:param query: The SQL query to be executed."""
    print(f"Performing query: {query}")
    return {"query" :{query}}

def review_query(state: State):
    print(f"Reviewing query: {state['query']}")
    return state

builder = StateGraph(State)
builder.add_node("perform_query", perform_query)
builder.add_node("review_query", review_query)

builder.add_edge("review_query", "perform_query")
builder.add_edge(START, "review_query")
builder.add_edge("perform_query", END)

graph = builder.compile(interrupt_before=["perform_query"], checkpointer=MemorySaver())

# Display the graph
display_graph(graph, file_name=os.path.basename(__file__))

initial_input = {"query": "SELECT * FROM users"}
config = {"configurable": {"thread_id": "thread-1"}}

for event in graph.stream(initial_input, config):
    print(event)

approval = input("Approve query execution? (yes/no): ")
if approval.lower() == "yes":
    for event in graph.stream(None, config):
        print(event)
else:
    print("Query execution cancelled.")
