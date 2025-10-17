from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class StockState(TypedDict):
    stock_price: float
    action: str

def monitor_stock(state: StockState):
    if state['stock_price'] > 150:
        state['action'] = 'Sell'
    elif state['stock_price'] < 100:
        state['action'] = 'Buy'
    else:
        state['action'] = 'Hold'
    return state

# Define the workflow
builder = StateGraph(StockState)
builder.add_node("monitor_stock", monitor_stock)
builder.add_edge(START, "monitor_stock")
builder.add_edge("monitor_stock", END)
graph = builder.compile()

# Sample invocation with a stock price trigger
result = graph.invoke({"stock_price": 180, "action": ""})
print(result)  # Output: {'stock_price': 120, 'action': 'Hold'}
