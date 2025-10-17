from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

# Initialize embeddings model
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    dimensions=1024
)

# Sample document to index
text = "LangChain is the framework for building context-aware reasoning applications."

# Index the document in the InMemoryVectorStore
vectorstore = InMemoryVectorStore.from_texts(
    [text],
    embedding=embeddings,
)

print("Document indexed successfully.")

# Convert the vector store into a retriever
retriever = vectorstore.as_retriever()

# Define a sample query
query = "What is langchain?"

# Retrieve the most similar document(s)
retrieved_documents = retriever.invoke(query)

# Display the content of the retrieved document
print("Retrieved document content:")
print(retrieved_documents[0].page_content)
