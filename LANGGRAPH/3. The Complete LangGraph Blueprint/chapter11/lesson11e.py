import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
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

# Step 5: Calculate the number of tokens for each chunk
def num_tokens_from_string(string: str, encoding_string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_string)
    num_tokens = len(encoding.encode(string))
    return num_tokens

# Calculate tokens for each document chunk and display the result
for idx, doc in enumerate(documents):
    num_tokens = num_tokens_from_string(doc.page_content, encoding_string="cl100k_base")  # "cl100k_base" for OpenAI's token encoding
    print(f"Document chunk {idx+1} has {num_tokens} tokens.")
