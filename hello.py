import chainlit as cl
from litellm import completion
import base64
import os
from dotenv import load_dotenv
load_dotenv()

# Configuration - change these to switch models
API_KEY = os.getenv("ANTHROPIC_API_KEY")  
MODEL_NAME = "claude-3-7-sonnet-20250219"  # Must support images

# Store conversation history

# Configuration - change these to switch models
 # Must support images

# Store conversation history in Chainlit's session
@cl.on_chat_start
async def start():
    cl.user_session.set("conversation_history", [])

def encode_image(image_file):
    """Convert uploaded image to base64 string."""
    return base64.b64encode(image_file.read()).decode("utf-8")

async def get_response(user_input, image_base64=None):
    # Get conversation history from session
    conversation_history = cl.user_session.get("conversation_history")
    
    # Prepare the message
    message = {"role": "user", "content": []}
    
    # Add text if provided
    if user_input:
        message["content"].append({"type": "text", "text": user_input})
    
    # Add image if provided
    if image_base64:
        message["content"].append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",  # Adjust based on your needs (jpeg, png, etc.)
                "data": image_base64
            }
        })
    
    # Add message to conversation history
    conversation_history.append(message)
    
    # Get response using LiteLLM
    response = completion(
        model=MODEL_NAME,
        messages=conversation_history,
        api_key=API_KEY,
        max_tokens=1000
    )
    
    # Extract the assistant's response
    assistant_response = response.choices[0].message.content
    
    # Add assistant's response to conversation history
    conversation_history.append({"role": "assistant", "content": assistant_response})
    
    # Update session history
    cl.user_session.set("conversation_history", conversation_history)
    
    return assistant_response

@cl.on_message
async def main(message: cl.Message):
    # Handle text input
    user_input = message.content
    
    # Handle file upload (photo)
    image_base64 = None
    if message.elements:  # Check if any files were uploaded
        for element in message.elements:
            if element.mime in ["image/jpeg", "image/png"]:
                image_base64 = encode_image(element.content)
                break
    
    # Get and send response
    response = await get_response(user_input, image_base64)
    await cl.Message(content=response).send()