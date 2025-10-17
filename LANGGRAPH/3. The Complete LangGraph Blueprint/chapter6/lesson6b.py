from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the LLM (using OpenAI's GPT-4o-mini)
model = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

# Node function to handle the user query and call the LLM
def call_llm(state: MessagesState):
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

# Define the graph
workflow = StateGraph(MessagesState)

# Add the node to call the LLM
workflow.add_node("call_llm", call_llm)

# Define the edges (start -> LLM -> end)
workflow.add_edge(START, "call_llm")
workflow.add_edge("call_llm", END)

# Initialize the MemorySaver checkpointer
checkpointer = MemorySaver()

# Compile the workflow with short-term memory
app_with_memory = workflow.compile(checkpointer=checkpointer)

# Function to simulate interacting with the agent across sessions
def interact_with_agent_across_sessions():
    while True:
        # Simulate a new session by allowing the user to input a thread ID
        thread_id = input("Enter thread ID (or 'new' for a new session): ")
        if thread_id.lower() in ["exit", "quit"]:
            print("Ending the conversation.")
            break
        
        if thread_id.lower().strip() == "new":
            thread_id = f"session_{os.urandom(4).hex()}"  # Generate a unique session ID
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "end session"]:
                print(f"Ending session {thread_id}.")
                break
            
            input_message = {
                "messages": [("human", user_input)]
            }

            # Invoke the graph with the correct thread ID to maintain memory across sessions
            config = {"configurable": {"thread_id": thread_id}}
            for chunk in app_with_memory.stream(input_message, config=config, stream_mode="values"):
                chunk["messages"][-1].pretty_print()

# Start interacting with the memory-persistent agent
interact_with_agent_across_sessions()
