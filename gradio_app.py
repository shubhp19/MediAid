import gradio as gr
import os
import time
import base64
from dotenv import load_dotenv
from gtts import gTTS  # Added for Google Text-to-Speech
from Brain import encode_image, analyze_image_with_query
from Patient_voice import transcribe_with_groq
import logging
import random


# Configure logging
logging.getLogger('asyncio').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('gradio').setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log")]
)
logger = logging.getLogger(__name__)

load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("ERROR: GROQ_API_KEY is missing! Check your .env file.")

def encode_logo(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()
logo_b64 = encode_logo("C:/Users/SHUBHAM/Downloads/Medivox-main/Medivox-main/icons/logo.png")

system_prompt = (
    "You have to act as a professional doctor."
    " With what I see, I think you have .... (Provide a concise medical opinion in max 2 sentences)."
    " No preamble, start your answer right away."
)

# Enhanced symptom detection prompt
symptom_detection_prompt = """You are a medical assistant tasked with identifying potential medical symptoms from user input. 
Analyze the provided text and determine if it contains any medical symptoms or health-related concerns (e.g., 'I have leg pain', 'feeling dizzy', 'coughing'). 
Return 'True' if symptoms are detected, 'False' otherwise. 
Do not include any additional explanation or text beyond 'True' or 'False'."""

# Encode custom icons with fallback
def encode_icon(path):
    try:
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    except FileNotFoundError:
        logger.warning(f"Icon file not found at {path}. Using default icon.")
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAABYSURBVHgB7dNBCQAwDARBE1/g2YkL/AE/g7/gA4Gphl5gG8aWPRcF0z22uE+4z4nFfcItTizuk3ZxYvEfLIm/wYr4G6yIv8GK+BusiL/BivgbnP8A9/4AtMgnU9gAAAAASUVORK5CYII="

icon_paths = {
    "attach": "icons/attach.png",
    "camera": "icons/camera.png",
    "mic": "icons/microphone.png",
    "send": "icons/send.png"
}

icons_b64 = {key: encode_icon(path) for key, path in icon_paths.items()}
custom_css = """
/* Your existing CSS */
html { height: 100%; margin: 0 !important; padding: 0 !important; background-color: #ffffff !important; }
.gradio-container { margin-top: 0 !important; padding-top: 0 !important; background-color: #ffffff !important; }
body, html, #app-container {
    margin: 0 !important;
    padding: 0 !important;
    background-color: #ffffff !important;
}
#app-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 0 !important;
    margin-top: 0 !important;
    box-sizing: border-box;
    background-color: #ffffff !important;
}
.uploaded-image {
    width: 200px;
    border-radius: 8px;
    margin: 10px 0;
}
.header {
    margin: 0;
    margin-top: 0 !important;
    padding: 0;
    padding-top: 0 !important;
    line-height: 0 !important;
    background-color: #ffffff !important;
}
.header-logo {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 0px !important;
    margin: 0;
    padding: 0;
    margin-top: -10px !important;
    margin-left: -1cm !important;
    flex-wrap: nowrap;
    background-color: #ffffff !important;
}
.logo-img {
    height: 60px;
    width: auto;
    display: inline-block;
    vertical-align: middle;
    margin-right: 0 !important;
    padding-right: 0 !important;
}
.logo-img, .logo-text {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
    background-color: transparent !important;
}
.logo-text {
    font-size: 28px;
    font-weight: bold;
    color: #2a2a2a;
    font-family: 'Poppins', sans-serif;
    margin: 0;
    padding: 0;
    vertical-align: middle;
    display: inline-block;
    background-color: transparent !important;
}
div.html-container {
    padding: 0 !important;
    margin: 0 !important;
    background-color: #ffffff !important;
}
.prose {
    margin: 0 !important;
    padding: 0 !important;
    background-color: #ffffff !important;
}
#chat-container {
    flex: 8 1 auto;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    margin-bottom: 15px;
    margin-top: 0 !important;
    overflow-y: auto;
    background: #F5FFFF !important;
    position: relative;
}
.chatbot-container {
    margin: 0;
    padding: 10px;
    background: #F5FFFF !important;
    height: 100%;
    box-sizing: border-box;
}
#chatbot {
    height: 610px !important;
    overflow: auto;
    background: #F5FFFF !important;
}
#chatbot .message {
    background: #ffffff !important;
    color: #000000 !important;
}
#chatbot .message-user {
    background: #ffffff !important;
    color: #000000 !important;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
    text-align: right;
}
#chatbot .message-user * {
    color: #000000 !important;
}
#chatbot .message-assistant {
    background: #ffffff !important;
    color: #000000 !important;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
    text-align: left;
}
#chatbot .message-assistant * {
    color: #000000 !important;
}
#chatbot .message-assistant:first-child {
    background: #ffffff !important;
    color: #000000 !important;
}
#chatbot .message-assistant:first-child * {
    color: #000000 !important;
}
#chatbot .camera-wrapper {
    max-width: 75% !important;
    margin: 5px 0 5px auto !important;
    padding: 0 !important;
    background: transparent !important;
    display: block !important;
    text-align: right !important;
}
#chatbot .input-message {
    background: #F5FFFF !important;
    color: #000000 !important;
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
    border: 1px solid #e0e0e0;
    position: relative;
    overflow: visible;
}
#camera-input, #mic-input {
    max-width: 100%;
    margin: 0 auto;
    display: none;
}
#camera-input.visible {
    display: block !important;
    width: 100 !important;
    max-width: 400px !important;
    background: #F5FFFF !important;
    padding: 10px !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 5px !important;
    margin: 0 auto 10px auto !important;
    box-sizing: border-box !important;
    text-align: center !important;
    z-index: 1000 !important;
}
#camera-input video {
    width: 100% !important;
    height: auto !important;
    border-radius: 5px !important;
}
#mic-input.visible {
    display: block !important;
    width: 100%;
    max-width: 400px;
    background: #F5FFFF !important;
    padding: 10px;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    margin: 0 auto 10px auto;
    box-sizing: border-box;
    text-align: center;
    z-index: 1000;
}
#mic-input .gr-audio-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
}
#mic-input .gr-audio-container button {
    background-color: #ff5733;
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
}
#mic-input .gr-audio-container button:hover {
    background-color: #e04e2d;
}
#input-panel {
    display: flex;
    align-items: center;
    padding: 8px;
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 25px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    width: 90%;
    margin: 0 auto;
    flex-wrap: nowrap;
    justify-content: flex-start;
    gap: 5px;
}
#input-panel .icon-btn {
    width: 32px;
    height: 32px;
    padding: 0;
    margin: 0;
    border: none;
    background-color: transparent;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    flex: 0 0 auto;
    min-width: 32px;
    cursor: pointer;
}
#send-btn {
    width: 40px;
    height: 40px;
    background-size: contain;
}
#attach-btn {
    background-image: url('data:image/png;base64,{{attach_b64}}');
    display: flex;
    align-items: center;
    justify-content: center;
}
#camera-btn {
    background-image: url('data:image/png;base64,{{camera_b64}}');
    display: flex;
    align-items: center;
    justify-content: center;
    background-size: contain;
    background-repeat: no-repeat;
}
#mic-btn {
    background-image: url('data:image/png;base64,{{mic_b64}}');
    display: flex;
    align-items: center;
    justify-content: center;
    background-size: contain;
    background-repeat: no-repeat;
}
#send-btn {
    background-image: url('data:image/png;base64,{{send_b64}}');
    display: flex;
    align-items: center;
    justify-content: center;
}
#textbox {
    flex: 1 1 auto;
    min-height: 40px;
    border-radius: 8px;
    padding: 0;
    margin: 0 15px;
    display: flex;
    align-items: center;
    max-width: 80%;
    min-width: 300px;
    background-color: #ffffff !important;
}
#textbox textarea {
    height: 32px !important;
    font-size: 16px;
    border: none;
    outline: none;
    background: transparent;
    resize: none;
    padding: 0 10px;
    width: 100%;
    line-height: 32px;
    box-sizing: border-box;
    background-color: transparent !important;
    color: #000000 !important;
}
#textbox textarea::placeholder {
    color: #888;
    opacity: 1;
}
.uploaded-image {
    width: 200px;
    border-radius: 8px;
    margin: 10px 0;
}
.gradio-container .gr-block.gr-box {
    margin-top: 0 !important;
    padding-top: 0 !important;
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
    background-color: #ffffff !important;
}
.gradio-container > .gr-block:first-child {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
    background-color: #ffffff !important;
}
#app-container {
    padding-top: 0 !important;
    margin-top: 0 !important;
    background-color: #ffffff !important;
}
@media (prefers-color-scheme: dark) {
  #chatbot, .chatbot-container, #chat-container {
    background: #F5FFFF !important;
  }
  .gradio-container #chatbot .message, 
  .gradio-container #chatbot .message-user, 
  .gradio-container #chatbot .message-assistant,
  .gradio-container #chatbot .message-assistant:first-child,
  .gradio-container #chatbot .input-message {
    background: #ffffff !important;
    color: #000000 !important;
  }
  .gradio-container #chatbot .message *, 
  .gradio-container #chatbot .message-user *, 
  .gradio-container #chatbot .message-assistant *,
  .gradio-container #chatbot .message-assistant:first-child *,
  .gradio-container #chatbot .input-message *,
  .gradio-container-5-29-0 #chatbot .prose *,
  .gradio-container-5-29-0 .prose * {
    color: #000000 !important;
  }
  /* Aggressive override for prose and all elements */
  :where(.gradio-container .prose *),
  :where(.gradio-container-5-29-0 .prose *) {
    color: #000000 !important;
  }
  :where(.gradio-container *),
  :where(.gradio-container-5-29-0 *) {
    --body-text-color: #000000 !important;
    color: #000000 !important;
  }
  /* New CSS to align mic input to the right */
  #chatbot .message.message-user.mic-wrapper {
      text-align: right !important;
      margin-left: auto !important;
      margin-right: 0 !important;
  }
}
@media screen and (max-width: 600px) {
  #input-panel {
    flex-wrap: wrap !important;
    justify-content: space-between !important;
    padding: 6px !important;
    width: 95% !important;
  }
  #textbox {
    min-width: 100% !important;
    max-width: 100% !important;
    margin: 10px 0 !important;
  }
  #textbox textarea {
    font-size: 16px !important;
    width: 100% !important;
  }
  #send-btn {
    flex-shrink: 0 !important;
    width: 40px !important;
    height: 40px !important;
  }
  #input-panel .icon-btn {
    width: 32px !important;
    height: 32px !important;
  }
}
"""

# Re-apply icon replacements
custom_css = custom_css.replace("{{attach_b64}}", icons_b64["attach"])
custom_css = custom_css.replace("{{camera_b64}}", icons_b64["camera"])
custom_css = custom_css.replace("{{mic_b64}}", icons_b64["mic"])
custom_css = custom_css.replace("{{send_b64}}", icons_b64["send"])

def text_to_speech_with_gtts(text, output_path):
    """Generate speech from text using gTTS and save to output_path."""
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(output_path)
        logger.info(f"Audio generated with gTTS and saved to {output_path}")
    except Exception as e:
        logger.error(f"Error generating audio with gTTS: {e}")
        raise

def detect_symptoms_with_model(text):
    """Use the model to detect symptoms in the provided text."""
    try:
        query = symptom_detection_prompt + f"\nUser input: {text}"
        response = analyze_image_with_query(
            query=query,
            encoded_image=None,
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        )
        logger.info(f"Symptom detection response for text '{text}': {response}")
        return response.strip().lower() == "true"
    except Exception as e:
        logger.error(f"Error in symptom detection for text '{text}': {e}")
        return False

def clean_user_content(msg):
    """Clean user content to extract text for analysis."""
    content = msg.get("content", "")
    if isinstance(content, str) and not content.strip().startswith("<img") and "🗣️" not in content:
        return content.lower().strip()
    return ""

def process_inputs(history, user_text=None, audio_file=None, image_file=None):
    chat_history = history or []
    if not chat_history:
        chat_history.append({"role": "assistant", "content": "Hi, I’m MediAid — your AI medical assistant. How can I help you today?"})
    
    user_name = None
    # Extract name from the latest user input or history
    if user_text and isinstance(user_text, str):
        user_text_lower = user_text.lower().strip()
        # Check for "hi this is [name]"
        if user_text_lower.startswith("hi this is"):
            try:
                user_name = user_text_lower.split("hi this is")[1].strip().split()[0].capitalize()
            except IndexError:
                pass
        # Check for "I am", "I'm", or "my name is"
        elif "i am" in user_text_lower:
            try:
                user_name = user_text_lower.split("i am")[1].strip().split()[0].capitalize()
            except IndexError:
                pass
        elif "i'm" in user_text_lower:
            try:
                user_name = user_text_lower.split("i'm")[1].strip().split()[0].capitalize()
            except IndexError:
                pass
        elif "my name is" in user_text_lower:
            try:
                user_name = user_text_lower.split("my name is")[1].strip().split()[0].capitalize()
            except IndexError:
                pass
        # Check for name after greeting (e.g., "hi jack")
        greetings = ["hi", "hello", "hey", "good morning", "good evening"]
        if not user_name and any(user_text_lower.startswith(greet) for greet in greetings):
            for greet in greetings:
                if user_text_lower.startswith(greet):
                    remaining_text = user_text_lower[len(greet):].strip()
                    if remaining_text:
                        try:
                            user_name = remaining_text.split()[0].capitalize()
                            break
                        except IndexError:
                            pass
        if user_name and len(chat_history) == 1 and chat_history[0]["role"] == "assistant":
            chat_history[0]["content"] = f"Welcome to Medical Assistant, {user_name}!" if user_name else "Welcome to Medical Assistant!"

    # Check history for name if not found in current input
    if not user_name and chat_history:
        for msg in chat_history:
            if msg.get("role") == "user" and isinstance(msg.get("content"), str):
                content_lower = msg["content"].lower().strip()
                if "hi this is" in content_lower:
                    try:
                        user_name = content_lower.split("hi this is")[1].strip().split()[0].capitalize()
                        break
                    except IndexError:
                        continue
                elif "i am" in content_lower:
                    try:
                        user_name = content_lower.split("i am")[1].strip().split()[0].capitalize()
                        break
                    except IndexError:
                        continue
                elif "i'm" in content_lower:
                    try:
                        user_name = content_lower.split("i'm")[1].strip().split()[0].capitalize()
                        break
                    except IndexError:
                        continue
                elif "my name is" in content_lower:
                    try:
                        user_name = content_lower.split("my name is")[1].strip().split()[0].capitalize()
                        break
                    except IndexError:
                        continue

    doctor_response = "No medical insights available."

    try:
        if audio_file:
            audio_path = audio_file if isinstance(audio_file, str) else audio_file[0] if isinstance(audio_file, tuple) else None
            if audio_path and os.path.exists(audio_path):
                logger.info(f"Transcribing audio file: {audio_path}")
                transcription = transcribe_with_groq(
                    stt_model="whisper-large-v3",
                    audio_filepath=audio_path,
                    GROQ_API_KEY=GROQ_API_KEY
                )
                if not transcription:
                    raise ValueError("Transcription failed.")
                chat_history.append({"role": "user", "content": f"🗣️ {transcription}"})
                user_text = transcription
            else:
                raise FileNotFoundError(f"Audio file not found at {audio_path}")

        if user_text and isinstance(user_text, str):
            chat_history.append({"role": "user", "content": user_text})

        encoded_image = None
        if image_file:
            image_path = image_file if isinstance(image_file, str) else image_file[0] if isinstance(image_file, tuple) else None
            if image_path and os.path.exists(image_path):
                logger.info(f"Image file received: {image_path}")
                encoded_image = encode_image(image_path)
                image_component = gr.Image(value=image_path, type="filepath", width=200, height=200)
                chat_history.append({"role": "user", "content": image_component})
        # Detect symptoms in all user text
        all_user_text = " ".join([clean_user_content(msg) for msg in chat_history if msg.get("role") == "user"])
        logger.info(f"All user text: {all_user_text}")
        has_symptom = detect_symptoms_with_model(all_user_text)

        # Handle responses based on symptoms first
        if user_text and isinstance(user_text, str):
            user_text_lower = user_text.lower().strip()
            if has_symptom or encoded_image:
                query = system_prompt + " " + (all_user_text if not encoded_image else "")
                logger.info(f"Query sent to analyze_image_with_query: {query}")
                try:
                    doctor_response = analyze_image_with_query(
                        query=query,
                        encoded_image=encoded_image,
                        model="meta-llama/llama-4-scout-17b-16e-instruct"
                    )
                except Exception as e:
                    doctor_response = f"Sorry, there was an issue processing your request. Please try again."
                    logger.error(f"Error in analyze_image_with_query: {e}")
                if not doctor_response:
                    raise ValueError("Analysis failed: No response returned.")
                logger.info(f"Doctor response received: {doctor_response}")
            else:
                # Check for short affirmatives
                acknowledgements = ["thank you", "thanks", "ok", "okay", "got it", "cool", "alright"]
                if any(ack in user_text_lower for ack in acknowledgements) and not has_symptom and not encoded_image:
                    responses = [
                        "You're welcome!",
                        "Let me know if there's anything else I can assist with.",
                        "Take care!"
                    ]
                    doctor_response = random.choice(responses)
                else:
                    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
                    intro_keywords = ["i am", "i'm", "my name is", "hi this is"]
                    is_greeting_or_intro = any(user_text_lower.startswith(greet) for greet in greetings) or any(kw in user_text_lower for kw in intro_keywords)

                    if is_greeting_or_intro and not has_symptom and not encoded_image:
                        if not user_name:
                            for greet in greetings:
                                if user_text_lower.startswith(greet):
                                    doctor_response = f"{greet.capitalize()}, I'm your medical assistant. Please describe any symptoms."
                                    break
                        else:
                            doctor_response = f"Hello {user_name}! I'm your medical assistant. How can I help you today?"
                    elif not has_symptom and not encoded_image:
                        doctor_response = f"{user_name}, please describe any symptoms or health concerns." if user_name else "Please describe any symptoms or health concerns."

        elif encoded_image and not user_text:
            query = system_prompt
            logger.info(f"Query sent to analyze_image_with_query: {query}")
            try:
                doctor_response = analyze_image_with_query(
                    query=query,
                    encoded_image=encoded_image,
                    model="meta-llama/llama-4-scout-17b-16e-instruct"
                )
            except Exception as e:
                doctor_response = f"Sorry, there was an issue processing your request. Please try again."
                logger.error(f"Error in analyze_image_with_query: {e}")
            if not doctor_response:
                raise ValueError("Analysis failed: No response returned.")
            logger.info(f"Doctor response received: {doctor_response}")

        chat_history.append({"role": "assistant", "content": doctor_response})

        output_audio_path = "response.mp3"
        text_to_speech_with_gtts(doctor_response, output_audio_path)
        if not os.path.exists(output_audio_path):
            raise FileNotFoundError(f"Text-to-speech failed: Output file {output_audio_path} not created.")
        time.sleep(0.5)

        return chat_history, chat_history, output_audio_path, gr.update(visible=False), gr.update(visible=False), ""
    except Exception as e:
        logger.error(f"Error in process_inputs: {e}")
        chat_history.append({"role": "assistant", "content": f"Sorry, an error occurred. Please try again later."})
        return chat_history, chat_history, None, gr.update(visible=False), gr.update(visible=False), ""

def open_camera(history):
    logger.info("Camera button clicked, opening webcam input")
    chat_history = history or []
    # Clear any previous input placeholders
    chat_history = [msg for msg in chat_history if msg.get("content") not in ["camera_input_placeholder", "mic_input_placeholder"]]
    chat_history.append({"role": "user", "content": "Click the capture button to take a photo"})
    return chat_history, gr.update(visible=True), gr.update(visible=False)

def handle_captured_image(history, image_file):
    logger.info("Camera input changed, processing image")
    chat_history = history or []
    if image_file:
        image_path = image_file if isinstance(image_file, str) else image_file[0] if isinstance(image_file, tuple) else None
        if os.path.exists(image_path):
            if chat_history and chat_history[-1]["content"] == "camera_input_placeholder":
                chat_history.pop()
            image_component = gr.Image(value=image_path, type="filepath", width=200, height=200)
            chat_history.append({"role": "user", "content": image_component})
            response = analyze_image_with_query(
                query=system_prompt,
                encoded_image=encode_image(image_path),
                model="meta-llama/llama-4-scout-17b-16e-instruct"
            )
            chat_history.append({"role": "assistant", "content": response})
            text_to_speech_with_gtts(response, "response.mp3")
            output_audio_path = "response.mp3"
            return chat_history, chat_history, output_audio_path, gr.update(visible=False), gr.update(visible=False), ""
    return chat_history, chat_history, None, gr.update(visible=False), gr.update(visible=False), ""

def insert_mic_input(history):
    logger.info("Mic button clicked, inserting mic input UI")
    chat_history = history or []
    # Clear any previous input placeholders
    chat_history = [msg for msg in chat_history if msg.get("content") not in ["camera_input_placeholder", "mic_input_placeholder"]]
    chat_history.append({"role": "user", "content": "Click the record button to start speaking"})
    return chat_history, gr.update(visible=False), gr.update(visible=True)

def log_mic_input(history, audio):
    logger.info("Mic input changed, processing audio")
    chat_history = history or []
    if audio:
        audio_path = audio if isinstance(audio, str) else audio[0] if isinstance(audio, tuple) else None
        if os.path.exists(audio_path):
            if chat_history and chat_history[-1]["content"] == "mic_input_placeholder":
                chat_history.pop()
            transcription = transcribe_with_groq(
                stt_model="whisper-large-v3",
                audio_filepath=audio_path,
                GROQ_API_KEY=GROQ_API_KEY
            )
            if transcription:
                chat_history.append({"role": "user", "content": f"Voice: {transcription}"})
                result = process_inputs(chat_history, user_text=transcription, audio_file=None, image_file=None)
                # Return updated state with mic input hidden
                return result[0], result[1], result[2], result[3], gr.update(visible=False), result[5]
    return chat_history, chat_history, None, gr.update(visible=False), gr.update(visible=False), ""

with gr.Blocks(css=custom_css, elem_id="app-container") as app:
    history = gr.State([])

    gr.HTML(f"""
        <div class="header-logo" style="display: flex; align-items: center;">
            <div class="logo-image-wrapper">
                <img src='data:image/png;base64,{logo_b64}' alt='MediAid Logo' class='logo-img'>
            </div>
            <div class="logo-text" style="display: inline-block; vertical-align: middle;">MediAid</div>
        </div>
    """, elem_classes="header")

    with gr.Column(elem_id="chat-container"):
        chatbot = gr.Chatbot(elem_id="chatbot", show_label=False, elem_classes="chatbot-container", type="messages", value=[{"role": "assistant", "content": "Hi, I’m MediAid — your AI medical assistant. How can I help you today?"}], height=500)
        camera_input = gr.Image(sources=["webcam"], type="filepath", label="Capture", visible=False, elem_id="camera-input")
        mic_input = gr.Audio(sources=["microphone"], type="filepath", visible=False, elem_id="mic-input")

    with gr.Row(elem_id="input-panel"):
        attach_btn = gr.UploadButton(label="", file_types=["image"], elem_id="attach-btn", elem_classes=["icon-btn"])
        camera_btn = gr.Button("", elem_id="camera-btn", elem_classes=["icon-btn"])
        mic_btn = gr.Button("", elem_id="mic-btn", elem_classes=["icon-btn"])
        txt = gr.Textbox(show_label=False, placeholder="Describe symptoms or ask a question...", container=False, elem_id="textbox")
        send_btn = gr.Button("", elem_id="send-btn", elem_classes=["icon-btn"])

    output_audio = gr.Audio(type="filepath", label="Audio Output", autoplay=True, visible=False)

    send_btn.click(
        fn=process_inputs,
        inputs=[history, txt, mic_input, attach_btn],
        outputs=[chatbot, history, output_audio, camera_input, mic_input, txt],
    )

    txt.submit(
        fn=process_inputs,
        inputs=[history, txt, mic_input, attach_btn],
        outputs=[chatbot, history, output_audio, camera_input, mic_input, txt],
    )

    attach_btn.upload(
        fn=process_inputs,
        inputs=[history, gr.State(value=None), gr.State(value=None), attach_btn],
        outputs=[chatbot, history, output_audio, camera_input, mic_input, txt],
    )

    camera_btn.click(
    fn=open_camera,
    inputs=[history],
    outputs=[chatbot, camera_input, mic_input],
    js="""
    function injectWebcam() {
        console.log('Attempting to inject webcam input');
        try {
            const chat = document.querySelector('#chatbot');
            const camera = document.querySelector('#camera-input');
            const mic = document.querySelector('#mic-input'); // Fixed typo from queryselector to querySelector
            if (chat && camera) {
                if (mic) mic.classList.remove('visible');
                if (!camera.classList.contains('visible')) {
                    camera.classList.add('visible');
                    const cameraWrapper = document.createElement('div');
                    cameraWrapper.className = 'camera-wrapper';
                    cameraWrapper.appendChild(camera);
                    chat.appendChild(cameraWrapper);
                    console.log('Webcam input appended to chat');
                    chat.scrollTop = chat.scrollHeight;
                } else {
                    console.log('Camera input already visible');
                }
            } else {
                console.error('Chat or camera input not found');
            }
        } catch (e) {
            console.error('Error in injectWebcam:', e);
        }
    }
    """
)
    camera_input.change(
        fn=handle_captured_image,
        inputs=[history, camera_input],
        outputs=[chatbot, history, output_audio, camera_input, mic_input, txt],
        js="""
        function hideCameraInput(history, image_file) {
            console.log('Hiding camera input');
            try {
                const camera = document.querySelector('#camera-input');
                if (camera) {
                    camera.style.display = 'none';
                    camera.classList.remove('visible');
                    const cameraWrapper = camera.closest('.camera-wrapper') || camera.parentElement;
                    if (cameraWrapper) {
                        cameraWrapper.remove();
                    }
                }
                const chat = document.querySelector('#chatbot');
                if (chat) {
                    chat.scrollTop = chat.scrollHeight;
                }
            } catch (e) {
                console.error('Error in hideCameraInput:', e);
            }
            return [history, image_file];
        }
        """
    )

    mic_btn.click(
        fn=insert_mic_input,
        inputs=[history],
        outputs=[chatbot, camera_input, mic_input],
        js="""
        function injectMic() {
            console.log('Attempting to inject mic input');
            const chat = document.querySelector('#chatbot');
            const mic = document.querySelector('#mic-input');
            const camera = document.querySelector('#camera-input');

            if (chat && mic) {
                if (camera) camera.classList.remove('visible');
                if (mic.classList.contains('visible')) {
                    console.log('Mic input already visible');
                    return;
                }
                const micWrapper = document.createElement('div');
                micWrapper.className = 'message message-user mic-wrapper';
                micWrapper.style.marginLeft = 'auto'; // Pushes it to the right
                micWrapper.style.marginRight = '0';
                micWrapper.appendChild(mic);
                chat.appendChild(micWrapper);
                mic.classList.add('visible');
                console.log('Mic input appended to chat');
                chat.scrollTop = chat.scrollHeight;
            } else {
                console.error('Chat or mic input not found');
            }
        }
        """
    )

    mic_input.change(
        fn=log_mic_input,
        inputs=[history, mic_input],
        outputs=[chatbot, history, output_audio, camera_input, mic_input, txt],
        js="""
        function hideMicInput(history, audio) {
            console.log('Hiding mic input');
            try {
                const mic = document.querySelector('#mic-input');
                if (mic) {
                    mic.style.display = 'none';
                    mic.classList.remove('visible');
                    const micWrapper = mic.closest('.mic-wrapper') || mic.parentElement;
                    if (micWrapper) {
                        micWrapper.remove();
                    }
                }
                const chat = document.querySelector('#chatbot');
                if (chat) {
                    chat.scrollTop = chat.scrollHeight;
                }
            } catch (e) {
                console.error('Error in hideMicInput:', e);
            }
            return [history, audio];
        }
        """
    )

if __name__ == "__main__":
    app.launch(debug=True, share=True)