from langchain_nvidia_ai_endpoints import ChatNVIDIA
import os

API_KEY = os.getenv("NVIDIA_API_KEY")

client = ChatNVIDIA(
  model="meta/llama-3.1-405b-instruct",
  api_key=API_KEY,
  temperature=0.2,
  top_p=0.7,
  max_tokens=1024,
)
prompt = "Write a promotional message for an eco-friendly gadget."
for chunk in client.stream([{"role":"user","content":prompt}]): 
  print(chunk.content, end="")

  
