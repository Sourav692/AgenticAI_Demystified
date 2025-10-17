import requests
from langgraph.graph import StateGraph, MessagesState, START, END
import urllib


# Define the node to fetch live calculator results
def calculator_node(state):
    last_message = state["messages"][-1].content.lower()
    
    # Extract the arithmetic expression from the user query
    expression = last_message.split("calculate")[-1].strip()
    
    # URL-encode the expression to ensure it's safe for use in the query string
    encoded_expression = urllib.parse.quote(expression)
    
    # Make the API call to the math.js API with the URL-encoded expression
    url = f"http://api.mathjs.org/v4/?expr={encoded_expression}"
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.text
        return {"messages": [f"The result of {expression} is {result}."]}
    else:
        return {"messages": ["Sorry, I couldn't calculate that."]}

# Define the graph workflow
builder = StateGraph(MessagesState)

# Add the calculator node
builder.add_node("calculator_node", calculator_node)

# Set up the edges
builder.add_edge(START, "calculator_node")
builder.add_edge("calculator_node", END)

# Compile the graph
app = builder.compile()

# Simulate interaction with the calculator API
def simulate_interaction():
    input_message = {"messages": [("human", "Calculate 5 + 3 * 2")]}
    
    # Process the input and stream the result
    for result in app.stream(input_message, stream_mode="values"):
        result["messages"][-1].pretty_print()

simulate_interaction()


