import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI

# Define the state schema
class State(TypedDict):
    messages: Annotated[list, operator.add]
    
# Define the same nodes as before
def weather_node(state: State):
    return {"messages": ["It's 25°C and sunny."]}

def calculator_node(state: State):
    return {"messages": ["2 + 2 equals 4."]}

# Define the graph
workflow = StateGraph(State)
workflow.add_node("weather_node", weather_node)
workflow.add_node("calculator_node", calculator_node)

workflow.add_edge(START, "weather_node")
workflow.add_edge("weather_node", "calculator_node")
workflow.add_edge("calculator_node", END)

app = workflow.compile()

def simulate_interaction():
    input_message = {"messages": [("human", "Tell me the weather")]}
    
    # Stream updates after each node
    for result in app.stream(input_message, stream_mode="updates"):
        print(result)

simulate_interaction()
