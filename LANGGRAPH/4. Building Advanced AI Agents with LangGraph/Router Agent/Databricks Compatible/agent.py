##########################################################
# Initial Imports
##########################################################
import os
from databricks.vector_search.client import VectorSearchClient
from langchain.schema import Document
from typing import List,Dict,TypedDict, Literal
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from databricks_langchain import ChatDatabricks, UCFunctionToolkit, VectorSearchRetrieverTool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
)
from typing import Annotated, Any, Generator, Optional, Sequence, Union
import mlflow

###########################################################
# Initial Variables Declaration
###########################################################
endpoint_name="router_agent_endpoint"
source_table_name="agentic_ai.langgraph.router_agent_chunks"
index_name="agentic_ai.langgraph.router_agent_index"

###########################################################
# Instantiate the VectorSearchClient to interact with Databricks Vector Search endpoints.
###########################################################
client = VectorSearchClient()
index = client.get_index(endpoint_name=endpoint_name, index_name=index_name)

################################################################################
# Define your LLM endpoint
################################################################################
# llm = ChatOpenAI(model="gpt-4o", temperature=0)
# LLM_ENDPOINT_NAME = "databricks-gpt-oss-120b"
LLM_ENDPOINT_NAME = "databricks-claude-3-7-sonnet"
llm = ChatDatabricks(endpoint=LLM_ENDPOINT_NAME)

######################################################################################################################
# Define the Customer Inquiry State
# We create a CustomerSupportState typed dictionary to keep track of each interaction:

# customer_query: The text of the customer's question
# query_category: Technical, Billing, or General (used for routing)
# query_sentiment: Positive, Neutral, or Negative (used for routing)
# final_response: The system's response to the customer
######################################################################################################################
class CustomerSupportState(TypedDict):
    """
    customer_query: the original query from the customer.
    query_category: the topic of the query (e.g., Technical, Billing).
    query_sentiment: the emotional tone (e.g., Positive, Negative).
    final_response: the system-generated response.
    """
    customer_query: str
    query_category: str
    query_sentiment: str
    final_response: str

class QueryCategory(BaseModel):
    categorized_topic: Literal['Technical', 'Billing', 'General']

class QuerySentiment(BaseModel):
    sentiment: Literal['Positive', 'Neutral', 'Negative']

######################################################################################################################
# Create Node Functions
# Each function below represents a stage in processing a customer inquiry:

# categorize_inquiry: Classifies the query into Technical, Billing, or General.
# analyze_inquiry_sentiment: Determines if the sentiment is Positive, Neutral, or Negative.
# generate_technical_response: Produces a response for technical issues.
# generate_billing_response: Produces a response for billing questions.
# generate_general_response: Produces a response for general queries.
# escalate_to_human_agent: Escalates the query to a human if sentiment is negative.
# determine_route: Routes the inquiry to the appropriate response node based on category and sentiment.
######################################################################################################################
def categorize_inquiry(support_state: CustomerSupportState) -> CustomerSupportState:
    """
    Classify the customer query into Technical, Billing, or General.
    """

    query = support_state["customer_query"]
    ROUTE_CATEGORY_PROMPT = """Act as a customer support agent trying to best categorize the customer query.
                               You are an agent for an AI products and hardware company.

                               Please read the customer query below and
                               determine the best category from the following list:

                               'Technical', 'Billing', or 'General'.

                               Remember:
                                - Technical queries will focus more on technical aspects like AI models, hardware, software related queries etc.
                                - General queries will focus more on general aspects like contacting support, finding things, policies etc.
                                - Billing queries will focus more on payment and purchase related aspects

                                Return just the category name (from one of the above)

                                Query:
                                {customer_query}
                            """
    prompt = ROUTE_CATEGORY_PROMPT.format(customer_query=query)
    route_category = llm.with_structured_output(QueryCategory).invoke(prompt)

    return {
        "query_category": route_category.categorized_topic
    }

def analyze_inquiry_sentiment(support_state: CustomerSupportState) -> CustomerSupportState:
    """
    Analyze the sentiment of the customer query as Positive, Neutral, or Negative.
    """

    query = support_state["customer_query"]
    SENTIMENT_CATEGORY_PROMPT = """Act as a customer support agent trying to best categorize the customer query's sentiment.
                                   You are an agent for an AI products and hardware company.

                                   Please read the customer query below,
                                   analyze its sentiment which should be one from the following list:

                                   'Positive', 'Neutral', or 'Negative'.

                                   Return just the sentiment (from one of the above)

                                   Query:
                                   {customer_query}
                                """
    prompt = SENTIMENT_CATEGORY_PROMPT.format(customer_query=query)
    sentiment_category = llm.with_structured_output(QuerySentiment).invoke(prompt)

    return {
        "query_sentiment": sentiment_category.sentiment
    }

