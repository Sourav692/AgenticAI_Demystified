import os
import uuid
import requests
import base64
from PIL import Image
from io import BytesIO
import tempfile
from pathlib import Path
from typing import Generator, Optional, Tuple
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import gradio as gr
import logging
from dataclasses import dataclass
from datetime import datetime

# Configure logging with timestamp
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'campaign_generator_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CampaignConfig:
    """Configuration settings for campaign generation."""
    STABLE_DIFFUSION_API_URL: str = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-medium"
    IMAGE_CFG_SCALE: float = 7.0
    IMAGE_STEPS: int = 50
    ASPECT_RATIO: str = "16:9"
    SEED: int = 0
    MODEL_TEMPERATURE: float = 0.7
    LLM_MODEL: str = "meta/llama-3.1-405b-instruct"

class CampaignGenerator:
    """Main class for handling campaign generation."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("NVIDIA API key not found in environment variables")
            
        self.config = CampaignConfig()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        
        # Initialize LLM
        self.llm = ChatNVIDIA(
            model=self.config.LLM_MODEL,
            api_key=self.api_key,
            temperature=self.config.MODEL_TEMPERATURE
        )
        
        # Set up temp directory for image storage
        self.temp_dir = Path(tempfile.gettempdir()) / "campaign_generator"
        self.temp_dir.mkdir(exist_ok=True)
        
    def cleanup_temp_files(self):
        """Clean up temporary image files."""
        try:
            for file in self.temp_dir.glob("*.png"):
                file.unlink()
        except Exception as e:
            logger.warning(f"Failed to clean up temp files: {e}")

    def generate_stable_diffusion_image(self, prompt: str) -> Image.Image:
        """Generate an image using NVIDIA's Stable Diffusion API."""
        try:
            payload = {
                "prompt": prompt,
                "cfg_scale": self.config.IMAGE_CFG_SCALE,
                "aspect_ratio": self.config.ASPECT_RATIO,
                "seed": self.config.SEED,
                "steps": self.config.IMAGE_STEPS,
                "negative_prompt": "",
            }

            logger.debug(f"Sending image generation request with prompt: {prompt[:100]}...")
            response = requests.post(
                self.config.STABLE_DIFFUSION_API_URL, 
                headers=self.headers, 
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            image_data = response.json().get("image")
            if not image_data:
                raise ValueError("No image data in response")
                
            image_bytes = base64.b64decode(image_data)
            return Image.open(BytesIO(image_bytes))
            
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise

    def stream_campaign(self, brief: str) -> Generator[Tuple[str, str, Optional[Image.Image]], None, None]:
        """Stream the campaign generation process step by step."""
        session_id = str(uuid.uuid4())
        logger.info(f"Starting campaign generation session {session_id}")
        
        try:
            # Step 1: Generate content
            logger.info("Generating marketing content...")
            yield "Generating marketing content...", "", None
            
            content_prompt = f"""
            Create professional marketing content for the following campaign brief:
            {brief}
            
            Provide:
            1. Headline: Attention-grabbing, max 10 words
            2. Main copy: 2-3 compelling sentences
            3. Call to action: Clear and actionable
            4. Three relevant hashtags
            
            Format the response with clear section headers and spacing.
            """
            
            content_response = self.llm.invoke([{"role": "user", "content": content_prompt}])
            content = content_response.content
            logger.debug(f"Generated content: {content[:100]}...")
            yield content, "Generating image prompt...", None

            # Step 2: Generate image prompt
            logger.info("Generating image prompt...")
            image_prompt_template = f"""
            Create a detailed image generation prompt based on this marketing content:
            {content}
            
            Focus on:
            - Visual style and mood
            - Key elements and composition
            - Color scheme
            - Artistic direction
            
            Format: Create a clear, detailed prompt suitable for Stable Diffusion.
            Avoid any text, logos, or trademarked elements.
            Keep the prompt focused on visual elements only.
            """
            
            prompt_response = self.llm.invoke([{"role": "user", "content": image_prompt_template}])
            image_prompt = prompt_response.content
            logger.debug(f"Generated image prompt: {image_prompt[:100]}...")
            yield content, image_prompt, None

            # Step 3: Generate image
            logger.info("Generating image...")
            yield content, image_prompt + "\n\nGenerating campaign visual...", None
            image = self.generate_stable_diffusion_image(image_prompt)
            
            # Save image temporarily
            temp_path = self.temp_dir / f"campaign_{session_id}.png"
            image.save(temp_path)
            logger.info(f"Saved generated image to {temp_path}")
            
            yield content, image_prompt, image

        except Exception as e:
            logger.error(f"Campaign generation failed: {e}")
            yield f"Error: {str(e)}", "", None

def create_gradio_interface() -> gr.Blocks:
    """Create and configure the Gradio interface."""
    generator = CampaignGenerator()
    
    with gr.Blocks(title="AI Campaign Generator") as demo:
        gr.Markdown("""
        # 🎨 AI Campaign Generator
        
        Generate professional marketing campaigns with AI-powered content and visuals.
        
        ### How to use:
        1. Enter your campaign brief including:
           - Campaign goals
           - Target audience
           - Key messages
           - Brand voice/tone
        2. Click 'Generate Campaign' and watch as your campaign comes to life!
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                input_text = gr.Textbox(
                    label="Campaign Brief",
                    placeholder="Describe your campaign goals, target audience, and key messages...",
                    lines=5
                )
                submit_btn = gr.Button("🚀 Generate Campaign", variant="primary")
                
            with gr.Column(scale=1):
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
                
        # Add examples
        gr.Examples(
            examples=[
                ["Create a campaign for a new eco-friendly reusable water bottle that keeps drinks cold for 24 hours. Target audience: environmentally conscious millennials who are active and health-focused."],
                ["Launch a mobile app that helps people learn meditation through short, guided sessions. Target audience: busy professionals aged 25-40 who are interested in mindfulness but struggle to find time."],
                ["Promote a subscription box service for organic, locally-sourced ingredients with recipe cards. Target audience: home cooks who value quality ingredients and want to support local farmers."]
            ],
            inputs=input_text
        )
        
        submit_btn.click(
            fn=generator.stream_campaign,
            inputs=input_text,
            outputs=[content_output, prompt_output, image_output],
            api_name="generate"
        )
        
        gr.Markdown("""
        ### Notes:
        - Content generation typically takes 10-15 seconds
        - Image generation may take up to 30 seconds
        - All generated content is temporary and will be deleted after the session
        """)
        
    return demo

if __name__ == "__main__":
    # Create and launch the interface
    demo = create_gradio_interface()
    
    # Launch with queue for better handling of multiple requests
    demo.queue()
    demo.launch(
        share=False,  # Set to True to create a public link
        debug=True,
        show_api=False
    )