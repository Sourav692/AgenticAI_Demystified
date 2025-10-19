pip install --no-cache-dir openbb openbb-cboe openbb-finviz

import json
from datetime import datetime, timedelta
from typing import Annotated, Any, Generator, Optional, Sequence, Union
from uuid import uuid4
import os

from openbb import obb

from typing_extensions import TypedDict

import mlflow
from databricks_langchain import ChatDatabricks, UCFunctionToolkit, VectorSearchRetrieverTool
from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    convert_to_openai_messages,
    HumanMessage,
    SystemMessage,
    RemoveMessage,
    trim_messages,
)
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.tools import BaseTool, tool
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.prebuilt import tools_condition
from mlflow.entities import SpanType
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
)
from langchain_openai import ChatOpenAI
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

import tiktoken

from pyspark.dbutils import DBUtils

from databricks.sdk.runtime import *

dbutils = DBUtils(spark)

################################################################################
# Open AI API Key
################################################################################
OPENAI_KEY = dbutils.secrets.get(scope="AgenticAI", key="OPENAI_KEY")

################################################################################
# Enter OpenBB Key
# Get a free API key from (https://my.openbb.co/app/platform/pat)
################################################################################
OPENBB_PAT = dbutils.secrets.get(scope="AgenticAI", key="OPENBB_PAT")

################################################################################
# Enter Tavily Search API Key
# Get a free API key from (https://tavily.com/#api)
################################################################################
OPENBB_PAT = dbutils.secrets.get(scope="AgenticAI", key="OPENBB_PAT")

################################################################################
# Enter Tavily Search API Key
# Get a free API key from (https://tavily.com/#api)
################################################################################
TAVILY_API_KEY = dbutils.secrets.get(scope="AgenticAI", key="TAVILY_API_KEY")

################################################################################
# Setup Environment Variables
################################################################################
os.environ['OPENAI_API_KEY'] = OPENAI_KEY
os.environ['TAVILY_API_KEY'] = TAVILY_API_KEY

################################################################################
# Enter OBB Keys
################################################################################
obb.user.credentials.fmp_api_key = dbutils.secrets.get(scope="AgenticAI", key="fmp_api_key")
obb.user.credentials.polygon_api_key = dbutils.secrets.get(scope="AgenticAI", key="polygon_api_key")

################################################################################
# Create Financial Tools
# Financial Analysis Tools: The system integrates multiple tools to get useful financial data and metrics:

# SEARCH_WEB: Fetches general stock market information from the web.
# GET_STOCK_FUNDAMENTAL_INDICATOR_METRICS: Provides insights into key financial metrics such as P/E ratio, ROE, etc.
# GET_STOCK_NEWS: Extracts the latest news and updates related to stocks or markets.
# GET_GENERAL_MARKET_DATA: Fetches data on overall market trends and performance.
# GET_STOCK_TICKER: Validates and fetches stock ticker symbols based on user queries.
# GET_STOCK_PRICE_METRICS: Retrieves price trends, performance, and metrics for specific stocks.
################################################################################
tavily_search = TavilySearchAPIWrapper()

@tool
def search_web(query: str, num_results=8) -> list:
    """Search the web for a query. Userful for general information or general news"""
    results = tavily_search.raw_results(query=query,
                                        max_results=num_results,
                                        search_depth='advanced',
                                        include_answer=False,
                                        include_raw_content=True)
    return results

@tool
def get_stock_ticker_symbol(stock_name: str) -> str:
    """Get the symbol, name and CIK for any publicly traded company"""
    # Use OpenBB to search for stock ticker symbol and company details by name.
    # The provider "sec" fetches data from the U.S. Securities and Exchange Commission (SEC).
    res = obb.equity.search(stock_name, provider="sec")

    # Convert the result to a DataFrame and format it as markdown for readability.
    stock_ticker_details = res.to_df().to_markdown()

    # Prepare the output with the stock details.
    output = """Here are the details of the company and its stock ticker symbol:\n\n""" + stock_ticker_details
    return output

