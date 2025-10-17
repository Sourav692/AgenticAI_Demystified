from langgraph.graph import StateGraph, MessagesState, START, END

# Define a node to simulate a weather response
def weather_node(state: MessagesState):
    return {"messages": ["It's sunny with a temperature of 25°C."]}

# Define a node to handle basic arithmetic calculations
def calculator_node(state: MessagesState):
    user_query = state["messages"][-1].content.lower()
    
    if "add" in user_query:
        numbers = [int(s) for s in user_query.split() if s.isdigit()]
        result = sum(numbers)
        return {"messages": [f"The result of addition is {result}."]}
    
    return {"messages": ["I can only perform addition for now."]}

# Define a default node to handle unrecognized inputs
def default_node(state: MessagesState):
    return {"messages": ["Sorry, I don't understand that request."]}

# Custom routing function to decide which node to route to
def routing_function(state: MessagesState):
    last_message = state["messages"][-1].content.lower()
    
    if "weather" in last_message:
        return "weather_node"  # Route to weather node
    elif "add" in last_message or "calculate" in last_message:
        return "calculator_node"  # Route to calculator node
    return "default_node"  # Route to default node for unrecognized inputs

# Build the workflow graph
builder = StateGraph(MessagesState)
builder.add_node("weather_node", weather_node)
builder.add_node("calculator_node", calculator_node)
builder.add_node("default_node", default_node)
builder.add_node("routing_function", routing_function)

# Set up the edges for routing
builder.add_conditional_edges(START, routing_function)
builder.add_edge("weather_node", END)
builder.add_edge("calculator_node", END)
builder.add_edge("default_node", END)  # Edge to end after default node

# Compile the graph
app = builder.compile()

# Simulate interaction with the agent
def simulate_interaction():
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        
        input_message = {"messages": [("human", user_input)]}
        for result in app.stream(input_message, stream_mode="values"):
            result["messages"][-1].pretty_print()

# Start interacting with the agent
simulate_interaction()
