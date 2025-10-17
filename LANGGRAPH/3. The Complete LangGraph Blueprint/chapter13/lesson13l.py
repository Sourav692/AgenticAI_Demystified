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
    next: Literal["Portfolio_Analysis_Agent", "Market_Research_Agent", 
                 "Risk_Assessment_Agent", "FINISH"]

# Supervisor prompt
system_prompt_fin = """
You are a Financial Supervisor managing a team of specialized agents:
- Portfolio Analysis Agent: Analyzes financial metrics and portfolio performance
- Market Research Agent: Researches market trends and news
- Risk Assessment Agent: Evaluates investment risks

Based on the user's query, select the most appropriate agent to handle the request.
For complete analysis, you may need to use multiple agents in sequence.
"""

prompt_fin = ChatPromptTemplate.from_messages([
    ("system", system_prompt_fin),
    MessagesPlaceholder(variable_name="messages"),
    ("system", "Choose the next agent from: {options}. Select FINISH only when "
              "all necessary analysis is complete.")
]).partial(options="['Portfolio_Analysis_Agent', 'Market_Research_Agent', "
           "'Risk_Assessment_Agent', 'FINISH']")

# Supervisor Agent Function
def supervisor_agent_fin(state):
    supervisor_chain_fin = prompt_fin | llm.with_structured_output(RouteResponseFin)
    print("\nSupervisor evaluating next action...")
    return supervisor_chain_fin.invoke(state)

# Define Agent Node Function with improved logging
def agent_node(state, agent, name):
    print(f"\nExecuting {name}...")
    try:
        result = agent.invoke(state)
        print(f"{name} completed successfully")
        return {
            "messages": [HumanMessage(content=result["messages"][-1].content, 
                                    name=name)]
        }
    except Exception as e:
        error_message = f"{name} encountered an error: {str(e)}"
        print(error_message)
        return {
            "messages": [HumanMessage(content=error_message, name=name)]
        }

def extract_symbol(query):
    """Extract stock symbol from query that could be string or dict"""
    try:
        if isinstance(query, dict):
            return query.get('symbol', '').upper()
        elif isinstance(query, str):
            # Extract last word from string query
            words = query.split()
            return words[-1].upper()
        else:
            raise ValueError(f"Unsupported query format: {type(query)}")
    except Exception as e:
        print(f"Error extracting symbol: {e}")
        return None

# Portfolio Analysis Function
def portfolio_analysis(query):
    """Fetch comprehensive financial metrics using Finnhub API"""
    try:
        stock_symbol = extract_symbol(query)
        # Get company profile
        profile = finnhub_client.company_profile2(symbol=stock_symbol)
        # Get basic financials
        financials = finnhub_client.company_basic_financials(stock_symbol, 'all')
        metrics = financials.get('metric', {})
        # Get current quote
        quote = finnhub_client.quote(stock_symbol)
        
        response = f"""
Portfolio Analysis for {stock_symbol} ({profile.get('name', 'Unknown Company')}):

Financial Metrics:
- Current Price: ${quote.get('c', 'N/A')}
- P/E Ratio: {metrics.get('peTTM', 'N/A')}
- Revenue Growth: {metrics.get('revenueGrowthTTM', 'N/A')}
- Market Cap: ${profile.get('marketCapitalization', 'N/A')}
- 52-Week Range: ${metrics.get('52WeekLow', 'N/A')} - ${metrics.get('52WeekHigh', 'N/A')}

Key Performance Indicators:
- Beta: {metrics.get('beta', 'N/A')}
- Dividend Yield: {metrics.get('dividendYieldIndicatedAnnual', 'N/A')}%
- Profit Margin: {metrics.get('grossMarginTTM', 'N/A')}%
- Debt to Equity: {metrics.get('totalDebtToEquityQuarterly', 'N/A')}
"""
        return response
    except Exception as e:
        return f"Error in portfolio analysis for {stock_symbol}: {str(e)}"

# Market Research Function
def market_research(query):
    """Get latest market news and comprehensive sentiment analysis"""
    try:
        stock_symbol = extract_symbol(query)
        # Get company news
        news = finnhub_client.company_news(stock_symbol, 
                                         _from="2024-01-01", 
                                         to="2024-12-31")
        # Get sentiment data
        sentiment = finnhub_client.news_sentiment(stock_symbol)
        
        response = f"""
Market Research for {stock_symbol}:

Recent News Headlines:
"""
        # Add recent news
        for i, article in enumerate(news[:3], 1):
            response += f"{i}. {article.get('headline', 'N/A')}\n"
            response += f"   Summary: {article.get('summary', 'N/A')[:100]}...\n\n"
        
        # Add sentiment analysis
        response += f"""
Market Sentiment Analysis:
- Overall Sentiment Score: {sentiment.get('companyNewsScore', 'N/A')}
- Bullish Articles: {sentiment.get('buzz', {}).get('bullishPercent', 'N/A')}%
- Bearish Articles: {sentiment.get('buzz', {}).get('bearishPercent', 'N/A')}%
- News Volume: {sentiment.get('buzz', {}).get('weeklyAverage', 'N/A')} articles/week
"""
        return response
    except Exception as e:
        return f"Error in market research for {stock_symbol}: {str(e)}"

