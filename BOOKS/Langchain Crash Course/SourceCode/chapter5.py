import os
from apikey import apikey
import streamlit as st 
from langchain_openai import OpenAI

os.environ["OPENAI_API_KEY"] = apikey

st.title('Medium Article Generator')
topic = st.text_input('Input your topic of interest')

llm = OpenAI(temperature=0.9)

if topic:
    response = llm.invoke(topic)
    st.write(response)
