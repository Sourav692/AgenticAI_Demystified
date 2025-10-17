import os
import requests
import base64
from PIL import Image
from io import BytesIO
import tempfile
from pathlib import Path
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage
import gradio as gr
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants and initialization
API_KEY = os.getenv("NVIDIA_API_KEY")
if not API_KEY:
    raise ValueError("NVIDIA API key not found in environment variables")

STABLE_DIFFUSION_API_URL = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-medium"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
}

# Initialize LLM
llm = ChatNVIDIA(
    model="meta/llama-3.1-405b-instruct",
    api_key=API_KEY,
    temperature=0.7
)

def generate_stable_diffusion_image(prompt: str) -> Image.Image:
    """Generate an image using NVIDIA's Stable Diffusion API."""
    try:
        payload = {
            "prompt": prompt,
            "cfg_scale": 7,
            "aspect_ratio": "16:9",
            "seed": 0,
            "steps": 50,
            "negative_prompt": "",
        }

        response = requests.post(
            STABLE_DIFFUSION_API_URL, 
            headers=HEADERS, 
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        image_data = response.json().get("image")
        if not image_data:
            raise ValueError("No image data in response")
            
        image_bytes = base64.b64decode(image_data)
        return Image.open(BytesIO(image_bytes))
        
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise

def generate_content(campaign_brief: str) -> tuple[str, str]:
    """Generate marketing content and image prompt."""
    try:
        # Generate content
        content_prompt = f"""
        Create professional marketing content for the following campaign brief:
        {campaign_brief}
        
        Provide:
        1. Headline: Attention-grabbing, max 10 words
        2. Main copy: 2-3 compelling sentences
        3. Call to action: Clear and actionable
        4. Three relevant hashtags
        """
        
        content_response = llm.invoke([{"role": "user", "content": content_prompt}])
        content = content_response.content
        
        # Generate image prompt
        image_prompt_template = f"""
        Create a detailed image generation prompt based on this marketing content:
        {content}
        
        Focus on:
        - Visual style and mood
        - Key elements and composition
        - Color scheme
        - Artistic direction
        
        Format: Create a clear, detailed prompt suitable for Stable Diffusion.
        """
        
        prompt_response = llm.invoke([{"role": "user", "content": image_prompt_template}])
        image_prompt = prompt_response.content
        
        return content, image_prompt
        
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        raise

def process_campaign(brief: str) -> tuple[str, str, Image.Image]:
    """Process the entire campaign generation workflow."""
    try:
        # Generate content and image prompt
        content, image_prompt = generate_content(brief)
        
        # Generate image
        image = generate_stable_diffusion_image(image_prompt)
        
        return content, image_prompt, image
        
    except Exception as e:
        logger.error(f"Campaign processing failed: {e}")
        raise

# Create Gradio interface
with gr.Blocks(title="AI Campaign Generator") as demo:
    gr.Markdown("""
    # AI Campaign Generator
    Generate professional marketing campaigns with AI-powered content and visuals.
    Provide a detailed campaign brief including goals, target audience, and key messages.
    """)
    
    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(
                label="Campaign Brief",
                placeholder="Describe your campaign goals, target audience, and key messages...",
                lines=5
            )
            submit_btn = gr.Button("Generate Campaign")
            
        with gr.Column():
            content_output = gr.Textbox(
                label="Generated Content",
                lines=8,
                interactive=False
            )
            prompt_output = gr.Textbox(
                label="Image Generation Prompt",
                lines=4,
                interactive=False
            )
            image_output = gr.Image(
                label="Generated Campaign Visual",
                type="pil"
            )
    
    def campaign_generator(brief):
        try:
            content, prompt, image = process_campaign(brief)
            return content, prompt, image
        except Exception as e:
            return f"Error: {str(e)}", "", None
    
    submit_btn.click(
        fn=campaign_generator,
        inputs=input_text,
        outputs=[content_output, prompt_output, image_output],
        api_name="generate"
    )

if __name__ == "__main__":
    # Clean up temporary files
    temp_dir = tempfile.gettempdir()
    for file in Path(temp_dir).glob("*.png"):
        try:
            file.unlink()
        except Exception:
            pass
            
    demo.launch()