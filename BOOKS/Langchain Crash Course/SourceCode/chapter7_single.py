import os
from apikey import apikey
import streamlit as st 
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

os.environ["OPENAI_API_KEY"] = apikey

st.title('Medium Article Generator')
topic = st.text_input('Input your topic of interest')

title_template = PromptTemplate(
  input_variables=['topic'],
  template='Give me medium article title on {topic}'
)

llm = OpenAI(temperature=0.9)

title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True)

if topic:
    response = title_chain.invoke(topic)
    st.write(response['text'])
