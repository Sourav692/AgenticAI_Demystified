from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class TrafficState(TypedDict):
    traffic_density: int
    action: str

def traffic_prediction(state: TrafficState):
    if state['traffic_density'] > 70:
        state['action'] = 'Slow down'
    elif state['traffic_density'] > 40:
        state['action'] = 'Maintain speed'
    else:
        state['action'] = 'Speed up'
    return state

# Define the workflow
builder = StateGraph(TrafficState)
builder.add_node("traffic_prediction", traffic_prediction)
builder.add_edge(START, "traffic_prediction")
builder.add_edge("traffic_prediction", END)
graph = builder.compile()

# Sample invocation
result = graph.invoke({"traffic_density": 65, "action": ""})
print(result)  # Output: {'traffic_density': 65, 'action': 'Maintain speed'}
