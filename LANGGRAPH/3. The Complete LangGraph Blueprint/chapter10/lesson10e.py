import asyncio
from arxiv import Client, Search
import arxiv
from langchain_core.tools import tool
import operator
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from typing import Annotated, List, Tuple, Union, Optional
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver

# Enhanced tools with error handling and input validation
@tool
async def search_research_papers(topic: str) -> str:
    """Searches for research papers on a given topic using the Arxiv API."""
    fake_research_paper = "Langgraph is a graph-based workflow research paper."
    return fake_research_paper

@tool
def extract_data(paper_url: str) -> str:
    """Extracts relevant data from a research paper's URL."""
    # Mock implementation; in a real case, scrape or access paper content based on the URL
    return f"Extracted data from paper at {paper_url}."

@tool
def summarize_findings(data: str) -> str:
    """Summarizes findings from the extracted data."""
    return f"### Summary of Findings\n\n{data}\n\n---\n"

# Enhanced state management
class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: Optional[str]
    error: Optional[str]

class Plan(BaseModel):
    steps: List[str] = Field(description="Numbered unique steps to follow, in order")

class Response(BaseModel):
    response: str = Field(description="Response to user.")

class Act(BaseModel):
    action: Union[Response, Plan] = Field(description="Action to perform")

# Improved system prompts
SYSTEM_PROMPT = """YYou are a research assistant. 
Your task is to assist with research by gathering and summarizing information on a given topic ONLY using the available tools.

Always identify the topic from the input and use it consistently across all steps.

Available tools:
1. search_research_papers - Searches for research papers on a given topic.
2. extract_data - Extracts relevant data from a research paper's URL.
3. summarize_findings - Summarizes the findings based on extracted data.

Each response should be formatted in Markdown for readability."""

# Enhanced agent setup
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("placeholder", "{messages}")
])
tools = [search_research_papers, extract_data, summarize_findings]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent_executor = create_react_agent(llm, tools, state_modifier=prompt)

# Improved planning step
async def plan_step(state: PlanExecute) -> dict:
    try:
        planner_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("placeholder", "{messages}")
        ])
        planner = planner_prompt | llm.with_structured_output(Plan)
        plan = await planner.ainvoke({"messages": [("user", state["input"])]})
        return {"plan": plan.steps}
    except Exception as e:
        return {"error": f"Planning error: {str(e)}"}

# Improved execution step with error handling
async def execute_step(state: PlanExecute) -> dict:
    try:
        if "error" in state:
            return {"response": f"Workflow failed: {state['error']}"}
        
        plan = state["plan"]
        if not plan:
            return {"response": "No plan steps available to execute"}
            
        task = plan[0]
        agent_response = await agent_executor.ainvoke({"messages": [("user", task)]})
        return {"past_steps": [(task, agent_response["messages"][-1].content)]}
    except Exception as e:
        return {"error": f"Execution error: {str(e)}"}

# Enhanced replanning with better error handling
async def replan_step(state: PlanExecute) -> dict:
    try:
        if "error" in state:
            return {"response": f"Workflow failed: {state['error']}"}
            
        replanner_prompt = ChatPromptTemplate.from_template("""
            Given the objective: {input}
            Original plan: {plan}
            Completed steps: {past_steps}
            
            Please either:
            1. Provide next steps if more work is needed
            2. Provide a final response if the workflow is complete
            
            Only include steps that still need to be done.
            """)
        
        replanner = replanner_prompt | llm.with_structured_output(Act)
        output = await replanner.ainvoke(state)
        
        if isinstance(output.action, Response):
            return {"response": output.action.response}
        return {"plan": output.action.steps}
    except Exception as e:
        return {"error": f"Replanning error: {str(e)}"}

# Setup workflow
def create_workflow():
    workflow = StateGraph(PlanExecute)
    
    # Add nodes
    workflow.add_node("planner", plan_step)
    workflow.add_node("agent", execute_step)
    workflow.add_node("replan", replan_step)
    
    # Add edges
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "agent")
    workflow.add_edge("agent", "replan")
    workflow.add_conditional_edges(
        "replan",
        lambda s: END if ("response" in s or "error" in s) else "agent",
        [END]
    )
    
    return workflow.compile(checkpointer=MemorySaver())

async def run_workflow():
    app = create_workflow()
    config = {
        "configurable": {"thread_id": "1"},
        "recursion_limit": 50
    }
    
    inputs = {"input": f"LangGraph"}
    
    try:
        async for event in app.astream(inputs, config=config, stream_mode="values"):
            if "error" in event:
                print(f"Error: {event['error']}")
                break
            print(event)
    except Exception as e:
        print(f"Workflow execution failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_workflow())