def generate_technical_response(support_state: CustomerSupportState) -> CustomerSupportState:
    """
    Provide a technical support response by combining knowledge from the vector store and LLM.
    """
    # Retrieve category and ensure it is lowercase for metadata filtering

    categorized_topic = support_state["query_category"]
    query = support_state["customer_query"]

    # Use metadata filter for 'technical' queries
    if categorized_topic.lower() == "technical":
        # Perform retrieval from VectorDB
        results = index.similarity_search(
                query_text="what is your refund policy?",
                columns=["content","category"],  # Ensure only columns present in the index are listed
                num_results=3,
                filters={"category": ["technical"]},
                query_type="hybrid"
            )
        relevant_docs = convert_vector_search_to_documents(results)
        retrieved_content = "\n\n".join(doc.page_content for doc in relevant_docs)

        # Combine retrieved information into the prompt
        prompt = ChatPromptTemplate.from_template(
            """
            Craft a clear and detailed technical support response for the following customer query.
            Use the provided knowledge base information to enrich your response.
            In case there is no knowledge base information or you do not know the answer just say:

            Apologies I was not able to answer your question, please reach out to +1-xxx-xxxx

            Customer Query:
            {customer_query}

            Relevant Knowledge Base Information:
            {retrieved_content}
            """
        )

        # Generate the final response using the LLM
        chain = prompt | llm
        tech_reply = chain.invoke({
            "customer_query": query,
            "retrieved_content": retrieved_content
        }).content
    else:
        # For non-technical queries, provide a default response or a general handling
        tech_reply = "Apologies I was not able to answer your question, please reach out to +1-xxx-xxxx"

    # Update and return the modified support state
    return {
        "final_response": tech_reply
    }

def generate_billing_response(support_state: CustomerSupportState) -> CustomerSupportState:
    """
    Provide a billing support response by combining knowledge from the vector store and LLM.
    """
    # Retrieve category and ensure it is lowercase for metadata filtering
    categorized_topic = support_state["query_category"]
    query = support_state["customer_query"]

    # Use metadata filter for 'billing' queries
    if categorized_topic.lower() == "billing":
        # Perform retrieval from VectorDB
        results = index.similarity_search(
                query_text="what is your refund policy?",
                columns=["content","category"],  # Ensure only columns present in the index are listed
                num_results=3,
                filters={"category": ["billing"]},
                query_type="hybrid"
            )
        relevant_docs = convert_vector_search_to_documents(results)
        retrieved_content = "\n\n".join(doc.page_content for doc in relevant_docs)

        # Combine retrieved information into the prompt
        prompt = ChatPromptTemplate.from_template(
            """
            Craft a clear and detailed billing support response for the following customer query.
            Use the provided knowledge base information to enrich your response.
            In case there is no knowledge base information or you do not know the answer just say:

            Apologies I was not able to answer your question, please reach out to +1-xxx-xxxx

            Customer Query:
            {customer_query}

            Relevant Knowledge Base Information:
            {retrieved_content}
            """
        )

        # Generate the final response using the LLM
        chain = prompt | llm
        billing_reply = chain.invoke({
            "customer_query": query,
            "retrieved_content": retrieved_content
        }).content
    else:
        # For non-billing queries, provide a default response or a general handling
        billing_reply = "Apologies I was not able to answer your question, please reach out to +1-xxx-xxxx"

    # Update and return the modified support state
    return {
        "final_response": billing_reply
    }
    
def generate_billing_response(support_state: CustomerSupportState) -> CustomerSupportState:
    """
    Provide a billing support response by combining knowledge from the vector store and LLM.
    """
    # Retrieve category and ensure it is lowercase for metadata filtering
    categorized_topic = support_state["query_category"]
    query = support_state["customer_query"]

    # Use metadata filter for 'billing' queries
    if categorized_topic.lower() == "billing":
        # Perform retrieval from VectorDB
        results = index.similarity_search(
                query_text="what is your refund policy?",
                columns=["content","category"],  # Ensure only columns present in the index are listed
                num_results=3,
                filters={"category": ["billing"]},
                query_type="hybrid"
            )
        relevant_docs = convert_vector_search_to_documents(results)
        retrieved_content = "\n\n".join(doc.page_content for doc in relevant_docs)

        # Combine retrieved information into the prompt
        prompt = ChatPromptTemplate.from_template(
            """
            Craft a clear and detailed billing support response for the following customer query.
            Use the provided knowledge base information to enrich your response.
            In case there is no knowledge base information or you do not know the answer just say:

            Apologies I was not able to answer your question, please reach out to +1-xxx-xxxx

            Customer Query:
            {customer_query}

            Relevant Knowledge Base Information:
            {retrieved_content}
            """
        )

        # Generate the final response using the LLM
        chain = prompt | llm
        billing_reply = chain.invoke({
            "customer_query": query,
            "retrieved_content": retrieved_content
        }).content
    else:
        # For non-billing queries, provide a default response or a general handling
        billing_reply = "Apologies I was not able to answer your question, please reach out to +1-xxx-xxxx"

    # Update and return the modified support state
    return {
        "final_response": billing_reply
    }

