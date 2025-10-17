import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import tiktoken

# Initialize the embeddings model
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

### Step 1: Load and Process Local Document (PDF)

# Load local PDF document
file_path = os.path.join(os.getcwd(), "chapter11", "Faiss by FacebookAI.pdf")
pdf_loader = PyPDFLoader(file_path)
pdf_documents = pdf_loader.load()

# Split PDF into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
split_pdf_documents = text_splitter.split_documents(pdf_documents)

### Step 2: Load and Process Web Content

# Define URLs to fetch web content
urls = [
    "https://github.com/facebookresearch/faiss",
    "https://github.com/facebookresearch/faiss/wiki"
]

# Load web content
web_loader = WebBaseLoader(web_paths=urls)
web_documents = web_loader.load()

# Split web documents into chunks
split_web_documents = text_splitter.split_documents(web_documents)

### Step 3: Combine Local and Web Documents

# Combine documents from both local and web sources
all_documents = split_pdf_documents + split_web_documents

### Step 4: Index Documents in Chroma Vector Store

# Index all documents in Chroma
db = Chroma.from_documents(documents=all_documents, embedding=embeddings)
print("All documents indexed in Chroma successfully.")

### Step 5: Define a Retriever

# Define a retriever to fetch relevant documents from the combined sources
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5})  # Retrieve top 5 relevant chunks

### Step 6: Define the Prompt Template for the LLM

prompt = ChatPromptTemplate.from_template(
"""
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""
)

### Step 7: Initialize the ChatOpenAI Model

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

### Step 8: Set up the Retrieval-Augmented Generation (RAG) Chain

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

### Step 9: Ask a Question and Generate a Response

question = "Who are the main authors of Faiss?"
for chunk in rag_chain.stream(question):
    print(chunk, end="", flush=True)
