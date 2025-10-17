# Import necessary libraries
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode


# Define tools
@tool
def play_song_on_spotify(song: str):
    """Play a song on Spotify."""
    return f"Successfully played {song} on Spotify!"

@tool
def play_song_on_apple(song: str):
    """Play a song on Apple Music."""
    return f"Successfully played {song} on Apple Music!"

# List of tools
tools = [play_song_on_apple, play_song_on_spotify]
tool_node = ToolNode(tools)

# Set up model
model = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

# Define model-calling function
def call_model(state):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# Define continuation logic
def should_continue(state):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "continue"
    return "end"

# Build the graph
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Define graph flow
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, {"continue": "action", "end": END})
workflow.add_edge("action", "agent")

# Set up memory for checkpointing
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

from langchain_core.messages import HumanMessage

config = {"configurable": {"thread_id": "1"}}
input_message = HumanMessage(content="Can you play Taylor Swift's most popular song?")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    print(event["messages"][-1].pretty_print())


# View state history
print("--- State History ---"+ "\n\n\n")
all_states = []
state_history = app.get_state_history(config)
for state in state_history:
    all_states.append(state)
    print(state)

# Replay from a previous state
replay_state = all_states[2]  # Replay right before tool execution
print("Replaying from state" + " " + str(replay_state) + "\n\n\n")
print("--- Replayed State ---"+ "\n\n\n")
for event in app.stream(None, replay_state.config):
    for v in event.values():
        print(v)
        print("\n\n\n")

print("--- Branching off Past States---")
# Get the last message with the tool call
last_message = replay_state.values["messages"][-1]

# Update the tool call from Apple Music to Spotify
last_message.tool_calls[0]["name"] = "play_song_on_spotify"

# Update the state and resume execution
branch_config = app.update_state(replay_state.config, {"messages": [last_message]})
for event in app.stream(None, branch_config):
    print(event)

