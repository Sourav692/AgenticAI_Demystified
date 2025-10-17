def test_addition_node():
    state = {"number1": 3, "number2": 5}
    result = addition_node(state)
    assert result["sum"] == 8

def addition_node(state):
    state["sum"] = state["number1"] + state["number2"]
    return state

def test_greeting_node():
    state = {"user_name": "Alice"}
    result = greeting_node(state)
    assert result["message"] == "Hello, Alice!"

def test_multiplication_node():
    state = {"number1": 4, "number2": 5}
    result = multiplication_node(state)
    assert result["product"] == 20

def greeting_node(state):
    state["message"] = f"Hello, {state['user_name']}!"
    return state

def multiplication_node(state):
    state["product"] = state["number1"] * state["number2"]
    return state

def test_addition_with_zero():
    state = {"number1": 0, "number2": 10}
    result = addition_node(state)
    assert result["sum"] == 10

def test_uppercase_node():
    state = {"text": "hello"}
    result = uppercase_node(state)
    assert result["text"] == "HELLO"

def uppercase_node(state):
    state["text"] = state["text"].upper()
    return state

def test_default_greeting():
    state = {}
    result = greeting_node(state)
    assert result["message"] == "Hello, Guest!"

from unittest.mock import patch
import pytest

@pytest.mark.parametrize("input1, input2, expected", [
    (1, 2, 3),
    (0, 5, 5),
    (-1, -1, -2),
])
def test_addition(input1, input2, expected):
    state = {"number1": input1, "number2": input2}
    result = addition_node(state)
    assert result["sum"] == expected

def test_greeting_workflow():
    graph = build_greeting_workflow()
    initial_state = {"user_name": "Alice"}
    final_state = graph.invoke(initial_state)
    assert final_state["message"] == "Hello, Alice!"

from langgraph.graph import StateGraph, START, END

def build_greeting_workflow():
    graph = StateGraph({"user_name": str, "message": str})
    graph.add_node("greeting", greeting_node)
    graph.add_edge(START, "greeting")
    graph.add_edge("greeting", END)
    return graph.compile()

def test_calculator_workflow():
    graph = build_calculator_workflow()
    initial_state = {"number1": 4, "number2": 5, "operation": "multiply"}
    final_state = graph.invoke(initial_state)
    assert final_state["result"] == 20

def build_calculator_workflow():
    graph = StateGraph({"number1": int, "number2": int, "operation": str, "result": int})
    graph.add_node("addition", addition_node)
    graph.add_node("multiplication", multiplication_node)
    graph.add_edge(START, "addition")
    graph.add_edge(START, "multiplication")
    graph.add_edge("addition", END)
    graph.add_edge("multiplication", END)
    return graph.compile()

def test_conditional_workflow():
    graph = build_conditional_workflow()
    initial_state = {"user_input": "check weather"}
    final_state = graph.invoke(initial_state)
    assert final_state["route"] == "weather_node"


def build_conditional_workflow():
    graph = StateGraph({"user_input": str, "route": str})
    graph.add_node("greeting_node", greeting_node)
    graph.add_node("weather_node", weather_node)
    graph.add_edge(START, "greeting_node")
    graph.add_edge("greeting_node", "weather_node")
    graph.add_edge("weather_node", END)
    return graph.compile()

def weather_node(state):
    state["route"] = "weather_node"
    return state

@patch("external_api.weather_api.get_weather")
def test_weather_api(mock_weather):
    mock_weather.return_value = {"temp": 72}
    graph = build_weather_workflow()
    initial_state = {"location": "New York"}
    final_state = graph.invoke(initial_state)
    assert final_state["temperature"] == 72

def build_weather_workflow():
    graph = StateGraph({"location": str, "temperature": int})
    graph.add_node("weather_node", weather_node)

def test_high_volume_inputs():
    graph = build_chatbot_workflow()
    for i in range(1000):
        initial_state = {"user_input": f"query {i}"}
        final_state = graph.invoke(initial_state)
        assert "response" in final_state

def build_chatbot_workflow():
    graph = StateGraph({"user_input": str, "response": str})
    graph.add_node("chatbot_node", chatbot_node)
    graph.add_edge(START, "chatbot_node")
    graph.add_edge("chatbot_node", END)
    return graph.compile()

def chatbot_node(state):
    state["response"] = f"Response for {state['user_input']}"
    return state



