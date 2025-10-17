import os
from apikey import apikey
import streamlit as st # used to create our UI frontend
import langchain
from langchain_openai import ChatOpenAI # used for GPT3.5/4 model
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain


os.environ["OPENAI_API_KEY"] = apikey
st.title('Chat with Document') # title in our web page
loader = TextLoader('./constitution.txt') # to load text document
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)
embeddings = OpenAIEmbeddings()
vector_store = Chroma.from_documents(chunks, embeddings)

# initialize OpenAI instance
llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
retriever=vector_store.as_retriever()
crc = ConversationalRetrievalChain.from_llm(llm, retriever)
# get question from user input
question = st.text_input('Input your question')

if question:
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    # run chain
    response = crc.invoke({
        'question': question,
        'chat_history': st.session_state['history']
    })

    st.session_state['history'].append((question, response['answer']))
    for prompts in st.session_state['history']:
        st.write("Question: " + prompts[0])
        st.write("Answer: " + prompts[1])

