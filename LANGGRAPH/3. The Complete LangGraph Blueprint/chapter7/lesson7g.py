from langgraph.graph import StateGraph, MessagesState, START, END
from time import sleep
from langgraph.types import StreamWriter

# Define a custom node to simulate a long-running task
def long_running_node(state: MessagesState,  writer: StreamWriter):
    for i in range(1, 6):
        sleep(1)  # Simulate a delay
        writer({"progress": f"Processing step {i}/5"})

    return {"messages": ["Task completed!"]}

# Define the graph
workflow = StateGraph(MessagesState)
workflow.add_node("long_running_node", long_running_node)
workflow.add_edge(START, "long_running_node")
workflow.add_edge("long_running_node", END)

# Compile the graph
app = workflow.compile()

# Simulate interaction and stream custom progress updates
def simulate_interaction():
    input_message = {"messages": [("human", "Start the long-running task")]}
    
    for result in app.stream(input_message, stream_mode=["custom","updates"]):
        if "progress" in result[-1]:
            print(result[-1])  # Stream custom progress updates
        else:
            print(result[-1]) # Stream final message

simulate_interaction()
