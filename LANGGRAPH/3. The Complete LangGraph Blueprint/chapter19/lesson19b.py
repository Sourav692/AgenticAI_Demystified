import os
from typing import TypedDict, Annotated, List, Sequence
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, BaseMessage
import operator
from pydantic import BaseModel, Field

# 1. First, let's write tests for our state structure
class CustomerState(TypedDict):
    """State for customer support workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    intent: str
    status: str

def test_state_structure():
    """Test that our state structure works as expected"""
    state = {
        "messages": [HumanMessage(content="Where is my order #12345?")],
        "intent": "",
        "status": ""
    }
    assert isinstance(state["messages"][0], BaseMessage)
    assert isinstance(state["intent"], str)
    assert isinstance(state["status"], str)

# 2. Intent Classification Node with LLM
intent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a customer support intent classifier. 
    Classify the user query into one of these intents: check_order, product_inquiry, 
    escalate, or unknown. Respond with just the intent."""),
    ("human", "{query}")
])

def test_intent_classifier_node():
    """Test the intent classifier node"""
    llm = ChatOpenAI(model="gpt-4-mini")
    state = {
        "messages": [HumanMessage(content="Where is my order #12345?")],
        "intent": "",
        "status": ""
    }
    result = intent_classifier_node(state)
    assert result["intent"] in ["check_order", "product_inquiry", "escalate", "unknown"]

def intent_classifier_node(state: CustomerState):
    """Classify customer intent using LLM"""
    llm = ChatOpenAI(model="gpt-4o-mini")
    classifier_chain = intent_prompt | llm
    query = state["messages"][-1].content
    intent = classifier_chain.invoke({"query": query}).content.strip().lower()
    state["intent"] = intent
    return state

# 3. Order Status Node
order_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a customer service agent checking order status.
    Available orders: #12345 (shipped), #67890 (processing).
    If the order number is not found, apologize and provide support options."""),
    ("human", "{query}")
])

def test_order_status_node():
    """Test the order status node"""
    llm = ChatOpenAI(model="gpt-4o-mini")
    state = {
        "messages": [HumanMessage(content="Where is my order #12345?")],
        "intent": "check_order",
        "status": ""
    }
    result = order_status_node(state)
    assert len(result["messages"]) > 1  # Original message plus response
    assert "shipped" in result["messages"][-1].content.lower()

def order_status_node(state: CustomerState):
    """Handle order status queries using LLM"""
    llm = ChatOpenAI(model="gpt-4o-mini")
    order_chain = order_prompt | llm
    query = state["messages"][-1].content
    response = order_chain.invoke({"query": query})
    state["messages"].append(response)
    return state

# 4. Product Inquiry Node
product_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a product information specialist.
    Products: wireless headphones (20-hour battery, noise cancellation),
    smartwatch (fitness tracking, heart rate monitoring).
    For unknown products, apologize and offer to connect with a specialist."""),
    ("human", "{query}")
])

def test_product_inquiry_node():
    """Test the product inquiry node"""
    state = {
        "messages": [HumanMessage(content="Tell me about wireless headphones")],
        "intent": "product_inquiry",
        "status": ""
    }
    result = product_inquiry_node(state)
    assert len(result["messages"]) > 1
    assert "battery" in result["messages"][-1].content.lower()

def product_inquiry_node(state: CustomerState):
    """Handle product inquiries using LLM"""
    llm = ChatOpenAI(model="gpt-4o-mini")
    product_chain = product_prompt | llm
    query = state["messages"][-1].content
    response = product_chain.invoke({"query": query})
    state["messages"].append(response)
    return state

# 5. Complete Workflow
def test_complete_workflow():
    """Test the complete customer support workflow"""
    workflow = build_support_workflow()
    
    # Test order status query
    result = workflow.invoke({
        "messages": [HumanMessage(content="Where is my order #12345?")],
        "intent": "",
        "status": ""
    })
    assert "shipped" in result["messages"][-1].content.lower()
    
    # Test product inquiry
    result = workflow.invoke({
        "messages": [HumanMessage(content="Tell me about wireless headphones")],
        "intent": "",
        "status": ""
    })
    assert "battery" in result["messages"][-1].content.lower()

def build_support_workflow():
    """Build the complete customer support workflow"""
    # Initialize graph with our state
    workflow = StateGraph(CustomerState)
    
    # Add nodes
    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("order_status", order_status_node)
    workflow.add_node("product_inquiry", product_inquiry_node)
    
    # Define routing logic
    def route_by_intent(state):
        return state["intent"]
    
    # Add edges
    workflow.add_edge(START, "intent_classifier")
    workflow.add_conditional_edges(
        "intent_classifier",
        route_by_intent,
        {
            "check_order": "order_status",
            "product_inquiry": "product_inquiry"
        }
    )
    workflow.add_edge("order_status", END)
    workflow.add_edge("product_inquiry", END)
    
    return workflow.compile()

# 6. Interactive Testing
def main():
    """Run interactive customer support agent"""
    workflow = build_support_workflow()
    
    print("Customer Support AI (type 'quit' to exit)")
    while True:
        try:
            query = input("\nCustomer: ")
            if query.lower() == 'quit':
                break
            
            # Initialize state with proper structure
            initial_state = {
                "messages": [HumanMessage(content=query)],
                "intent": "",
                "status": ""
            }
            
            try:
                result = workflow.invoke(initial_state)
                # Safely access the last message's content
                if result and "messages" in result and len(result["messages"]) > 0:
                    print(f"Agent: {result['messages'][-1].content}")
                else:
                    print("Agent: I apologize, but I'm having trouble processing that request. Please try again.")
            except Exception as e:
                print(f"Agent: I apologize, but I encountered an error. Please try rephrasing your question.")
                print(f"Debug: {str(e)}")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    main()