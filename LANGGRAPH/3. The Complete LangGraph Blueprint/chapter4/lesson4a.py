from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Check if API key exists
if api_key is None:
    print("Error: OPENAI_API_KEY not found in environment variables")
else:
    print("API key loaded successfully")