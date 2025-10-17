
import os
import finnhub
from functools import partial
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
import operator


# Initialize the Finnhub client with your API key
finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))

# Set up LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Define Route Response structure for supervisor's decision
class RouteResponseFin(BaseModel):
    next: Literal["Portfolio_Analysis_Agent", "Market_Research_Agent", "Risk_Assessment_Agent", "FINISH"]

# Supervisor prompt
system_prompt_fin = (
    "You are a Financial Supervisor managing the following agents: Portfolio Analysis, Market Research, and Risk Assessment."
    " Select the next agent based on the user's query."
)
prompt_fin = ChatPromptTemplate.from_messages([
    ("system", system_prompt_fin),
    MessagesPlaceholder(variable_name="messages"),
    ("system", "Choose the next agent from: {options}.")
]).partial(options="['Portfolio_Analysis_Agent', 'Market_Research_Agent', 'Risk_Assessment_Agent', 'FINISH']")

# Supervisor Agent Function
def supervisor_agent_fin(state):
    supervisor_chain_fin = prompt_fin | llm.with_structured_output(RouteResponseFin)
    return supervisor_chain_fin.invoke(state)

# Define Agent Node Function
def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["messages"][-1].content, name=name)]}

# Portfolio Analysis Agent
def portfolio_analysis(query):
    """Fetch basic financial metrics using Finnhub API"""
    try:
        stock_symbol = query.split()[-1]
        financials = finnhub_client.company_basic_financials(stock_symbol, 'all')
        metrics = financials.get('metric', {})
        response = (
            f"Portfolio Analysis for {stock_symbol}: P/E Ratio: {metrics.get('peRatio')}, "
            f"Revenue Growth: {metrics.get('revenueGrowth')}, "
            f"52-Week High: {metrics.get('52WeekHigh')}, 52-Week Low: {metrics.get('52WeekLow')}"
        )
        return response
    except Exception as e:
        return f"Error in fetching portfolio data: {str(e)}"

portfolio_agent = create_react_agent(llm, tools=[portfolio_analysis], state_modifier="Portfolio Analysis Agent")
portfolio_analysis_node = partial(agent_node, agent=portfolio_agent, name="Portfolio_Analysis_Agent")

# Market Research Agent
def market_research(query):
    """ Get latest market news and sentiment """
    news = finnhub_client.general_news("general")
    top_news = news[:3]  # Retrieve top 3 news items for brevity
    response = "Latest Market News:\n" + "\n".join(
        f"{item['headline']} - {item['source']} ({item['url']})" for item in top_news
    )
    return response

market_research_agent = create_react_agent(llm, tools=[market_research], state_modifier="Market Research Agent")
market_research_node = partial(agent_node, agent=market_research_agent, name="Market_Research_Agent")

# Risk Assessment Agent
def risk_assessment(query):
    """ Perform basic risk evaluation using volatility metrics (example)"""
    try:
        stock_symbol = query.split()[-1]
        quote = finnhub_client.quote(stock_symbol)
        price_change = quote.get("dp", 0)
        risk_level = "High Risk" if abs(price_change) > 5 else "Moderate Risk" if abs(price_change) > 2 else "Low Risk"
        return f"Risk Assessment for {stock_symbol}: Price Change: {price_change}%, Risk Level: {risk_level}"
    except Exception as e:
        return f"Error in assessing risk: {str(e)}"

risk_assessment_agent = create_react_agent(llm, tools=[risk_assessment], state_modifier="Risk Assessment Agent")
risk_assessment_node = partial(agent_node, agent=risk_assessment_agent, name="Risk_Assessment_Agent")

# Define Workflow State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

# Set up the Workflow
workflow_fin = StateGraph(AgentState)
workflow_fin.add_node("Portfolio_Analysis_Agent", portfolio_analysis_node)
workflow_fin.add_node("Market_Research_Agent", market_research_node)
workflow_fin.add_node("Risk_Assessment_Agent", risk_assessment_node)
workflow_fin.add_node("supervisor", supervisor_agent_fin)

# Define routing for agents to return to the supervisor
for member in ["Portfolio_Analysis_Agent", "Market_Research_Agent", "Risk_Assessment_Agent"]:
    workflow_fin.add_edge(member, "supervisor")

# Define the supervisor’s routing decisions
conditional_map_fin = {
    "Portfolio_Analysis_Agent": "Portfolio_Analysis_Agent",
    "Market_Research_Agent": "Market_Research_Agent",
    "Risk_Assessment_Agent": "Risk_Assessment_Agent",
    "FINISH": END
}
workflow_fin.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map_fin)
workflow_fin.add_edge(START, "supervisor")

# Compile the workflow
graph_fin = workflow_fin.compile()

# Test with Example Query
inputs_fin = {"messages": [HumanMessage(content="Analyze the portfolio for AAPL.")]}
for output in graph_fin.stream(inputs_fin, stream_mode="values"):
    print(output)
