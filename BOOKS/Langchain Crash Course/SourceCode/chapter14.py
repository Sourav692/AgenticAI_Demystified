import os
from apikey import apikey
import streamlit as st # used to create our UI frontend
from langchain_openai import ChatOpenAI # used for GPT3.5/4 model
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain


os.environ["OPENAI_API_KEY"] = apikey

def clear_history():
    if 'history' in st.session_state:
        del st.session_state['history']


st.title('Chat with Document') # title in our web page

uploaded_file = st.file_uploader('Upload file:',type=['pdf','docx', 'txt'])
add_file = st.button('Add File', on_click=clear_history)

if uploaded_file and add_file:
    with st.spinner('Reading, chunking and embedding file...'):
        bytes_data = uploaded_file.read()
        file_name = os.path. join('./', uploaded_file.name)
        with open (file_name, 'wb') as f:
            f.write(bytes_data)

        name, extension = os.path.splitext(file_name)

        if extension == '.pdf':
            from langchain_community.document_loaders import PyPDFLoader

            loader = PyPDFLoader(file_name)
        elif extension == '.docx':
            from langchain_community.document_loaders import Docx2txtLoader

            loader = Docx2txtLoader(file_name)
        elif extension == '.txt':
            from langchain_community.document_loaders import TextLoader

            loader = TextLoader(file_name)
        else:
            st.write('Document format is not supported!')

        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
        chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        vector_store = Chroma.from_documents(chunks, embeddings)

        # initialize OpenAI instance
        llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
        retriever=vector_store.as_retriever()

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
