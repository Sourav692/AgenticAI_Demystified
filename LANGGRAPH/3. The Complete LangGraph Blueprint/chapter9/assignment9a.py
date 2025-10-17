# Import necessary components
import os
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from display_graph import display_graph

# Define tools for the agent
@tool
def search(query: str):
    """Call to search the web and fetch data."""
    # Simulate searching the web
    return f"I looked up: {query}. Result: It's sunny in San Francisco, but you better look out if you're a Gemini 😈."

# Define the human feedback tool
class AskHuman(BaseModel):
    """Simulates asking a human a question."""
    question: str

# Set up the tools and tool nodes
tools = [search]
tool_node = ToolNode(tools)

# Set up the AI model
model = ChatOpenAI(model="gpt-4o")

# Bind the model to tools including the ask_human tool
model = model.bind_tools(tools + [AskHuman])

# Define functions for the agent

# Function to decide the next step based on the last message
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    
    # If no tool call, finish the process
    if not last_message.tool_calls:
        return "end"
    
    # If the tool call is AskHuman, return that node
    elif last_message.tool_calls[0]["name"] == "AskHuman":
        return "ask_human"
    
    # Otherwise, continue the workflow
    else:
        return "continue"

# Function to call the model and return the response
def call_model(state):
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

# Define the human interaction node
def ask_human(state):
    pass  # No actual processing here, this is handled as a breakpoint

# Build the workflow graph

# Create the state graph
workflow = StateGraph(MessagesState)

# Define the nodes for the workflow
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)
workflow.add_node("ask_human", ask_human)

# Set the starting node
workflow.add_edge(START, "agent")

# Define conditional edges based on the agent's output
workflow.add_conditional_edges(
    "agent", 
    should_continue, 
    {
        "continue": "action",  # Proceed to the tool action
        "ask_human": "ask_human",  # Ask human for input
        "end": END,  # Finish the process
    }
)

# Add the edge from action back to agent for continued workflow
workflow.add_edge("action", "agent")

# Add the edge from ask_human back to agent after human feedback
workflow.add_edge("ask_human", "agent")

# Set up memory for checkpointing
memory = MemorySaver()

# Compile the graph with a breakpoint before ask_human
app = workflow.compile(checkpointer=memory, interrupt_before=["ask_human"])

# Visualize the workflow
display_graph(app, file_name=os.path.basename(__file__))

from langchain_core.messages import HumanMessage

# Initial configuration and user message
config = {"configurable": {"thread_id": "2"}}
input_message = HumanMessage(
    content="Use the search tool to ask the user where they are, then look up the weather there"
)

# Start the interaction with the agent
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()

# Get the ID of the last tool call (AskHuman tool call)
tool_call_id = app.get_state(config).values["messages"][-1].tool_calls[0]["id"]

# Create the tool response message
tool_message = [
    {"tool_call_id": tool_call_id, "type": "tool", "content": "San Francisco"}
]

# Update the state as if the response came from the user
app.update_state(config, {"messages": tool_message}, as_node="ask_human")

# Continue the agent's workflow
for event in app.stream(None, config, stream_mode="values"):
    event["messages"][-1].pretty_print()