@tool
def get_stock_price_metrics(stock_ticker: str) -> str:
    """Get historical stock price data, stock price quote and price performance data
       like price changes for a specific stock ticker"""

    # Fetch the latest stock price quote using "cboe" provider.
    res = obb.equity.price.quote(stock_ticker, provider='cboe')
    price_quote = res.to_df().to_markdown()

    # Retrieve stock price performance metrics (e.g., percentage change) using "finviz" provider.
    res = obb.equity.price.performance(symbol=stock_ticker, provider='finviz')
    price_performance = res.to_df().to_markdown()

    # Fetch historical price data for the past year using "yfinance" provider.
    end_date = datetime.now()
    start_date = (end_date - timedelta(days=365)).strftime("%Y-%m-%d")
    res = obb.equity.price.historical(symbol=stock_ticker, start_date=start_date,
                                      interval='1d', provider='yfinance')
    price_historical = res.to_df().to_markdown()

    # Combine the results into a formatted output.
    output = ("""Here are the stock price metrics and data for the stock ticker symbol """ + stock_ticker + """: \n\n""" +
              "Price Quote Metrics:\n\n" + price_quote +
              "\n\nPrice Performance Metrics:\n\n" + price_performance +
              "\n\nPrice Historical Data:\n\n" + price_historical)
    return output

@tool
def get_stock_fundamental_indicator_metrics(stock_ticker: str) -> str:
    """Get fundamental indicator metrics for a specific stock ticker"""

    # Retrieve fundamental financial ratios (e.g., P/E ratio, ROE) using "fmp" provider.
    res = obb.equity.fundamental.ratios(symbol=stock_ticker, period='annual',
                                        limit=10, provider='fmp')
    fundamental_ratios = res.to_df().to_markdown()

    # Fetch additional fundamental metrics (e.g., EBITDA, revenue growth) using "yfinance" provider.
    res = obb.equity.fundamental.metrics(symbol=stock_ticker, period='annual',
                                        limit=10, provider='yfinance')
    fundamental_metrics = res.to_df().to_markdown()

    # Combine fundamental ratios and metrics into a single output.
    output = ("""Here are the fundamental indicator metrics and data for the stock ticker symbol """ + stock_ticker + """: \n\n""" +
              "Fundamental Ratios:\n\n" + fundamental_ratios +
              "\n\nFundamental Metrics:\n\n" + fundamental_metrics)
    return output

@tool
def get_stock_news(stock_ticker: str) -> str:
    """Get news article headlines for a specific stock ticker"""

    # Define the date range to fetch news (last 45 days).
    end_date = datetime.now()
    start_date = (end_date - timedelta(days=45)).strftime("%Y-%m-%d")

    # Retrieve news headlines for the stock using "tmx" provider.
    # res = obb.news.company(symbol=stock_ticker, start_date=start_date, provider='tmx', limit=50)
    # Change the provide to Polygon. As tmx now support only CANADA Companies
    res = obb.news.company(symbol=stock_ticker, start_date=start_date, provider='polygon', limit=50)
    news = res.to_df()

    # Extract relevant columns (symbols and titles) and format as markdown.
    news = news[['symbols', 'title']].to_markdown()

    # Prepare the output with the news headlines.
    output = ("""Here are the recent news headlines for the stock ticker symbol """ + stock_ticker + """: \n\n""" + news)
    return output

@tool
def get_general_market_data() -> str:
    """Get general data and indicators for the whole stock market including,
       most actively traded stocks based on volume, top price gainers and top price losers.
       Useful when you want an overview of the market and what stocks to look at."""

    # Retrieve the most actively traded stocks using "yfinance" provider.
    res = obb.equity.discovery.active(sort='desc', provider='yfinance', limit=15)
    most_active_stocks = res.to_df().to_markdown()

    # Fetch the top price gainers using "yfinance" provider.
    res = obb.equity.discovery.gainers(sort='desc', provider='yfinance', limit=15)
    price_gainers = res.to_df().to_markdown()

    # Retrieve the top price losers using "yfinance" provider.
    res = obb.equity.discovery.losers(sort='desc', provider='yfinance', limit=15)
    price_losers = res.to_df().to_markdown()

    # Combine the market data into a single formatted output.
    output = ("""Here's some detailed information of the stock market which includes most actively traded stocks, gainers and losers:\n\n""" +
              "Most actively traded stocks:\n\n" + most_active_stocks +
              "\n\nTop price gainers:\n\n" + price_gainers +
              "\n\nTop price losers:\n\n" + price_losers)
    return output

