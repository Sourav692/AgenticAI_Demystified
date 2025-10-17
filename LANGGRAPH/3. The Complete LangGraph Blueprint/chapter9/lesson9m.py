from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Define the state structure
class State(TypedDict):
    input: str
    user_feedback: str

# Define node functions
def step_1(state: State):
    print(f"Step 1: {state['input']}")
    return state

def human_feedback(state: State):
    print("--- Waiting for human feedback ---")
    feedback = input("Please provide your feedback: ")
    state['user_feedback'] = feedback
    return state

def step_3(state: State):
    print(f"Step 3: User feedback received: {state['user_feedback']}")
    return state

# Build the graph
builder = StateGraph(State)
builder.add_node("step_1", step_1)
builder.add_node("human_feedback", human_feedback)
builder.add_node("step_3", step_3)

# Define the flow
builder.add_edge(START, "step_1")
builder.add_edge("step_1", "human_feedback")
builder.add_edge("human_feedback", "step_3")
builder.add_edge("step_3", END)

# Set up memory and breakpoints
memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["human_feedback"])

# Run the graph
initial_input = {"input": "Proceed with workflow?"}
thread = {"configurable": {"thread_id": "1"}}

# Stream the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="values"):
    print(event)

# Get user input and update the state
user_feedback = input("User feedback: ")
graph.update_state(thread, {"user_feedback": user_feedback}, as_node='human_feedback')

# Resume execution
for event in graph.stream(None, thread, stream_mode="values"):
    print(event)
