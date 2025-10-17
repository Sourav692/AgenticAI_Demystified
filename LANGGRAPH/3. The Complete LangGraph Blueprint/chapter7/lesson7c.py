import operator
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict

# Define the state schema
class State(TypedDict):
    messages: Annotated[list, operator.add]

# Define a node to handle weather queries
def weather_node(state: State):
    return {"messages": ["The weather is sunny and 25°C."]}

# Define a node to handle calculator queries
def calculator_node(state: State):
    return {"messages": ["The result of 2 + 2 is 4."]}

# Define the workflow graph
workflow = StateGraph(State)
workflow.add_node("weather_node", weather_node)
workflow.add_node("calculator_node", calculator_node)

# Set the edges for the graph
workflow.add_edge(START, "weather_node")
workflow.add_edge("weather_node", "calculator_node")
workflow.add_edge("calculator_node", END)

# Compile the workflow
app = workflow.compile()

# Simulate interaction and stream the full state
def simulate_interaction():
    input_message = {"messages": [("human", "Tell me the weather")]}
    
    # Stream the full state of the graph
    for result in app.stream(input_message, stream_mode="values"):
        print(result)  # Print the full state after each node

simulate_interaction()
