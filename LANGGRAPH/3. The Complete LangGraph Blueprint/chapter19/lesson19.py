from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing import TypedDict, Annotated, List, Sequence
import operator
from langchain_core.messages import BaseMessage, AIMessage
from langgraph.graph import StateGraph, START, END




def test_intent_classifier():
    """Test the intent classifier node"""
    state = {
        "messages": [HumanMessage(content="Where is my order #12345?")],
        "intent": "",
        "status": ""
    }
    result = intent_classifier_node(state)
    assert result["intent"] == IntentEnum.CHECK_ORDER

class CustomerState(TypedDict):
    """State for customer support workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    intent: str
    status: str


def intent_classifier_node(state: CustomerState):
    """Classify customer intent using LLM"""
    llm = ChatOpenAI(model="gpt-4o-mini")
    classifier_chain = intent_prompt | llm
    query = state["messages"][-1].content
    intent = classifier_chain.invoke({"query": query}).content.strip().lower()
    state["intent"] = intent
    return state

from enum import Enum

class IntentEnum(str, Enum):
    CHECK_ORDER = "check_order"
    PRODUCT_INQUIRY = "product_inquiry"
    ESCALATE = "escalate"
    UNKNOWN = "unknown"

intent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a customer support intent classifier. 
    Classify the user query into one of these intents: check_order, product_inquiry, 
    escalate, or unknown. Respond with just the intent."""),
    ("human", "{query}")
])

def test_order_status():
    """Test the order status node"""
    state = {
        "messages": [HumanMessage(content="Where is my order #12345?")],
        "intent": IntentEnum.CHECK_ORDER,
        "status": ""
    }
    result = order_status_node(state)
    response_text = result["messages"][-1].content.lower()
    assert "shipped" in response_text or "processing" in response_text

def order_status_node(state: CustomerState):
    """Handle order status queries using LLM"""
    llm = ChatOpenAI(model="gpt-4o-mini")
    order_chain = order_prompt | llm
    query = state["messages"][-1].content
    response = order_chain.invoke({"query": query})
    state["messages"].append(AIMessage(content=response.content))
    return state

order_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a customer service agent checking order status.
    Available orders: #12345 (shipped), #67890 (processing).
    If the order number is not found, apologize and provide support options.""")
])

def product_inquiry_node(state: CustomerState):
    """Handle product inquiries using LLM"""
    llm = ChatOpenAI(model="gpt-4o-mini")
    product_chain = product_prompt | llm
    query = state["messages"][-1].content
    response = product_chain.invoke({"query": query})
    state["messages"].append(AIMessage(content=response.content))
    return state

product_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a product information specialist.
    Products: wireless headphones (20-hour battery, noise cancellation),
    smartwatch (fitness tracking, heart rate monitoring).
    For unknown products, apologize and offer to connect with a specialist."""),])


def test_general_chat():
    """Test general conversation handling"""
    state = {
        "messages": [HumanMessage(content="Hello, I’m James")],
        "intent": IntentEnum.GENERAL_CHAT,
        "status": ""
    }
    result = general_chat_node(state)
    response_text = result["messages"][-1].content.lower()
    assert "nice to meet you" in response_text and "james" in response_text

def general_chat_node(state: CustomerState):
    """Handle general conversation and queries"""
    llm = ChatOpenAI(model="gpt-4o-mini")
    chat_chain = general_chat_prompt | llm
    query = state["messages"][-1].content
    response = chat_chain.invoke({"query": query})
    state["messages"].append(AIMessage(content=response.content))
    return state

general_chat_prompt = ChatPromptTemplate.from_messages([
    ("system","You are a helpful assistant.")
])

def test_complete_workflow():
    """Test the complete customer support workflow"""
    workflow = build_support_workflow()

    # Test order status
    state = {"messages": [HumanMessage(content="Where is my order #12345?")]}
    result = workflow.invoke(state)
    assert "shipped" in result["messages"][-1].content.lower()

    # Test product inquiry
    state = {"messages": [HumanMessage(content="Tell me about wireless headphones")]}
    result = workflow.invoke(state)
    assert "wireless headphones" in result["messages"][-1].content.lower()

    # Test general chat
    state = {"messages": [HumanMessage(content="My name is James")]}
    result = workflow.invoke(state)
    assert "nice to meet you" in result["messages"][-1].content.lower()

def build_support_workflow():
    """Build the complete customer support workflow"""
    workflow = StateGraph(CustomerState)
    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("order_status", order_status_node)
    workflow.add_node("product_inquiry", product_inquiry_node)
    workflow.add_node("general_chat", general_chat_node)
    workflow.add_edge(START, "intent_classifier")
    workflow.add_edge("intent_classifier", "order_status")
    workflow.add_edge("intent_classifier", "product_inquiry")
    workflow.add_edge("intent_classifier", "general_chat")
    workflow.add_edge("order_status", END)
    workflow.add_edge("product_inquiry", END)
    workflow.add_edge("general_chat", END)
    return workflow.compile()
    






