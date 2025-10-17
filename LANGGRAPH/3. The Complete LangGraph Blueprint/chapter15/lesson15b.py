from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class DiagnosticState(TypedDict):
    symptoms: str
    diagnosis: str

def analyze_symptoms(state: DiagnosticState):
    if "slow" in state['symptoms']:
        state['diagnosis'] = "Possible network issue."
    elif "error" in state['symptoms']:
        state['diagnosis'] = "Check application logs for errors."
    else:
        state['diagnosis'] = "Further investigation needed."
    return state

# Define the workflow
builder = StateGraph(DiagnosticState)
builder.add_node("analyze_symptoms", analyze_symptoms)
builder.add_edge(START, "analyze_symptoms")
builder.add_edge("analyze_symptoms", END)
graph = builder.compile()

# Sample invocation
result = graph.invoke({"symptoms": "application slow response", "diagnosis": ""})
print(result)  # Output: {'symptoms': 'application slow response', 'diagnosis': 'Possible network issue.'}
