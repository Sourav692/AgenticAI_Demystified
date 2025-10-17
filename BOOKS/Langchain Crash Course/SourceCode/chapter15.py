import os
from apikey import apikey
import streamlit as st # used to create our UI frontend
from langchain_openai import ChatOpenAI # used for GPT3.5/4 model
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import YoutubeLoader

os.environ["OPENAI_API_KEY"] = apikey

def clear_history():
    if 'history' in st.session_state:
        del st.session_state['history']


st.title('Chat with Youtube') # title in our web page
youtube_url = st.text_input('Input your Youtube URL')

if youtube_url:
    with st.spinner('Reading, chunking and embedding file...'):
        loader = YoutubeLoader.from_youtube_url(youtube_url)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                       chunk_overlap=200)

        chunks = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        vector_store = Chroma.from_documents(chunks, embeddings)

        # initialize OpenAI instance
        llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
        retriever = vector_store.as_retriever()

        crc = ConversationalRetrievalChain.from_llm(llm, retriever)

        st.session_state.crc = crc

        # success message when file is chunked & embedded successfully
        st.success('File uploaded, chunked and embedded successfully')

# get question from user input
question = st.text_input('Input your question')

if question:
    if 'crc' in st.session_state:
        crc = st.session_state.crc

        if 'history' not in st.session_state:
            st.session_state['history'] = []

        response = crc.invoke({
            'question': question,
            'chat_history': st.session_state['history']
        })

        st.session_state['history'].append((question, response['answer']))
        st.write(response['answer'])
        for prompts in st.session_state['history']:
            st.write("Question: " + prompts[0])
            st.write("Answer: " + prompts[1])
