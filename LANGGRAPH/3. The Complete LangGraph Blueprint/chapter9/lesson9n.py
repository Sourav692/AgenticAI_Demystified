import os
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool

from display_graph import display_graph

# Define the state structure
class State(TypedDict):
    input: str
    user_feedback: str

# Define a reasoning step for the agent
def agent_reasoning(state: State):
    print(f"Agent is reasoning: {state['input']}")
    # Agent decides whether to ask human based on input length
    if len(state["input"]) > 10:
        print("Agent needs clarification.")
        return state
    else:
        state["user_feedback"] = "No clarification needed"
        return state

# Define a human feedback step
def ask_human(state: State):
    print("--- Asking for human feedback ---")
    feedback = input("Please provide feedback on the input: ")
    state['user_feedback'] = feedback
    return state

# Define a tool action after human feedback
@tool
def perform_action(user_feedback: str):
    """
    Perform an action based on the provided user feedback.
    """
    print(f"Action taken based on feedback: {user_feedback}")
    return {"user_feedback": f"Feedback processed: {user_feedback}"}

# Build the graph
builder = StateGraph(State)
builder.add_node("agent_reasoning", agent_reasoning)
builder.add_node("ask_human", ask_human)
builder.add_node("perform_action", perform_action)

# Define flow with conditions
builder.add_edge(START, "agent_reasoning")
builder.add_conditional_edges(
    "agent_reasoning", 
    lambda state: "ask_human" if len(state["input"]) > 10 else "perform_action",
    {"ask_human": "ask_human", "perform_action": "perform_action"}
)
builder.add_edge("ask_human", "perform_action")
builder.add_edge("perform_action", END)

# Set up memory and breakpoints
memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["ask_human"])

# Display the graph
display_graph(graph, file_name=os.path.basename(__file__))

# Run the graph
initial_input = {"input": "Proceed with reasoning?"}
thread = {"configurable": {"thread_id": "1"}}

# Stream the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="values"):
    print(event)

# Get user input and update the state
user_feedback = input("User feedback: ")
graph.update_state(thread, {"user_feedback": user_feedback}, as_node="ask_human")

# Resume execution after feedback
for event in graph.stream(None, thread, stream_mode="values"):
    print(event)
