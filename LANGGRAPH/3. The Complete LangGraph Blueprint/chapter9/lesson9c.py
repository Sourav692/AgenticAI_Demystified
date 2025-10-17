# Import necessary modules
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from display_graph import display_graph

# Define the tool: a web search function
@tool
def search(query: str):
    """Simulates a web search call."""
    return [
        f"The current weather in {query} is sunny and 75°F."
    ]

# Register the tool in the tool node
tools = [search]
tool_node = ToolNode(tools)

# Set up the AI model (simulated with ChatAnthropic)
model = ChatOpenAI(model="gpt-4o-mini")
model = model.bind_tools(tools)

# Define conditional logic to determine whether to continue or stop
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"  # No more tool calls, finish the graph
    else:
        return "continue"  # Otherwise, continue to next step

# Define the function that simulates reasoning and invokes the model
def agent_reasoning(state):
    messages = state["messages"]
    response = model.invoke(messages)
    # Append the model's response to the message history
    return {"messages": [response]}

# Build the React agent using LangGraph
workflow = StateGraph(MessagesState)

# Add nodes: agent reasoning and tool invocation
workflow.add_node("agent_reasoning", agent_reasoning)
workflow.add_node("call_tool", tool_node)

# Define the flow
workflow.add_edge(START, "agent_reasoning")  # Start with reasoning

# Conditional edges: if the agent should continue reasoning or stop
workflow.add_conditional_edges(
    "agent_reasoning", should_continue, {
        "continue": "call_tool",  # If the agent should proceed to the tool
        "end": END  # If no further steps are needed, end the workflow
    }
)

# Normal edge: after invoking the tool, return to agent reasoning
workflow.add_edge("call_tool", "agent_reasoning")

# Set up memory for breakpoints and add a breakpoint before calling the tool
memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["call_tool"])

# Display the graph
display_graph(app, file_name="react_agent_graph.png")

# Simulate user input for the agent
initial_input = {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]}
thread = {"configurable": {"thread_id": "1"}}

# Run the agent reasoning step first
for event in app.stream(initial_input, thread, stream_mode="values"):
    print(event)

# Before proceeding to tool invocation, pause for human intervention
user_approval = input("Do you approve invoking the web search tool? (yes/no): ")

if user_approval.lower() == "yes":
    # Continue with tool invocation
    for event in app.stream(None, thread, stream_mode="values"):
        print(event)
else:
    print("Execution halted by user.")