# Risk Assessment Function
def risk_assessment(query):
    """Perform comprehensive risk evaluation"""
    try:
        stock_symbol = extract_symbol(query)
        quote = finnhub_client.quote(stock_symbol)
        metrics = finnhub_client.company_basic_financials(stock_symbol, 
                                                        'all')['metric']
        
        # Calculate risk metrics
        price_change = quote.get("dp", 0)
        volatility = metrics.get('yearlyVolatility', 0)
        beta = metrics.get('beta', 0)
        
        # Determine risk level based on multiple factors
        risk_factors = []
        if abs(price_change) > 5: risk_factors.append("High Price Volatility")
        if volatility > 30: risk_factors.append("High Market Volatility")
        if beta > 1.5: risk_factors.append("High Market Sensitivity")
        
        risk_level = "High Risk" if len(risk_factors) >= 2 else \
                    "Moderate Risk" if len(risk_factors) == 1 else "Low Risk"
        
        response = f"""
Risk Assessment for {stock_symbol}:

Key Risk Metrics:
- Price Change (24h): {price_change:.2f}%
- Volatility (Yearly): {volatility:.2f}%
- Beta: {beta:.2f}
- RSI: {metrics.get('rsi', 'N/A')}

Risk Analysis:
- Risk Level: {risk_level}
- Risk Factors: {', '.join(risk_factors) if risk_factors else 'No significant risk factors identified'}

Additional Risk Indicators:
- Debt/Equity Ratio: {metrics.get('totalDebtToEquityQuarterly', 'N/A')}
- Current Ratio: {metrics.get('currentRatioQuarterly', 'N/A')}
- Quick Ratio: {metrics.get('quickRatioQuarterly', 'N/A')}
"""
        return response
    except Exception as e:
        return f"Error in risk assessment for {stock_symbol}: {str(e)}"

# Create agents with their respective tools and prompts
portfolio_agent = create_react_agent(llm, tools=[portfolio_analysis], 
                                   state_modifier="Portfolio Analysis Agent")
market_research_agent = create_react_agent(llm, tools=[market_research], 
                                         state_modifier="Market Research Agent")
risk_assessment_agent = create_react_agent(llm, tools=[risk_assessment], 
                                         state_modifier="Risk Assessment Agent")

# Create agent nodes
portfolio_analysis_node = partial(agent_node, agent=portfolio_agent, 
                                name="Portfolio_Analysis_Agent")
market_research_node = partial(agent_node, agent=market_research_agent, 
                             name="Market_Research_Agent")
risk_assessment_node = partial(agent_node, agent=risk_assessment_agent, 
                             name="Risk_Assessment_Agent")

# Define Workflow State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

# Set up the Workflow
workflow_fin = StateGraph(AgentState)

# Add nodes
workflow_fin.add_node("Portfolio_Analysis_Agent", portfolio_analysis_node)
workflow_fin.add_node("Market_Research_Agent", market_research_node)
workflow_fin.add_node("Risk_Assessment_Agent", risk_assessment_node)
workflow_fin.add_node("supervisor", supervisor_agent_fin)

# Define routing for agents to return to supervisor
for member in ["Portfolio_Analysis_Agent", "Market_Research_Agent", 
              "Risk_Assessment_Agent"]:
    workflow_fin.add_edge(member, "supervisor")

# Define the supervisor's routing decisions
conditional_map_fin = {
    "Portfolio_Analysis_Agent": "Portfolio_Analysis_Agent",
    "Market_Research_Agent": "Market_Research_Agent",
    "Risk_Assessment_Agent": "Risk_Assessment_Agent",
    "FINISH": END
}

workflow_fin.add_conditional_edges("supervisor", lambda x: x["next"], 
                                 conditional_map_fin)
workflow_fin.add_edge(START, "supervisor")

# Compile the workflow
graph_fin = workflow_fin.compile()

def run_analysis(query):
    """Run a complete analysis with detailed output"""
    print(f"\nStarting analysis for query: {query}")
    print("=" * 80)
    
    inputs_fin = {"messages": [HumanMessage(content=query)]}
    
    for output in graph_fin.stream(inputs_fin, stream_mode="values"):
        if "messages" in output:
            for message in output["messages"]:
                if hasattr(message, 'name'):
                    print(f"\n{message.name} Response:")
                    print("-" * 40)
                    print(message.content)
                    print("-" * 40)
        if "next" in output:
            print(f"\nNext action: {output['next']}")
    
    print("\nAnalysis complete")
    print("=" * 80)

# Test the system with different queries
if __name__ == "__main__":
    test_queries = [
        "Analyze the portfolio for AAPL",
        "Research market trends for AAPL",
        "Assess the risk level for AAPL"
    ]
    
    for query in test_queries:
        run_analysis(query)