def generate_general_response(support_state: CustomerSupportState) -> CustomerSupportState:
    """
    Provide a general support response by combining knowledge from the vector store and LLM.
    """
    # Retrieve category and ensure it is lowercase for metadata filtering
    categorized_topic = support_state["query_category"]
    query = support_state["customer_query"]

    # Use metadata filter for 'general' queries
    if categorized_topic.lower() == "general":
        # Perform retrieval from VectorDB
        results = index.similarity_search(
                query_text="what is your refund policy?",
                columns=["content","category"],  # Ensure only columns present in the index are listed
                num_results=3,
                filters={"category": ["general"]},
                query_type="hybrid"
            )
        relevant_docs = convert_vector_search_to_documents(results)
        retrieved_content = "\n\n".join(doc.page_content for doc in relevant_docs)
        print(retrieved_content)

        # Combine retrieved information into the prompt
        prompt = ChatPromptTemplate.from_template(
            """
            Craft a clear and detailed general support response for the following customer query.
            Use the provided knowledge base information to enrich your response.
            In case there is no knowledge base information or you do not know the answer just say:

            Apologies I was not able to answer your question, please reach out to +1-xxx-xxxx

            Customer Query:
            {customer_query}

            Relevant Knowledge Base Information:
            {retrieved_content}
            """
        )

        # Generate the final response using the LLM
        chain = prompt | llm
        general_reply = chain.invoke({
            "customer_query": query,
            "retrieved_content": retrieved_content
        }).content
    else:
        # For non-general queries, provide a default response or a general handling
        general_reply = "Apologies I was not able to answer your question, please reach out to +1-xxx-xxxx"

    # Update and return the modified support state
    return {
        "final_response": general_reply
    }

def escalate_to_human_agent(support_state: CustomerSupportState) -> CustomerSupportState:
    """
    Escalate the query to a human agent if sentiment is negative.
    """

    return {
        "final_response": "Apologies, we are really sorry! Someone from our team will be reaching out to your shortly!"
    }

def determine_route(support_state: CustomerSupportState) -> str:
    """
    Route the inquiry based on sentiment and category.
    """
    if support_state["query_sentiment"] == "Negative":
        return "escalate_to_human_agent"
    elif support_state["query_category"] == "Technical":
        return "generate_technical_response"
    elif support_state["query_category"] == "Billing":
        return "generate_billing_response"
    else:
        return "generate_general_response"
    
###########################################################
# Convert the vector search result to LangChain Document
###########################################################
def convert_vector_search_to_documents(results) -> List[Document]:
  column_names = []
  for column in results["manifest"]["columns"]:
      column_names.append(column)

  langchain_docs = []
  for item in results["result"]["data_array"]:
      metadata = {}
      score = item[-1]
      # print(score)
      i = 1
      for field in item[1:-1]:
          # print(field + "--")
          metadata[column_names[i]["name"]] = field
          i = i + 1
      doc = Document(page_content=item[0], metadata=metadata)  # , 9)
      langchain_docs.append(doc)
  return langchain_docs

###############################################################################
# Create Tool-Calling Agent with Language Model and Tools
###############################################################################
def create_router_agent():
    """
    Create a chatbot agent with the given language model and tools.
    """
    # Create the graph with our typed state
    customer_support_graph = StateGraph(CustomerSupportState)

    # Add nodes for each function
    customer_support_graph.add_node("categorize_inquiry", categorize_inquiry)
    customer_support_graph.add_node("analyze_inquiry_sentiment", analyze_inquiry_sentiment)
    customer_support_graph.add_node("generate_technical_response", generate_technical_response)
    customer_support_graph.add_node("generate_billing_response", generate_billing_response)
    customer_support_graph.add_node("generate_general_response", generate_general_response)
    customer_support_graph.add_node("escalate_to_human_agent", escalate_to_human_agent)

    # Add edges to represent the processing flow
    customer_support_graph.add_edge("categorize_inquiry", "analyze_inquiry_sentiment")
    customer_support_graph.add_conditional_edges(
        "analyze_inquiry_sentiment",
        determine_route,
        [
            "generate_technical_response",
            "generate_billing_response",
            "generate_general_response",
            "escalate_to_human_agent"
        ]
    )

    # All terminal nodes lead to the END
    customer_support_graph.add_edge("generate_technical_response", END)
    customer_support_graph.add_edge("generate_billing_response", END)
    customer_support_graph.add_edge("generate_general_response", END)
    customer_support_graph.add_edge("escalate_to_human_agent", END)

    # Set the entry point for the workflow
    customer_support_graph.set_entry_point("categorize_inquiry")

    # Compile the graph into a runnable agent
    memory = MemorySaver()
    compiled_support_agent = customer_support_graph.compile(checkpointer=memory)
    return compiled_support_agent

