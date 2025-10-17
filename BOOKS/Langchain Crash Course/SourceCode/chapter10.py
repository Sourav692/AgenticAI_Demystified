import os
from apikey import apikey
import streamlit as st # used to create our UI frontend
from langchain_openai import ChatOpenAI # used for GPT3.5/4 model
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA


os.environ["OPENAI_API_KEY"] = apikey
st.title('Chat with Document') # title in our web page
loader = TextLoader('./constitution.txt') # to load text document
documents = loader.load()
# print(documents)


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200) # Initialize RecursiveCharacterTextSplitter
chunks = text_splitter.split_documents(documents) # Create the Chunks using text_splitter object

st.write(chunks[0]) 
st.write(chunks[1])

embeddings = OpenAIEmbeddings()
vector_store = Chroma.from_documents(chunks, embeddings)

# initialize OpenAI instance
llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
retriever=vector_store.as_retriever()
chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
# get question from user input
question = st.text_input('Input your question')

if question:
    # run chain
    response = chain.invoke(question)
    st.write(response['result'])

