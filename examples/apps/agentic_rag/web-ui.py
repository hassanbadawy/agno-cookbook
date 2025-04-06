#-----------------Logger Setup-----------------
import sys
sys.path.append("./services/utils")
from logger import setup_logging
logger = setup_logging(__file__)
#------------------------------------------------
try:
    import streamlit as st
    import requests
    from pathlib import Path
    from PIL import Image
    import uuid
    import os
    import traceback
except Exception as e:
    logger.error(f"❌ Error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

API_URL = "http://localhost:8001/task-manager"
        

# Initialize session state for a specific user
def initialize_user_session(session_id):
    """
    Initializes or retrieves user-specific session state.
    
    Args:
        session_id (str): The unique identifier for the current user session.
    """
    # Create a namespace for this user if it doesn't exist
    if "users" not in st.session_state:
        st.session_state["users"] = {}
        
    if session_id not in st.session_state["users"]:
        st.session_state["users"][session_id] = {
            "messages": [{"role": "assistant", "content": "How can I help you?"}],
            "current_image_url": None,
            "current_image_display": None,
            "debug_info": None
        }
    
    return st.session_state["users"][session_id]

# Get the current user's data
def get_user_data():
    """Returns the session data for the current user."""
    return st.session_state["users"][session_id]

# Save uploaded image with user-specific path
def save_uploaded_image(uploaded_image, session_id):
    """
    Saves the uploaded image with a unique name in a user-specific directory.
    
    Args:
        uploaded_image: The uploaded image file.
        session_id: The user's session ID.
    
    Returns:
        str: The URL where the image is accessible.
    """
    try:
        # Create user-specific directory
        user_dir = save_dir / session_id
        user_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"demo_{uuid.uuid4().hex}.jpg"
        save_path = user_dir / unique_filename
        
        # Save the image
        image = Image.open(uploaded_image)
        image.save(save_path, format='JPEG')
        logger.info(f"💾 Image saved to {save_path}")
        CONTAINER_NAME = os.environ.get("AGENTIC_CONTAINER", "localhost")
        # Return URL with session_id in path
        return f"http://{CONTAINER_NAME}:8003/web-ui/{session_id}/{unique_filename}"
    except Exception as e:
        st.error(f"❌ Error saving image: {str(e)}")
        logger.error(f"❌ Error saving image: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Update functions to use user-specific data
def update_chat_history(role, msg, session_id):
    """
    Updates the chat history for a specific user.
    
    Args:
        role (str): The role of the message sender.
        msg: The message object.
        session_id (str): The user's session ID.
    
    Returns:
        tuple: (text, image_url)
    """
    user_data = get_user_data()
    text = ""
    image_url = user_data.get("current_image_url", "")
    
    if msg.files:
        # Handle new image input
        with st.chat_message(role):
            st.image(msg.files[0])
            st.write("Image attached")
        
        user_data["messages"].append({
            "role": role,
            "content": "Image attached",
            "image": msg.files[0]
        })
        
        # Save new image and update session state
        image_url = save_uploaded_image(msg.files[0], session_id)
        user_data["current_image_url"] = image_url
        user_data["current_image_display"] = msg.files[0]
        
        if role=='user' and not msg.text:
            text = "What do you see in this image?"
    
    if msg.text:
        # Handle text input
        with st.chat_message(role):
            st.write(msg.text)
        
        if msg.text.lower() == "clear":
            user_data["messages"] = []
            user_data["current_image_url"] = None
            user_data["current_image_display"] = None
            st.rerun()
            return
        
        # Check if user wants to remove the current image
        if msg.text.lower() in ["remove image", "delete image", "clear image"]:
            user_data["current_image_url"] = None
            user_data["current_image_display"] = None
            text = "Image removed"
            user_data["messages"].append({"role": role, "content": text})
            return text, ""
        
        user_data["messages"].append({"role": role, "content": msg.text})
        text = msg.text
    
    # Display the current image in the sidebar if it exists
    if user_data["current_image_display"]:
        with st.sidebar:
            st.subheader("Current Image")
            st.image(user_data["current_image_display"], caption="Current Context Image", use_container_width=True)
    
    return text, image_url

def display_conversation_history(session_id):
    """
    Displays the conversation history for a specific user.
    
    Args:
        session_id (str): The user's session ID.
    """
    user_data = get_user_data()
    for message in user_data["messages"]:
        with st.chat_message(message["role"]):
            if "image" in message:
                st.image(message["image"])
            st.write(message["content"])

def initialize_session_state():
    """
    Initializes the session state for chat messages and current image if not already set.
    """
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    if "current_image_url" not in st.session_state:
        st.session_state["current_image_url"] = None
    if "current_image_display" not in st.session_state:
        st.session_state["current_image_display"] = None

def display_processed_image_in_sidebar(image_url):
    """
    Displays the processed image in the sidebar with a download link.
    
    Args:
        image_url (str): The URL of the processed image.
    """
    with st.sidebar:
        st.image(image_url, caption="Processed Image", use_container_width=True)
        st.markdown(f"[Download the processed image]({image_url})")

def send_api_request(question, image_url):
    """
    Sends the user question and optional image URL to the API.
    
    Args:
        question (str): The user question.
        image_url (str): The URL of the uploaded image.
    
    Returns:
        dict: The API response.
    """
    data = {"question": question, "image_url": image_url or ""}
    logger.info(f"📤 API request data: {data}")

    try:
        response = requests.post(API_URL, json=data)
        response.raise_for_status()  # Raise an error for bad responses.
        result = response.json()
        logger.info(f"📥 API response: {result}")
        return result
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error sending request: {e}")
        logger.error(f"❌ Error sending request: {e}")
        logger.error(traceback.format_exc())
        if response is not None:
            logger.error(f"Response content: {response.content}")
        return None
    except ValueError as e:
        st.error(f"❌ Error parsing response: {e}")
        logger.error(f"❌ Error parsing response: {e}")
        logger.error(traceback.format_exc())
        return None
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
        logger.error(f"❌ An unexpected error occurred: {e}")
        logger.error(traceback.format_exc())
        return None


# Update response parser to handle user paths
class ResponseParser:
    def __init__(self, response, session_id):
        self.response = response
        self.session_id = session_id
        self.text = ""
        self.files = []
        self.parse()
    
    def parse(self):
        message = self.response.get("message", "")
        # Remove markdown code block formatting if present
        if message.startswith("```") and message.endswith("```"):
            self.text = message[3:-3].strip()
        else:
            self.text = message
            
        image_url = self.response.get("image_url", "")
        self.files = []
        if image_url:
            meta_data = self.response.get("metadata", {})
            if meta_data:
                filepath = meta_data.get("filepath", "")
                self.files.append(filepath)
        return self

try:
    # Streamlit UI setup
    st.title("💬 MetaVision")

    session_id = st.context.cookies["_streamlit_xsrf"].split("|")[-1]
    # Create directory if it doesn't exist
    save_dir = Path("artifacts/img-svr/web-ui")
    save_dir.mkdir(parents=True, exist_ok=True)

    # Initialize user-specific session state
    initialize_user_session(session_id)
    user_data = get_user_data()

    debug = True
    if debug:
        st.sidebar.title("Debug Information")
        st.sidebar.write(f"Session ID: {session_id}")
        
    # Initialize session state for chat messages
    initialize_session_state()

    # Initialize session state for debug info if not already set
    if "debug_info" not in st.session_state:
        st.session_state["debug_info"] = None
        
    # Display conversation history specific to this user
    display_conversation_history(session_id)

    msg = st.chat_input("Upload Image, or ask something...", accept_file=True, file_type=["jpg", "jpeg", "png"])
    # Process new user input
    if msg:
        # Update the user-specific chat history
        logger.info(f"📝 User message from {session_id}: {msg}")
        query_text, image_url = update_chat_history("user", msg, session_id)
        
        # Use persisted image URL if one exists for this user
        if not image_url and user_data.get("current_image_url"):
            image_url = user_data["current_image_url"]
        
        # Send request to API
        response = send_api_request(query_text, image_url)
        if response:
            # Parse the response for this user
            masg_parser = ResponseParser(response, session_id)
            logger.info(f"📝 Response for {session_id}: {masg_parser.text}")
            
            # Create message object for the assistant's response
            from types import SimpleNamespace
            assistant_msg = SimpleNamespace(text=masg_parser.text, files=masg_parser.files)
            
            # Update the user's chat history with assistant's response
            update_chat_history("assistant", assistant_msg, session_id)
            
            # Store debug info for this user
            if debug:
                user_data["debug_info"] = response

    # Display debug info if available
    if debug and user_data.get("debug_info"):
        with st.sidebar:
            with st.expander("Debug Information"):
                st.json(user_data["debug_info"])
except Exception as e:
    logger.error(f"❌ Error: {str(e)}")
    logger.error(traceback.format_exc())
    raise