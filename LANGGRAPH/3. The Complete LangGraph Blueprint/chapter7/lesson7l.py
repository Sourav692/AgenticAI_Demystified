import requests
import urllib.parse
from langgraph.graph import StateGraph, MessagesState, START, END
from dotenv import load_dotenv
import os

# Load API keys from environment variables
load_dotenv()
weather_api_key = os.getenv("OPENWEATHER_API_KEY")

# Define the node for fetching live weather data
def live_weather_node(state):
    last_message = state["messages"][-1].content.lower()
    
    # Extract city name from user query
    if "in" in last_message:
        city = last_message.split("in")[-1].strip().replace("?", "")
    else:
        city = "London"  # Default city
    
    # URL-encode the city name for the API request
    city_encoded = urllib.parse.quote(city)
    
    # Fetch the weather data from OpenWeatherMap API
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_encoded}&appid={weather_api_key}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        return {"messages": [f"The weather in {city} is {temperature}°C with {description}."]}
    else:
        return {"messages": ["Sorry, I couldn't fetch the weather information."]}

# Define the node for calculator operations using Math.js API
def calculator_node(state):
    last_message = state["messages"][-1].content.lower()
    
    # Extract the arithmetic expression from the user query
    expression = last_message.split("calculate")[-1].strip()
    
    # URL-encode the expression for the API request
    encoded_expression = urllib.parse.quote(expression)
    
    # Fetch the result from Math.js API
    url = f"http://api.mathjs.org/v4/?expr={encoded_expression}"
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.text
        return {"messages": [f"The result of {expression} is {result}."]}
    else:
        return {"messages": ["Sorry, I couldn't calculate that."]}

# Define a default node for unrecognized inputs
def default_node(state):
    return {"messages": ["Sorry, I don't understand that request."]}

# Define the routing function to route the user query to the appropriate node
def routing_function(state):
    last_message = state["messages"][-1].content.lower()
    
    if "weather" in last_message:
        return "live_weather_node"
    elif "calculate" in last_message:
        return "calculator_node"
    return "default_node"

# Build the LangGraph workflow
builder = StateGraph(MessagesState)
builder.add_node("live_weather_node", live_weather_node)
builder.add_node("calculator_node", calculator_node)
builder.add_node("default_node", default_node)

# Add conditional edges to route the queries
builder.add_conditional_edges(START, routing_function)
builder.add_edge("live_weather_node", END)
builder.add_edge("calculator_node", END)
builder.add_edge("default_node", END)

# Compile the graph
app = builder.compile()

# Simulate interaction with the user
def simulate_interaction():
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        
        input_message = {"messages": [("human", user_input)]}
        
        # Stream the result
        for result in app.stream(input_message, stream_mode="values"):
            result["messages"][-1].pretty_print()

simulate_interaction()
