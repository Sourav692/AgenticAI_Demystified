import os
from apikey import apikey
import streamlit as st 
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate

os.environ["OPENAI_API_KEY"] = apikey

st.title('Medium Article Generator')
topic = st.text_input('Input your topic of interest')

title_template = PromptTemplate(
  input_variables=['topic', 'language'],
  template='Give me medium article title on {topic} in {language}'
)

llm = OpenAI(temperature=0.9)

if topic:
    response = llm(title_template.format(topic=topic,language='english'))
    st.write(response)
