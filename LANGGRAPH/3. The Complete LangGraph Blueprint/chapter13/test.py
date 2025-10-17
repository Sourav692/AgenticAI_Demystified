from typing import Annotated
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.tools import PythonREPLTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Literal

# Initialize tools
tavily_tool = TavilySearchResults(max_results=5)
python_repl_tool = PythonREPLTool()

from langchain_core.messages import HumanMessage

def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {
        "messages": [HumanMessage(content=result["messages"][-1].content, 
                                name=name)]
    }

# Define team members
members = ["Researcher", "Coder"]

# System prompt for the supervisor
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    " following workers: {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)

# Define possible options for the supervisor
options = ["FINISH"] + members

class routeResponse(BaseModel):
    next: Literal[*options]

# Create the supervisor's prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Given the conversation above, who should act next?"
            " Or should we FINISH? Select one of: {options}",
        ),
    ]
).partial(options=str(options), members=", ".join(members))

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Define the supervisor agent function
def supervisor_agent(state):
    supervisor_chain = prompt | llm.with_structured_output(routeResponse)
    return supervisor_chain.invoke(state)

import functools
import operator
from typing import Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import create_react_agent

# Define the agent state structure
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

# Create the research and coding agents
research_agent = create_react_agent(llm, tools=[tavily_tool])
research_node = functools.partial(agent_node, agent=research_agent, 
                                name="Researcher")

code_agent = create_react_agent(llm, tools=[python_repl_tool])
code_node = functools.partial(agent_node, agent=code_agent, name="Coder")

# Build the workflow graph
workflow = StateGraph(AgentState)
workflow.add_node("Researcher", research_node)
workflow.add_node("Coder", code_node)
workflow.add_node("supervisor", supervisor_agent)

# Add edges for worker nodes to report back to supervisor
for member in members:
    workflow.add_edge(member, "supervisor")

# Add conditional edges based on supervisor's decisions
conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
workflow.add_conditional_edges(
    "supervisor", 
    lambda x: x["next"],
    conditional_map
)

# Add the entry point
workflow.add_edge(START, "supervisor")

# Compile the graph
graph = workflow.compile()

# Example usage
for s in graph.stream(
    {
        "messages": [
            HumanMessage(content="Research recent advances in AI and summarize.")
        ]
    }
):
    if "__end__" not in s:
        print(s)
        print("----")