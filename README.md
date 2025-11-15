# MediAid
MediAid is an intelligent medical assistant web app that helps users interact with AI using text, voice, and images. Built using Gradio, it provides real-time medical insights, symptom detection, and conversational support — all in an intuitive chat interface.
“One of the most impactful projects I’ve built is called MediAid, a multimodal AI healthcare assistant. The main idea was to make medical information more accessible and reliable.
Most chatbots today are text-only, which is a limitation — in healthcare, users often prefer speaking naturally or showing images of symptoms rather than typing. So, I designed MediAid to handle text, voice, and image inputs, and generate instant answers in both text and audio formats.

I started by collecting verified medical data from public and trusted sources like WHO, CDC, and PubMed. I extracted and cleaned the text, split it into small, context-friendly chunks, and converted each chunk into a vector embedding using a transformer-based model. These embeddings were stored in a FAISS vector database, which enables fast semantic search when a user asks a question.

Then I built a retrieval-augmented generation pipeline (RAG). Whenever a user asks something, the system converts the question into an embedding, searches FAISS for similar chunks, and attaches those retrieved texts to the prompt before sending it to the Groq LLM (Vision + Text). The model reasons over that retrieved data to ensure answers are fact-based and not hallucinated.

For multimodal input, I used Whisper on Groq for speech-to-text, base64 encoding for image processing, and direct text handling for normal queries. I unified all inputs into a single structured format before passing them to the LLM.

After the LLM generates a response, I used gTTS and ElevenLabs for text-to-speech conversion, so users can hear the answer spoken back to them. Finally, I built the frontend using Gradio, which supports chat, microphone, and image-upload components out of the box. Each user action in Gradio triggers a backend Python function that handles preprocessing, retrieval, reasoning, and output generation.

All of this forms a real-time, multimodal medical assistant that’s accessible, fast, and factual. The tech stack includes Python, Groq API, LangChain, FAISS, Gradio, Whisper, gTTS, ElevenLabs, ffmpeg, and dotenv. The focus was on designing a modular, scalable AI system where every layer — from data to LLM to voice output — works seamlessly together.”