###############################################################################
# Convert Responses to ChatCompletion Messages
###############################################################################
class LangGraphResponsesAgent(ResponsesAgent):
    def __init__(self, agent):
        self.agent = agent

    def _responses_to_cc(self, message: dict[str, Any]) -> list[dict[str, Any]]:
        """Convert from a Responses API output item to ChatCompletion messages."""
        msg_type = message.get("type")
        if msg_type == "function_call":
            return [
                {
                    "role": "assistant",
                    "content": "tool call",
                    "tool_calls": [
                        {
                            "id": message["call_id"],
                            "type": "function",
                            "function": {
                                "arguments": message["arguments"],
                                "name": message["name"],
                            },
                        }
                    ],
                }
            ]
        elif msg_type == "message" and isinstance(message["content"], list):
            return [
                {"role": message["role"], "content": content["text"]}
                for content in message["content"]
            ]
        elif msg_type == "reasoning":
            return [{"role": "assistant", "content": json.dumps(message["summary"])}]
        elif msg_type == "function_call_output":
            return [
                {
                    "role": "tool",
                    "content": message["output"],
                    "tool_call_id": message["call_id"],
                }
            ]
        compatible_keys = ["role", "content", "name", "tool_calls", "tool_call_id"]
        filtered = {k: v for k, v in message.items() if k in compatible_keys}
        return [filtered] if filtered else []

    def _prep_msgs_for_cc_llm(self, responses_input) -> list[dict[str, Any]]:
        "Convert from Responses input items to ChatCompletion dictionaries"
        cc_msgs = []
        for msg in responses_input:
            cc_msgs.extend(self._responses_to_cc(msg.model_dump()))

    def _langchain_to_responses(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        "Convert from ChatCompletion dict to Responses output item dictionaries"
        for message in messages:
            message = message.model_dump()
            role = message["type"]
            if role == "ai":
                if tool_calls := message.get("tool_calls"):
                    return [
                        self.create_function_call_item(
                            id=message.get("id") or str(uuid4()),
                            call_id=tool_call["id"],
                            name=tool_call["name"],
                            arguments=json.dumps(tool_call["args"]),
                        )
                        for tool_call in tool_calls
                    ]
                else:
                    return [
                        self.create_text_output_item(
                            text=message["content"],
                            id=message.get("id") or str(uuid4()),
                        )
                    ]
            elif role == "tool":
                return [
                    self.create_function_call_output_item(
                        call_id=message["tool_call_id"],
                        output=message["content"],
                    )
                ]
            elif role == "user":
                return [message]

    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        outputs = [
            event.item
            for event in self.predict_stream(request)
            if event.type == "response.output_item.done"
        ]
        return ResponsesAgentResponse(output=outputs, custom_outputs=request.custom_inputs)

    def predict_stream(
        self,
        request: ResponsesAgentRequest,
    ) -> Generator[ResponsesAgentStreamEvent, None, None]:
        cc_msgs = []
        for msg in request.input:
            cc_msgs.extend(self._responses_to_cc(msg.model_dump()))

        for event in self.agent.stream({"messages": cc_msgs}, stream_mode=["updates", "messages"]):
            if event[0] == "updates":
                for node_data in event[1].values():
                    for item in self._langchain_to_responses(node_data["messages"]):
                        yield ResponsesAgentStreamEvent(type="response.output_item.done", item=item)
            # filter the streamed messages to just the generated text messages
            elif event[0] == "messages":
                try:
                    chunk = event[1][0]
                    if isinstance(chunk, AIMessageChunk) and (content := chunk.content):
                        yield ResponsesAgentStreamEvent(
                            **self.create_text_delta(delta=content, item_id=chunk.id),
                        )
                except Exception as e:
                    print(e)

# Create the agent object, and specify it as the agent object to use when
# loading the agent back for inference via mlflow.models.set_model()
mlflow.langchain.autolog()
agent = create_router_agent()
AGENT = LangGraphResponsesAgent(agent)
mlflow.models.set_model(AGENT)
