from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document  # Import the Document class

# Initialize embeddings model
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    dimensions=1024
)

# Define sample documents as Document objects
documents = [
    Document(page_content="LangChain is a framework for building context-aware reasoning applications."),
    Document(page_content="FAISS is a library for efficient similarity search and clustering of dense vectors."),
    Document(page_content="The quick brown fox jumps over the lazy dog.")
]

# Index documents in Chroma vector store
db = Chroma.from_documents(documents, embedding=embeddings)
print("Documents indexed in Chroma successfully.")

# Define a query to search
query = "What is LangChain?"

# Perform similarity search in Chroma
docs = db.similarity_search(query)

# Display the content of the retrieved document
print("Most similar document to the query:")
print(docs[0].page_content)

# Generate embedding for the query
query_embedding = embeddings.embed_query(query)

# Perform similarity search by embedding vector
docs_by_vector = db.similarity_search_by_vector(query_embedding)

# Display the content of the retrieved document
print("Most similar document to the query (vector search):")
print(docs_by_vector[0].page_content)

