from typing import Annotated, Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from datetime import datetime

class FinancialState(TypedDict):
    user_input: str
    budget: dict
    investments: dict
    current_date: datetime
    next_action: str

def BudgetToolNode(state: FinancialState):
    # In real-world, you'd connect to a budgeting API
        return {"budget": {"income": 5000, "expenses": {"food": 500, "rent": 1000}}}

def InvestmentToolNode(state: FinancialState):
        # Connect to an investment platform API
        return {"investments": {"stocks": 10000, "bonds": 5000}}

def FinancialAdvisorNode(state: FinancialState):
    # This could involve a more complex LLM or financial model
    if state["budget"]["income"] - sum(state["budget"]["expenses"].values()) > 500:
        return {"advice": "Consider increasing your investment in stocks", "next_action": "invest"}
    return {"advice": "Keep current budget allocations", "next_action": "budget_review"}

# Initialize the graph
finance_graph = StateGraph(FinancialState)

# Add nodes
finance_graph.add_node("budget_query", BudgetToolNode)
finance_graph.add_node("investment_query", InvestmentToolNode)
finance_graph.add_node("financial_advice", FinancialAdvisorNode)

# Define edges
finance_graph.add_edge(START, "budget_query")
finance_graph.add_edge("budget_query", "investment_query")
#finance_graph.add_conditional_edges("financial_advice", "investment_query", lambda state: state["next_action"] == "invest")
#finance_graph.add_conditional_edges("financial_advice", "budget_query", lambda state: state["next_action"] == "budget_review")
finance_graph.add_edge("investment_query", "financial_advice")
finance_graph.add_edge("financial_advice", END)
#finance_graph.add_edge("budget_query", END)

# Example execution
initial_state = FinancialState(
    user_input="How's my budget and should I invest more?",
    budget={},
    investments={},
    current_date=datetime.now(),
    next_action="start"
)
graph = finance_graph.compile()
result = graph.invoke(initial_state)
print("Final Financial State:", result)