################################################################################
# Define Your System Prompt
################################################################################
AGENT_SYS_PROMPT = """Role: You are an AI stock market assistant tasked with providing investors
with up-to-date, detailed information on individual stocks or advice based on general market data.

Objective: Assist data-driven stock market investors by giving accurate,
complete, but concise information relevant to their questions about individual
stocks or general advice on useful stocks based on general market data and trends.

Capabilities: You are given a number of tools as functions. Use as many tools
as needed to ensure all information provided is timely, accurate, concise,
relevant, and responsive to the user's query.

Starting Flow:
Input validation: Determine if the input is asking about a specific company
or stock ticker (Flow 2). If not, check if they are asking for general advice on potentially useful stocks
based on current market data (Flow 1). Otherwise, respond in a friendly, positive, professional tone
that you don't have information to answer as you can only provide financial advice based on market data.
For each of the flows related to valid questions use the following instructions:

Flow 1:
A. Market Analysis: If the query is valid and the user wants to get general advice on the market
or stocks worth looking into for investing, leverage the general market data tool to get relevant data.
In case you need more information then you can also use web search.

Flow 2:
A. Symbol extraction. If the query is valid and is related to a specific company or companies,
extract the company name or ticker symbol from the question.
If a company name is given, look up the ticker symbol using a tool.
If the ticker symbol is not found based on the company, try to
correct the spelling and try again, like changing "microsfot" to "microsoft",
or broadening the search, like changing "southwest airlines" to a shorter variation
like "southwest" and increasing "limit" to 10 or more. If the company or ticker is
still unclear based on the question or conversation so far, and the results of the
symbol lookup, then ask the user to clarify which company or ticker.

B. Information retrieval. Determine what data the user is seeking on the symbol
identified. Use the appropriate tools to fetch the requested information. Only use
data obtained from the tools. You may use multiple tools in a sequence. For instance,
first determine the company's symbol, then retrieve price data using the symbol
and fundamental indicator data etc. For specific queries only retrieve data using the most relevant tool.
If detailed analysis is needed, you can call multiple tools to retrieve data first.
In case you still need more information then you can also use web search.

Response Generation Flow:
Compose Response: Analyze the retrieved data carefully and provide a comprehensive answer to the user in a clear and concise format,
in a friendly professional tone, emphasizing the data retrieved.
If the user asks for recommendations you can give some recommendations
but emphasize the user to do their own research before investing.
When generating the final response in markdown,
if there are special characters in the text, such as the dollar symbol,
ensure they are escaped properly for correct rendering e.g $25.5 should become \$25.5

Example Interaction:
User asks: "What is the PE ratio for Eli Lilly?"
Chatbot recognizes 'Eli Lilly' as a company name.
Chatbot uses symbol lookup to find the ticker for Eli Lilly, returning LLY.
Chatbot retrieves the PE ratio using the proper function with symbol LLY.
Chatbot responds: "The PE ratio for Eli Lilly (symbol: LLY) as of May 12, 2024 is 30."

Check carefully and only call the tools which are specifically named below.
Only use data obtained from these tools.
"""


# just checking size of the system prompt so we do not cross 128K context window limit when trimming messages later
enc = tiktoken.encoding_for_model("gpt-4o")
tokens = enc.encode(AGENT_SYS_PROMPT)
print(f"Number of tokens: {len(tokens)}")

################################################################################
# Key Steps For Agent Creation
# State Definition:

