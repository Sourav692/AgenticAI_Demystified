from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatAnthropic, ChatOpenAI
from fastapi import FastAPI
from langserve import add_routes
import os
import uvicorn

api_key = ''
os.environ['OPENAI_API_KEY'] = api_key
os.environ['ANTHROPIC_API_KEY'] ='hsdhhhdhdaj'

test = FastAPI(
  title="Demo app for testing",
  version="1.5",
  description="demo forlangserve",
)

add_routes(
    test,
    ChatAnthropic(),
    path="/anthropic_test",
)

add_routes(
    test,
    ChatOpenAI(),
    path="/openai_test",
)

model = ChatOpenAI()
prompt = ChatPromptTemplate.from_template("Explain to me {topic}")
add_routes(
    test,
    prompt | model,
    path="/demo",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(test, host="localhost", port=8000)