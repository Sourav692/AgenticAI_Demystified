# %%
!pip install -qq langchain==0.3.14
!pip install -qq langchain-openai==0.3.0
!pip install -qq langchain-community==0.3.14

# %%
!pip install -qq markitdown

# %%
import os
from dotenv import load_dotenv
load_dotenv()

# %%
WEATHER_API_KEY = os.environ['OPENAI_API_KEY']

# %%
from langchain_core.tools import tool
from markitdown import MarkItDown
from langchain_community.tools.tavily_search import TavilySearchResults
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import requests
import json
from warnings import filterwarnings
filterwarnings('ignore')

tavily_tool = TavilySearchResults(max_results=5,
                                  search_depth='basic',
                                  include_answer=False,
                                  include_raw_content=True)
# certain websites won't let you crawl them unless you specify a user-agent
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
})
md = MarkItDown(requests_session=session)

@tool
def search_web_extract_info(query: str) -> list:
    """Search the web for a query and extracts useful information from the search links."""
    print('Calling web search tool')
    results = tavily_tool.invoke(query)
    docs = []

    def extract_content(url):
        """Helper function to extract content from a URL."""
        extracted_info = md.convert(url)
        text_title = extracted_info.title.strip()
        text_content = extracted_info.text_content.strip()
        return text_title + '\n' + text_content
    # parallelize execution of different urls
    with ThreadPoolExecutor() as executor:
        for result in tqdm(results):
            try:
                future = executor.submit(extract_content, result['url'])
                # Wait for up to 15 seconds for the task to complete
                content = future.result(timeout=15)
                docs.append(content)
            except TimeoutError:
                print(f"Extraction timed out for url: {result['url']}")
            except Exception as e:
                print(f"Error extracting from url: {result['url']} - {e}")

    return docs


@tool
def get_weather(query: str) -> list:
    """Search weatherapi to get the current weather of the queried location."""
    print('Calling weather tool')
    base_url = "http://api.weatherapi.com/v1/current.json"
    complete_url = f"{base_url}?key={WEATHER_API_KEY}&q={query}"

    response = requests.get(complete_url)
    data = response.json()
    if data.get("location"):
        return data
    else:
        return "Weather Data Not Found"

# %%
# Extract the final answer from the agent response
def extract_final_answer(agent_response):
    """
    Extract the Final Answer portion from the agent response

    Args:
        agent_response (dict): The response from agent_executor.invoke()
        method (str): Method to use - "split", "regex", or "parse"

    Returns:
        str: The final answer content only
    """
    output = agent_response['output']

    import re
    match = re.search(r'Final Answer:\s*(.*)', output, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return "No Final Answer found"

# %%
get_weather.invoke("Get weather in kolkata now")

# %%
from langchain_openai import ChatOpenAI

chatgpt = ChatOpenAI(model="gpt-4o", temperature=0)
tools = [search_web_extract_info, get_weather]

chatgpt_with_tools = chatgpt.bind_tools(tools)

# %%
prompt = "Show me Local Attractions in Bangalore and The Weather in Bangalore"
response = chatgpt_with_tools.invoke(prompt)
response.tool_calls

# %%
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SYS_PROMPT = """Act as a helpful assistant.
                You run in a loop of Thought, Action, PAUSE, Observation.
                At the end of the loop, you output an Answer.
                Use Thought to describe your thoughts about the question you have been asked.
                Use Action to run one of the actions available to you - then return PAUSE.
                Observation will be the result of running those actions.
                Repeat till you get to the answer for the given user query.

                If user ask about some local attraction spot of a destination or location then provide the list of local attractions as bullet points and also provide the current weather of the location.

                Use the following workflow format:
                  Question: the input task you must solve
                  Thought: you should always think about what to do
                  Action: the action to take which can be any of the following:
                            - break it into smaller steps if needed
                            - see if you can answer the given task with your trained knowledge
                            - call the most relevant tools at your disposal mentioned below in case you need more information
                  Action Input: the input to the action
                  Observation: the result of the action
                  ... (this Thought/Action/Action Input/Observation can repeat N times)
                  Thought: I now know the final answer
                  Final Answer: the final answer to the original input question


                Tools at your disposal to perform tasks as needed:
                  - get_weather: whenever user asks get the weather of a place.
                  - search_web_extract_info: whenever user asks for specific information or if you don't know the answer.
             """

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", SYS_PROMPT),
        MessagesPlaceholder(variable_name="history", optional=True),
        ("human", "{query}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# %%
from langchain.agents import create_tool_calling_agent

chatgpt = ChatOpenAI(model="gpt-4o-mini", temperature=0)
tools = [search_web_extract_info, get_weather]
agent = create_tool_calling_agent(chatgpt, tools, prompt_template)

# %%
from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(agent=agent,
                               tools=tools,
                               early_stopping_method='force',
                               max_iterations=10)

# %%
query = """Kolkata"""
resp = agent_executor.invoke({"query": query})

# %%
from IPython.display import display, Markdown
final_answer = extract_final_answer(resp)

# %%
display(Markdown(resp["output"]))

# %%
display(Markdown(final_answer))

# %%



