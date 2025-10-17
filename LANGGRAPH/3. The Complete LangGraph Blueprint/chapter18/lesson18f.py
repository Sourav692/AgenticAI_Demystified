import requests


# Fetch data from a public API
url = "https://api.github.com"
response = requests.get(url)


# Print the response
print("Response Status Code:", response.status_code)
print("Response Data:", response.json())

import requests
url = "https://httpbin.org/post"
payload = {"name": "John", "age": 30}


# Sending a POST request
response = requests.post(url, json=payload)


# Print the response
print("Response Status Code:", response.status_code)
print("Response Data:", response.json())

import requests


url = "https://example.com/api"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json",
}


try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for HTTP codes >= 400
    print("Response Data:", response.json())
except requests.RequestException as e:
    print("An error occurred:", e)

import gradio as gr


def reverse_text(text):
    """Reverses the input text."""
    return text[::-1]


# Create a simple Gradio interface
interface = gr.Interface(
    fn=reverse_text,  # Function to run
    inputs="text",    # Input type
    outputs="text"    # Output type
)


interface.launch()  # Start the interface

import gradio as gr


def greet(name, age):
    """Generates a greeting message."""
    return f"Hello, {name}! You are {age} years old."


# Create a Gradio interface with two inputs
interface = gr.Interface(
    fn=greet,
    inputs=["text", "number"],  # Name as text and age as number
    outputs="text"             # Output as text
)


interface.launch()

import gradio as gr
from PIL import Image


def process_image(image):
    """Converts the image to grayscale."""
    return image.convert("L")  # Convert to grayscale


# Create an interface with image input and output
interface = gr.Interface(
    fn=process_image,
    inputs="image",
    outputs="image"
)


interface.launch()

from PIL import Image


# Open an image
image = Image.open("example.jpg")
image.show()  # Display the image


# Save the image in PNG format
image.save("example.png")

from PIL import Image, ImageFilter


# Open an image
image = Image.open("example.jpg")


# Apply transformations
resized_image = image.resize((200, 200))  # Resize
rotated_image = image.rotate(45)         # Rotate
blurred_image = image.filter(ImageFilter.BLUR)  # Apply blur


# Save the transformed images
resized_image.save("resized.png")
rotated_image.save("rotated.png")
blurred_image.save("blurred.png")

from PIL import Image
from io import BytesIO
import base64


# Simulate an API response with Base64 image data
image_data_base64 = "..."  # Replace with actual Base64 string
image_data = base64.b64decode(image_data_base64)


# Load the image from memory
image = Image.open(BytesIO(image_data))
image.show()

def number_generator():
    for i in range(1, 6):
        yield i


# Using the generator
for number in number_generator():
    print(number)

def multi_step_process():
    yield "Step 1: Initializing..."
    yield "Step 2: Processing data..."
    yield "Step 3: Finalizing..."
    yield "Process complete!"


for step in multi_step_process():
    print(step)








