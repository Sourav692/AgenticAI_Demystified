from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from pydantic import BaseModel

# Define the state with prompt and generated_code fields
class CodeGenState(TypedDict):
    prompt: str
    generated_code: str

# Initialize the ChatOpenAI tool for code generation
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

class CodeGen(BaseModel):
    """Code to generate"""
    generated_code: str


# Define the code generation function using ChatOpenAI and LangChain
def generate_code(state: CodeGenState):
    # Create a HumanMessage with the prompt
    human_message = HumanMessage(content=state['prompt'])

    # Send the HumanMessage to ChatOpenAI for code generation
    llm_tool = llm.with_structured_output(CodeGen)
    response = llm_tool.invoke([human_message])

    # Extract the generated code from the AIMessage
    state['generated_code'] = response.generated_code
    return state

# Define the workflow
builder = StateGraph(CodeGenState)
builder.add_node("generate_code", generate_code)
builder.add_edge(START, "generate_code")
builder.add_edge("generate_code", END)
graph = builder.compile()

# Sample invocation with a natural language prompt
result = graph.invoke({"prompt": "Write Python code for a complete LangGraph AI Agent for code generation graph using langchain_openai.", "generated_code": ""})
print(result['generated_code'])