# The State class defines the structure of the conversation state, which holds the list of messages.
# Tools Setup:

# The tools list contains functions the agent can use to fetch data or perform actions (e.g., stock data, web search).
# LLM Initialization:

# The ChatOpenAI instance is initialized with GPT-4o and bound to the tools, enabling the agent to use them when needed.
# Chatbot Node:

# The chatbot function processes user input, trims the conversation history to avoid exceeding token limits, and generates a response using the LLM.
# Tool Node:

# The ToolNode handles the execution of tools when the agent decides to use them (e.g., fetching stock prices or searching the web).
# Graph Construction:

# The graph is built by adding nodes (chatbot and tools) and edges, with conditional logic to decide when to use tools or end the conversation.
# Agent Compilation:

# The graph is compiled into a runnable agent (financial_analyst_agent), which can process user inputs and interact with tools as needed.
################################################################################

################################################################################
# Define your LLM endpoint
################################################################################
# llm = ChatOpenAI(model="gpt-4o", temperature=0)
# LLM_ENDPOINT_NAME = "databricks-gpt-oss-120b"
LLM_ENDPOINT_NAME = "databricks-claude-3-7-sonnet"
llm = ChatDatabricks(endpoint=LLM_ENDPOINT_NAME)

################################################################################
# Define the state of the graph, which holds the conversation messages
################################################################################
class State(TypedDict):
    messages: Annotated[list, add_messages]

###############################################################################
## Define tools for your agent, enabling it to retrieve data or take actions
## beyond text generation
## To create and see usage examples of more tools, see
## https://docs.databricks.com/en/generative-ai/agent-framework/agent-tool.html
###############################################################################
tools = [
    get_stock_ticker_symbol,
    get_stock_price_metrics,
    get_stock_fundamental_indicator_metrics,
    get_stock_news,
    search_web,
    get_general_market_data
]

###############################################################################
# Create Tool-Calling Agent with Language Model and Tools
###############################################################################
def create_tool_calling_agent(
    llm: LanguageModelLike,
    tools: list,
    system_prompt: Optional[str] = None,
):
    """Create a tool-calling agent that uses the given model and tools.

    Args:
        llm (LanguageModelLike): The language model to use for the agent.
        tools (list): A list of tools the agent can use.
        system_prompt (Optional[str]): An optional system prompt to guide the agent's behavior.

    Returns:
        A tool-calling agent that can use the given model and tools.
    """
    # Create a chat model with the given model and tools
    llm_with_tools = llm.bind_tools(tools)
    # System message to guide the agent's behavior
    SYS_MSG = SystemMessage(content=AGENT_SYS_PROMPT)

    def chatbot(state: State):
        # Trim messages to avoid exceeding token limits
        messages = trim_messages(
            state["messages"],
            max_tokens=127000,
            strategy="last", # keep last 127K tokens in messages
            token_counter=ChatOpenAI(model="gpt-4o"),
            include_system=True, # keep system message always
            allow_partial=True, # trim messages to partial content if needed

        )
        # Invoke the LLM with the system message and trimmed conversation history
        return {"messages": [llm_with_tools.invoke([SYS_MSG] + messages)]}
    
    # Initialize the graph builder with the defined state
    graph_builder = StateGraph(State)

    # Add the chatbot node to the graph
    graph_builder.add_node("chatbot", chatbot)

    # Add a node for executing tools (e.g., fetching data, searching the web)
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    # Add conditional edges: the chatbot decides whether to use tools or end the conversation
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        ['tools', END]
    )

    # After using a tool, return to the chatbot to decide the next step
    graph_builder.add_edge("tools", "chatbot")

    # Set the chatbot as the entry point of the graph
    graph_builder.set_entry_point("chatbot")

    # Compile the graph into a runnable agent
    financial_analyst_agent = graph_builder.compile()

    return financial_analyst_agent

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
agent = create_tool_calling_agent(llm, tools, AGENT_SYS_PROMPT)
AGENT = LangGraphResponsesAgent(agent)
mlflow.models.set_model(AGENT)
