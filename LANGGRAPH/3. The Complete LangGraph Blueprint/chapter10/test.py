import asyncio
from langchain_core.tools import tool
import operator
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from typing import Annotated, List, Tuple, Union
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

@tool
def validate_expense_report(report_id: str):
    """Validates an employee's expense report."""
    return f"Expense report {report_id} is valid."

@tool
def check_policy_compliance(report_id: str):
    """Checks whether the report complies with company policy."""
    return f"Report {report_id} complies with company policy."

@tool
def route_to_manager(report_id: str):
    """Routes the report to the manager for approval."""
    return f"Report {report_id} has been routed to the manager."

@tool
def notify_employee(report_id: str, status: str):
    """Notifies the employee of the report's status."""
    return f"Employee notified that report {report_id} is {status}."

tools = [validate_expense_report, check_policy_compliance, route_to_manager, notify_employee]

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant that processes expense reports. 
    When using tools, make sure to include the required parameters.
    For example:
    - validate_expense_report(report_id)
    - check_policy_compliance(report_id)
    - route_to_manager(report_id)
    - notify_employee(report_id, status)
    
    Always extract the report ID from the user's request and use it in the tools."""),
    ("placeholder", "{messages}")
])

llm = ChatOpenAI(model="gpt-4")
agent_executor = create_react_agent(llm, tools, state_modifier=prompt)

class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str
    
class Plan(BaseModel):
    steps: List[str] = Field(description="Numbered unique steps to follow, in order")

class Response(BaseModel):
    response: str = Field(description="Response to user.")

class Act(BaseModel):
    action: Union[Response, Plan] = Field(description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan.")

# Planning step for workflow
planner_prompt = ChatPromptTemplate.from_messages([
    ("system", """Create a step-by-step plan to process and approve expense reports.
    Use ONLY the following tools with their exact parameters:
    1. validate_expense_report(report_id)
    2. check_policy_compliance(report_id)
    3. route_to_manager(report_id)
    4. notify_employee(report_id, status)
    
    Make sure each step includes the specific report ID from the user's request."""),
    ("placeholder", "{messages}")
])

planner = planner_prompt | ChatOpenAI(model="gpt-4", temperature=0).with_structured_output(Plan)

async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke({"messages": [("user", state["input"])]})
    return {"plan": plan.steps}

async def execute_step(state: PlanExecute):
    plan = state["plan"]
    task = plan[0]
    # Extract report ID from the input
    report_id = "12345"  # In this case it's hardcoded from the input
    
    # Modify the task to include the report ID if it's not present
    if "report_id" not in task.lower():
        if "validate" in task.lower():
            task = f"validate_expense_report('{report_id}')"
        elif "compliance" in task.lower():
            task = f"check_policy_compliance('{report_id}')"
        elif "route" in task.lower():
            task = f"route_to_manager('{report_id}')"
        elif "notify" in task.lower():
            task = f"notify_employee('{report_id}', 'processed')"

    agent_response = await agent_executor.ainvoke({"messages": [("user", task)]})
    return {"past_steps": [(task, agent_response["messages"][-1].content)]}

# Re-planning step
replanner_prompt = ChatPromptTemplate.from_template(
    """For the given objective, come up with a simple step by step numbered plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

Your objective was this:
{input}

Your original plan was this:
{plan}

You have currently done the follow steps:
{past_steps}

Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan."""
)

replanner = replanner_prompt | ChatOpenAI(model="gpt-4", temperature=0).with_structured_output(Act)

async def replan_step(state: PlanExecute):
    output = await replanner.ainvoke(state)
    if isinstance(output.action, Response):
        return {"response": output.action.response}
    return {"plan": output.action.steps}

# Create and configure the workflow
workflow = StateGraph(PlanExecute)
workflow.add_node("planner", plan_step)
workflow.add_node("agent", execute_step)
workflow.add_node("replan", replan_step)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "agent")
workflow.add_edge("agent", "replan")
workflow.add_conditional_edges(
    "replan",
    lambda s: END if "response" in s else "agent",
    [END]
)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}, "recursion_limit": 50}

async def run_plan_and_execute():
    inputs = {"input": "Validate and process the expense report with report ID 12345."}
    async for event in app.astream(inputs, config=config, stream_mode="values"):
        print(event)

if __name__ == "__main__":
    asyncio.run(run_plan_and_execute())