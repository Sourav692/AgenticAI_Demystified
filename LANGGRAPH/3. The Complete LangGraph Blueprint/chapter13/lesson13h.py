import os
import time
import logging
from typing import Annotated, List, TypedDict
import pandas as pd
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
import psycopg2
from table_config import TABLE_CONFIG
from langgraph.graph import StateGraph, SEND, END
from langchain_core.messages import HumanMessage, BaseMessage
import operator


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename="audit_data_monitor.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Validate environment variables
def get_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        logging.error(f"Environment variable '{var_name}' is not set.")
        raise EnvironmentError(f"Environment variable '{var_name}' is required.")
    return value

# Database connection configuration
DB_CONFIG = {
    "dbname": get_env_var("DB_NAME"),
    "user": get_env_var("DB_USER"),
    "password": get_env_var("DB_PASSWORD"),
    "host": get_env_var("DB_HOST"),
    "port": get_env_var("DB_PORT"),
}

# Embeddings function
def get_embedding(text):
    return OpenAIEmbeddings().embed_query(text)

# Query Retrieval Task for a Single Table
def retrieve_table_data(table_name: str, query_embedding):
    table_results = []
    with psycopg2.connect(**DB_CONFIG) as conn:
        vector_query = f"""
        WITH target AS (
            SELECT %s::vector AS query_embedding
        )
        SELECT
            *,
            1 - (embedding <=> query_embedding) AS similarity
        FROM
            {table_name}, target
        ORDER BY
            similarity DESC
        LIMIT 5;
        """
        with conn.cursor() as cursor:
            cursor.execute(vector_query, (query_embedding,))
            results = cursor.fetchall()
            table_results = [{"similarity": r[-1], **dict(zip([desc[0] for desc in cursor.description], r))} for r in results]
    return table_results

# Generate AI Summary with Reduced Prompt Size
def generate_ai_summary(query_text: str, table_results: dict) -> str:
    prompt = f"A financial audit query was received: '{query_text}'. Relevant data from various tables:\n\n"
    for table, records in table_results.items():
        prompt += f"Table: {table}\n"
        for record in records[:3]:  # Limit to the top 3 records
            essential_fields = {k: v for k, v in record.items() if k not in ["embedding", "query_embedding", "similarity"]}
            prompt += f" - {essential_fields}\n"

    prompt += "\nProvide a concise summary of the audit findings, focusing on insights, potential issues, and recommendations."
    
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-002",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=3,
    )
    response = model.invoke(prompt)
    return response.content

# Query Retrieval Agent with Parallel Processing
def query_retrieval_agent(state):
    query_text = state["query_text"]
    query_embedding = get_embedding(query_text)
    messages = [HumanMessage(content="Query Retrieval Agent is initiating parallel retrieval across tables.")]

    # Parallel SEND tasks for each table
    parallel_tasks = [
        SEND(retrieve_table_data, config["table"], query_embedding)
        for config in TABLE_CONFIG.values()
    ]

    # Execute all tasks concurrently
    table_results = {}
    results = StateGraph().parallel(parallel_tasks)

    # Collect results into table_results dictionary
    for config, result in zip(TABLE_CONFIG.values(), results):
        table_results[config["table"]] = result

    messages.append(HumanMessage(content="Query Retrieval Agent has completed parallel retrieval. Generating summary."))
    
    # Generate AI summary
    ai_summary = generate_ai_summary(query_text, table_results)
    messages.append(HumanMessage(content=ai_summary))
    
    return {"messages": messages}

# Define the Data Loading Agent for completeness
class DataLoader(TypedDict):
    query_text: str
    messages: Annotated[List[BaseMessage], operator.add]

data_loader_graph = StateGraph(DataLoader)

# Define the Data Loader Agent (simplified)
def data_loader_agent(state):
    # Placeholder logic for data loading
    messages = [HumanMessage(content="Data Loading Agent completed data preparation.")]
    return {"messages": messages}

# Define StateGraph and Node Connections
data_loader_graph.add_node("DataLoaderAgent", data_loader_agent)
data_loader_graph.add_node("QueryRetrievalAgent", query_retrieval_agent)

data_loader_graph.set_entry_point("DataLoaderAgent")
data_loader_graph.add_edge("DataLoaderAgent", "QueryRetrievalAgent")
data_loader_graph.add_edge("QueryRetrievalAgent", END)

# Compile the graph
graph = data_loader_graph.compile()

# Initialize state and execute the graph
initial_state = {"query_text": "Identify all significant expenses for Q4"}
for s in graph.stream(initial_state):
    if "__end__" not in s:
        print(s)
        print("----")
