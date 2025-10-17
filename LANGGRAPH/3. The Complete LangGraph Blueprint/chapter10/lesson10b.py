import operator
import os
import platform
import subprocess
import psutil
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from typing import Annotated, List, Tuple, Union
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

# Define diagnostic and action tools
@tool
def check_cpu_usage():
    """Checks the actual CPU usage."""
    cpu_usage = psutil.cpu_percent(interval=1)
    return f"CPU Usage is {cpu_usage}%."

@tool
def check_disk_space():
    """Checks actual disk space."""
    disk_usage = psutil.disk_usage('/').percent
    return f"Disk space usage is at {disk_usage}%."

@tool
def check_network():
    """Checks network connectivity by pinging a reliable server."""
    response = subprocess.run(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.PIPE)
    if response.returncode == 0:
        return "Network connectivity is stable."
    else:
        return "Network connectivity issue detected."

@tool
def restart_server():
    """Restarts the server with an OS-independent approach."""
    current_os = platform.system()
    
    try:
        if current_os == "Windows":
            os.system("shutdown /r /t 0")  # Windows restart command
        elif current_os == "Linux" or current_os == "Darwin":  # Darwin is macOS
            os.system("sudo shutdown -r now")  # Linux/macOS restart command
        else:
            return "Unsupported operating system for server restart."
        return "Server restart initiated successfully."
    except Exception as e:
        return f"Failed to restart server: {e}"

# Tools setup
tools = [check_cpu_usage, check_disk_space, check_network, restart_server]

# Enhanced system prompt with clear decision-making guidelines
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an IT diagnostics agent. Follow these guidelines:
    1. Check metrics in order: CPU -> Disk -> Network
    2. Analysis thresholds:
       - CPU Usage > 80%: Critical
       - Disk Space < 15%: Critical
       - Network: Must be stable
    3. Take action:
       - If any metric is critical, recommend server restart
       - If all metrics normal, report healthy status
    4. Never repeat checks unless explicitly needed
    5. After server restart, perform one final check to verify improvement"""),
    ("placeholder", "{messages}")
])

llm = ChatOpenAI(model="gpt-4o-mini")
agent_executor = create_react_agent(llm, tools, state_modifier=prompt)

# Modified state structure to track check history and results
class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str
    checks_complete: bool
    restart_performed: bool
    final_check: bool
    messages: Annotated[List[str], operator.add]  # Add messages to track each step and result

class Plan(BaseModel):
    steps: List[str] = Field(description="Tasks to check and resolve server issues")

class Response(BaseModel):
    response: str

class Act(BaseModel):
    action: Union[Response, Plan] = Field(description="Action to perform")

# Enhanced planning prompt with better context awareness
planner_prompt = ChatPromptTemplate.from_messages([
    ("system", """Create a focused diagnostic plan:
    1. Only include necessary checks
    2. Track what's already been checked
    3. Include restart if thresholds exceeded
    4. One final verification after restart
    Available tools: check_cpu_usage, check_disk_space, check_network, restart_server"""),
    ("placeholder", "{messages}"),
])

planner = planner_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Plan)

# Improved replanning logic
replanner_prompt = ChatPromptTemplate.from_template("""
Analyze the current situation and determine next steps:

Task: {input}
Completed steps: {past_steps}
Checks complete: {checks_complete}
Restart performed: {restart_performed}
Final check: {final_check}

Rules:
1. Don't repeat checks unless verifying after restart
2. If CPU > 80% or Disk < 15%, proceed to restart
3. After restart, do one final check
4. End process after final verification

Available tools:
- check_cpu_usage
- check_disk_space
- check_network
- restart_server
""")

replanner = replanner_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Act)

# Enhanced execution step with state tracking
async def execute_step(state: PlanExecute):
    if not state.get("checks_complete"):
        state["checks_complete"] = False
    if not state.get("restart_performed"):
        state["restart_performed"] = False
    if not state.get("final_check"):
        state["final_check"] = False
    
    plan = state["plan"]
    if not plan:
        return state
        
    task = plan[0]
    tool_map = {
        "check_cpu_usage": check_cpu_usage,
        "check_disk_space": check_disk_space,
        "check_network": check_network,
        "restart_server": restart_server
    }
    
    if task in tool_map:
        result = tool_map[task].invoke({})
        state["past_steps"].append((task, result))
        state["messages"].append(f"Executed {task}: {result}")  # Log the message here
        state["plan"] = state["plan"][1:]
        
        # Update state flags based on actions
        if task == "restart_server":
            state["restart_performed"] = True
        elif state["restart_performed"] and not state["final_check"]:
            state["final_check"] = True
            
        # Check if all initial checks are complete
        if len(state["past_steps"]) >= 3 and not state["checks_complete"]:
            state["checks_complete"] = True
            
    return state

# Initial planning step
async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke({"messages": [("user", state["input"])]})
    state["plan"] = plan.steps
    state["messages"].append(f"Planned {plan}: {plan.steps}")  # Log the message here
    state["checks_complete"] = False
    state["restart_performed"] = False
    state["final_check"] = False
    return state

# Enhanced replanning with better decision making
async def replan_step(state: PlanExecute):
    output = await replanner.ainvoke(state)
    
    if isinstance(output.action, Response):
        return {"response": output.action.response}
    
    # Avoid repeating checks unless doing final verification
    if state["restart_performed"] and not state["final_check"]:
        state["plan"] = ["check_cpu_usage", "check_disk_space", "check_network"]
    else:
        state["plan"] = [step for step in output.action.steps 
                        if step not in [s[0] for s in state["past_steps"]] or
                        (state["restart_performed"] and not state["final_check"])]
    
    return state

# Enhanced end condition check
def should_end(state: PlanExecute):
    # End conditions:
    # 1. All checks complete and no issues found
    # 2. Restart performed and final check complete
    # 3. Maximum steps reached (safety check)
    if (state["checks_complete"] and not state["plan"]) or \
       (state["restart_performed"] and state["final_check"]) or \
       len(state["past_steps"]) > 15:  # Safety limit
        return END
    return "agent"

# Build the workflow
workflow = StateGraph(PlanExecute)
workflow.add_node("planner", plan_step)
workflow.add_node("agent", execute_step)
workflow.add_node("replan", replan_step)

workflow.add_edge(START, "planner")
workflow.add_edge("planner", "agent")
workflow.add_edge("agent", "replan")
workflow.add_conditional_edges("replan", should_end, ["agent", END])

app = workflow.compile()

# Example usage
async def run_plan_and_execute():
    inputs = {
        "input": "Diagnose the server issue and restart if necessary.",
        "past_steps": [],
        "checks_complete": False,
        "restart_performed": False,
        "final_check": False,
        "messages": []  # Initialize an empty list for messages
    }
    config = {"recursion_limit": 15}
    
    async for event in app.astream(inputs, config=config):
        print(event)
        print("\n\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_plan_and_execute())