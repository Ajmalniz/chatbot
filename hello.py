import streamlit as st
from litellm import completion
import base64

# Configuration - change these to switch models
API_KEY = "YOUR_ANTHROPIC_API_KEY_HERE"
MODEL_NAME = "anthropic/claude-3-5-sonnet-20241022"  # Must support images

# Store conversation history
conversation_history = []

def encode_image(image_file):
    """Convert uploaded image to base64 string."""
    return base64.b64encode(image_file.read()).decode("utf-8")

def get_response(user_input, image_base64=None):
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
    
    return assistant_response

# Streamlit frontend
st.title("Chatbot with Photo Upload")

# Display chat history
for message in conversation_history:
    if message["role"] == "user":
        content = [c for c in message["content"] if c["type"] == "text"]
        if content:
            st.write(f"You: {content[0]['text']}")
    else:
        st.write(f"Assistant: {message['content']}")

# Input box for text
user_input = st.text_input("Type your message:")

# File uploader for photos
uploaded_file = st.file_uploader("Attach a photo (optional)", type=["jpg", "jpeg", "png"])

# Process input when submitted
if st.button("Send") and (user_input or uploaded_file):
    image_base64 = encode_image(uploaded_file) if uploaded_file else None
    response = get_response(user_input, image_base64)
    st.experimental_rerun()  # Refresh to show new messages
