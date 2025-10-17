import os
import requests
import base64
from PIL import Image
from io import BytesIO

# Define the Stable Diffusion API URL
STABLE_DIFFUSION_API_URL = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-medium"

# Retrieve the API key from the environment variable
API_KEY = os.getenv("NVIDIA_API_KEY")

# Set up the headers
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
}

def generate_visual_with_display(prompt: str):
    """
    Generates and displays digital artwork using NVIDIA's Stable Diffusion API.

    Args:
        prompt (str): The description of the image to be generated.

    Returns:
        None
    """
    payload = {
        "prompt": prompt,
        "cfg_scale": 7,
        "aspect_ratio": "16:9",
        "seed": 0,
        "steps": 50,
        "negative_prompt": "",
    }

    # Send the POST request to the API
    response = requests.post(STABLE_DIFFUSION_API_URL, headers=HEADERS, json=payload)

    # Raise an error if the request fails
    response.raise_for_status()

    # Parse the JSON response
    response_body = response.json()

    # Extract the Base64 image data
    image_data_base64 = response_body.get("image", None)
    if not image_data_base64:
        print("No image data found in the response.")
        return

    # Decode Base64 to binary data
    image_data = base64.b64decode(image_data_base64)

    # Open the image using PIL and display it
    image = Image.open(BytesIO(image_data))
    image.show()

    # Optionally, save the image to a file
    image.save("generated_image.png")
    print("Image saved as 'generated_image.png'")

# Example usage
if __name__ == "__main__":
    prompt = "a woman with a t-shirt written 'Stable Diffusion'"
    try:
        generate_visual_with_display(prompt)
    except Exception as e:
        print(f"Error: {e}")
