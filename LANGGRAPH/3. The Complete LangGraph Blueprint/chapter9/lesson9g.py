from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

class State(TypedDict):
    amount: float

builder = StateGraph(State)

def define__transaction(state: State):
    print("Defining transaction...")
    return state

def verify_transaction(state: State):
    print(f"Verifying transaction amount: {state['amount']}")
    return state

builder.add_node("define_transaction", define__transaction)
builder.add_node("verify_transaction", verify_transaction)
builder.add_edge(START, "define_transaction")
builder.add_edge("define_transaction", "verify_transaction")
builder.add_edge("verify_transaction", END)

graph = builder.compile(interrupt_before=["verify_transaction"],checkpointer=MemorySaver())

initial_input = {"amount": 1000.0}
config = {"configurable": {"thread_id": "thread-1"}}

for event in graph.stream(initial_input, config):
    print(event)

approval = input("Approve this transaction? (yes/no): ")
if approval.lower() == "yes":
    for event in graph.stream(None, config):
        print(event)
else:
    print("Transaction cancelled.")
