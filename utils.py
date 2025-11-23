import os
import json
import speech_recognition as sr
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize LLM based on provider
def get_llm(api_key, provider="OpenAI"):
    if provider == "OpenAI":
        return ChatOpenAI(api_key=api_key, model="gpt-3.5-turbo")
    elif provider == "Gemini":
        return ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-2.5-flash")
    return None

def get_ai_question(profile, history, api_key, provider="OpenAI"):
    """Generates the next interview question."""
    llm = get_llm(api_key, provider)
    if not llm:
        return "Error: Invalid API Key or Provider"

    # Construct context from history
    history_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in history])
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are a professional interviewer conducting a job interview for a {profile} position.
        
        Previous conversation:
        {history}
        
        Based on the previous conversation (if any), ask the NEXT relevant interview question. 
        Do not repeat questions. 
        Keep the question professional and concise.
        If this is the first question, start with a standard introductory question for the role.
        Only output the question itself.
        """
    )
    
    try:
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"profile": profile, "history": history_text})
    except Exception as e:
        return f"Error generating question: {str(e)}. Please check your API Key in .env file."

def transcribe_audio(audio_bytes, api_key=None):
    """Transcribes audio bytes to text using Gemini (fallback to SpeechRecognition if no key)."""
    
    # Try Gemini first if key is provided
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Gemini 2.5 Flash is good for audio
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            prompt = "Transcribe the following audio exactly as spoken. Do not add any other text."
            
            # Pass audio bytes directly
            response = model.generate_content([
                prompt,
                {"mime_type": "audio/webm", "data": audio_bytes}
            ])
            
            return response.text.strip()
        except Exception as e:
            print(f"Gemini transcription failed: {e}")
            # Fall through to legacy method
            
    # Legacy SpeechRecognition method (requires WAV/ffmpeg)
    r = sr.Recognizer()
    
    import io
    import tempfile
    from pydub import AudioSegment
    
    try:
        # Create a temp file for the input audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_input:
            tmp_input.write(audio_bytes)
            tmp_input_path = tmp_input.name

        # Convert to WAV using pydub
        try:
            audio = AudioSegment.from_file(tmp_input_path)
            wav_path = tmp_input_path.replace(".webm", ".wav")
            audio.export(wav_path, format="wav")
        except Exception as e:
            # Fallback: Try treating it as wav directly
            wav_path = tmp_input_path
            print(f"Warning: Audio conversion failed (ffmpeg likely missing): {e}")

        # Recognize
        with sr.AudioFile(wav_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            
        # Cleanup
        try:
            os.remove(tmp_input_path)
            if wav_path != tmp_input_path:
                os.remove(wav_path)
        except:
            pass

        return text
    except Exception as e:
        return f"Error transcribing audio: {str(e)}. (Note: ffmpeg is required for local processing, or provide a valid Gemini API Key)"

def evaluate_interview(profile, history, api_key, provider="OpenAI"):
    """Generates a final evaluation report."""
    llm = get_llm(api_key, provider)
    if not llm:
        return "Error: Invalid API Key"

    history_text = "\n".join([f"Question: {q}\nCandidate Answer: {a}" for q, a in history])

    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert hiring manager. Evaluate the following interview for a {profile} position.
        
        Interview Transcript:
        {history}
        
        Output the result strictly in valid JSON format with the following keys:
        1. "report_markdown": A detailed markdown report (Overall Impression, Strengths, Areas for Improvement, Rating 1-10, Hiring Recommendation).
        2. "recommendation": One of "Strong Hire", "Hire", "No Hire".
        3. "motivational_message": If recommendation is "No Hire", provide a short, encouraging 1-2 sentence motivational message for the candidate. Otherwise, leave empty string.
        
        Do not include markdown formatting (like ```json) around the output. Just the raw JSON string.
        """
    )
    
    try:
        chain = prompt | llm | StrOutputParser()
        result_str = chain.invoke({"profile": profile, "history": history_text})
        
        # Clean up potential markdown code blocks if model adds them
        result_str = result_str.replace("```json", "").replace("```", "").strip()
        
        import json
        return json.loads(result_str)
    except Exception as e:
        return {
            "report_markdown": f"Error generating evaluation: {str(e)}. Please check your API Key in .env file.",
            "recommendation": "Error",
            "motivational_message": ""
        }

def save_session(profile, history, evaluation):
    """Saves the interview session to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/interview_{profile.replace(' ', '_')}_{timestamp}.json"
    
    data = {
        "profile": profile,
        "timestamp": timestamp,
        "history": history,
        "evaluation": evaluation
    }
    
    os.makedirs("data", exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    
    return filename

def text_to_speech(text):
    """Converts text to speech using edge-tts (high quality neural voice)."""
    try:
        import asyncio
        import edge_tts
        import base64
        import tempfile
        
        # Voice: Indian English Female (Neerja) - High Quality
        VOICE = "en-IN-NeerjaNeural"
        
        async def _generate():
            communicate = edge_tts.Communicate(text, VOICE)
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                await communicate.save(tmp.name)
                return tmp.name

        # Run async function
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        mp3_path = loop.run_until_complete(_generate())
        
        # Read and encode
        with open(mp3_path, "rb") as f:
            audio_bytes = f.read()
            
        # Cleanup
        try:
            os.remove(mp3_path)
        except:
            pass
            
        b64 = base64.b64encode(audio_bytes).decode()
        return b64
    except Exception as e:
        print(f"TTS Error: {e}")
        return None
