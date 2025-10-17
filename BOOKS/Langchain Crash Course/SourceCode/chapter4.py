import os
from apikey import apikey
import streamlit as st

os.environ["OPENAI_API_KEY"] = apikey

st.title('Medium Article Generator')
topic = st.text_input('Input your topic of interest')

