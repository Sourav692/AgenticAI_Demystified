from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
import uuid

# Initialize the in-memory store
in_memory_store = InMemoryStore()

# Function to store user information
def store_user_info(state: MessagesState, config, *, store=in_memory_store):
    user_id = config["configurable"]["user_id"]
    namespace = (user_id, "memories")
    memory_id = str(uuid.uuid4())
    memory = {"user_name": state["user_name"]}
    store.put(namespace, memory_id, memory)
    return {"messages": ["User information saved."]}

# Function to retrieve stored user information
def retrieve_user_info(state: MessagesState, config, *, store=in_memory_store):
    user_id = config["configurable"]["user_id"]
    namespace = (user_id, "memories")
    memories = store.search(namespace)
    if memories:
        info = f"Hello {memories[-1].value['user_name']}, welcome back!"
    else:
        info = "I don't have any information about you yet."
    return {"messages": [info]}

# Function to manage user input and memory storage/retrieval
def call_model(state: MessagesState, config):
    last_message = state["messages"][-1].content.lower()
    
    # Store the user's name
    if "remember my name" in last_message:
        user_name = last_message.split("remember my name is")[-1].strip()
        state["user_name"] = user_name
        return store_user_info(state, config)
    
    # Retrieve the user's name
    if "what's my name" in last_message or "what is my name" in last_message:
        return retrieve_user_info(state, config)
    
    # Default LLM response for other inputs
    return {"messages": ["I didn't understand your request."]}


# Define the graph workflow
workflow = StateGraph(MessagesState)
workflow.add_node("call_model", call_model)
workflow.add_edge(START, "call_model")
workflow.add_edge("call_model", END)

# Compile the graph with both checkpointer and memory store
app_with_memory = workflow.compile(checkpointer=MemorySaver(), store=in_memory_store)

def simulate_sessions():
    # First session: store user's name
    config = {"configurable": {"thread_id": "session_1", "user_id": "user_123"}}
    input_message = {"messages": [("human", "Remember my name is Alice")]}
    for chunk in app_with_memory.stream(input_message, config=config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()
    
    # Second session: retrieve user's name
    config = {"configurable": {"thread_id": "session_2", "user_id": "user_123"}}
    input_message = {"messages": [("human", "What's my name?")]}
    for chunk in app_with_memory.stream(input_message, config=config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

simulate_sessions()


