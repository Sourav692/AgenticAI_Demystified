import os
from apikey import apikey
from langchain import hub
from langchain_openai import OpenAI
from langchain.agents import load_tools, create_react_agent, AgentExecutor

os.environ["OPENAI_API_KEY"] = apikey

# we set temperature to 0 because we want an objective research tool without hallucinations
llm = OpenAI(temperature=0.0)

tools = load_tools(['wikipedia', 'llm-math'], llm)

# get the default ReAct prompt to use
prompt = hub.pull("hwchase17/react")

# get answer from commandline input
answer = input('Input Wikipedia Research Task\n')

# construct the ReAct agent
agent = create_react_agent(llm, tools, prompt)

# create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
# run the executor
response = agent_executor.invoke({'input': answer})
print(response)
