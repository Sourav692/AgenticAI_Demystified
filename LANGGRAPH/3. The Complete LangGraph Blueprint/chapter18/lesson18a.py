import os
import requests
import json

# Retrieve the API key from the environment variable
API_KEY = os.getenv("NVIDIA_API_KEY")
url = "https://integrate.api.nvidia.com/v1/chat/completions"

# Define headers with Authorization, Accept, and Content-Type
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def call_nvidia_api_stream(prompt):
    """Call NVIDIA API with streaming and format the output."""
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": True,
        "model": "meta/llama-3.1-405b-instruct",
        "max_tokens": 1024,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "top_p": 0.7,
        "temperature": 0.2
    }
    
    # Make the POST request with streaming enabled
    response = requests.post(url, headers=headers, json=payload, stream=True)
    
    if response.status_code == 200:
        output = ""
        print("Generating response:")
        for chunk in response.iter_lines():
            if chunk:
                try:
                    # Parse the JSON chunk and extract content
                    data = json.loads(chunk[6:])  # Skip 'data: ' prefix
                    if 'choices' in data:
                        delta = data['choices'][0]['delta']
                        content = delta.get('content', "")  # Safely get content
                        if content: output += content
                        print(content, end='', flush=True)  # Print progressively
                except json.JSONDecodeError:
                    continue
        print("\n\nFinal Output:")
        print(output)
        return output
    else:
        raise Exception(f"API Error: {response.text}")

# Example usage
call_nvidia_api_stream("Write a promotional message for an eco-friendly gadget.")
