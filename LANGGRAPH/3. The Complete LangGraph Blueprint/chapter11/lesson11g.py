import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import tiktoken

# Step 1: Load the document
file_path = os.path.join(os.getcwd(), "chapter11", "Faiss by FacebookAI.pdf")
raw_documents = PyPDFLoader(file_path=file_path).load()

# Step 2: Split the document into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)

# Step 3: Initialize the embeddings model
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

# Step 4: Index the document chunks in Chroma vector store
db = Chroma.from_documents(documents=documents, embedding=embeddings)
print("Documents indexed in Chroma successfully.")

# Step 5: Define a retriever for similarity search
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})  # Retrieve top 3 relevant chunks

# Step 6: Define the prompt template for the LLM
prompt = ChatPromptTemplate.from_template(
"""
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""
)

# Step 7: Initialize the ChatOpenAI model (e.g., gpt-4 or another preferred model)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Step 8: Set up the Retrieval-Augmented Generation (RAG) chain
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# Step 9: Ask a question and generate a response
question = "Can you explain what FAISS is used for?"
for chunk in rag_chain.stream(question):
    print(chunk, end="", flush=True)
