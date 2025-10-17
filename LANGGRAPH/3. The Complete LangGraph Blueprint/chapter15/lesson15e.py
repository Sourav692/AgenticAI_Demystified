from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import json

# Define the state with code_snippet and suggestion fields
class PairProgrammingState(TypedDict):
    code_snippet: str
    suggestion: str

# Initialize the ChatOpenAI tool for code analysis
llm_tool = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

# Define the AI-driven code analysis function
def analyze_code(state: PairProgrammingState):
    # Create a prompt for structured suggestions
    structured_prompt = (
        f"Analyze the following Python code snippet and provide suggestions for improvement. "
        f"Respond in JSON format with a 'suggestion' field.\n\n"
        f"Code snippet:\n{state['code_snippet']}\n\n"
        "Response format:\n"
        "{\n"
        "  \"suggestion\": \"<insert suggestion here>\"\n"
        "}"
    )
    human_message = HumanMessage(content=structured_prompt)

    # Send the HumanMessage to ChatOpenAI for analysis
    ai_message = llm_tool.invoke([human_message])

    # Parse the JSON response for the suggestion
    try:
        structured_response = json.loads(ai_message.content)
        state['suggestion'] = structured_response.get("suggestion", "No specific suggestions.")
    except json.JSONDecodeError:
        state['suggestion'] = "Error: Unable to parse the generated response."

    return state

# Define the workflow
builder = StateGraph(PairProgrammingState)
builder.add_node("analyze_code", analyze_code)
builder.add_edge(START, "analyze_code")
builder.add_edge("analyze_code", END)
graph = builder.compile()

# Sample invocation with a code snippet
result = graph.invoke({"code_snippet": "for i in range(len(arr)): print(arr[i])", "suggestion": ""})
print(result['suggestion'])  # Expected output: A dynamic suggestion, such as using enumerate()
