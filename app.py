import streamlit as st
import os
from datetime import datetime
from utils import get_ai_question, transcribe_audio, evaluate_interview, save_session, text_to_speech
from streamlit_mic_recorder import mic_recorder
from dotenv import load_dotenv

load_dotenv(override=True)

# Debug API Key (Masked)
key = os.getenv("GOOGLE_API_KEY")
if key:
    print(f"DEBUG: API Key loaded: {key[:5]}...{key[-5:]}")
else:
    print("DEBUG: API Key NOT found in environment")

# Page Config
st.set_page_config(page_title="AI Virtual Interviewer", layout="wide", page_icon="🎙️")

# Initialize Session State
if 'interview_active' not in st.session_state:
    st.session_state.interview_active = False
if 'candidate_name' not in st.session_state:
    st.session_state.candidate_name = None
if 'job_profile' not in st.session_state:
    st.session_state.job_profile = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "evaluation" not in st.session_state:
    st.session_state.evaluation = None

# --- LOGIN PAGE ---
if not st.session_state.interview_active:
    st.title("🤖 AI Virtual Interviewer")
    st.markdown("### Login to Start Your Interview")
    
    with st.form("login_form"):
        name = st.text_input("Enter your Name")
        role = st.selectbox(
            "Select Job Profile",
            ["Software Engineer", "Data Scientist", "Product Manager", "Marketing Specialist", "HR Manager", 
             "Web Developer", "Quality Analyst", "Data Engineer", "Data Analyst"]
        )
        submitted = st.form_submit_button("Start Interview")
        
        if submitted:
            if name:
                st.session_state.candidate_name = name
                st.session_state.job_profile = role
                st.session_state.interview_active = True
                st.session_state.chat_history = []
                st.session_state.question_count = 0
                st.session_state.evaluation = None
                
                # Determine greeting
                hour = datetime.now().hour
                if hour < 12:
                    greeting = "Good Morning"
                elif hour < 18:
                    greeting = "Good Afternoon"
                else:
                    greeting = "Good Evening"
                
                # First question
                first_q_text = "Tell me about yourself."
                full_display_text = f"{greeting} {name}. {first_q_text}"
                
                st.session_state.current_question = full_display_text
                
                # Generate Audio with Greeting (Restored)
                audio_b64 = text_to_speech(full_display_text)
                st.session_state.audio_autoplay = audio_b64
                
                st.rerun()
            else:
                st.error("Please enter your name.")
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🎯 Role Specific")
        st.write("Questions tailored to your selected job profile.")
    with c2:
        st.markdown("### 🗣️ Voice Interaction")
        st.write("Speak naturally, just like a real interview.")
    with c3:
        st.markdown("### 📊 Detailed Feedback")
        st.write("Get scored on content, clarity, and confidence.")

# --- INTERVIEW PAGE ---
else:
    # Sidebar (Only visible after login)
    with st.sidebar:
        try:
            st.image("assets/logo.jpg", width=150)
        except:
            pass
        st.title("Interview Settings")
        
        # Dark Mode Toggle
        dark_mode = st.toggle("🌙 Dark Mode", value=True)
        
        st.info(f"Candidate: **{st.session_state.candidate_name}**")
        st.info(f"Role: **{st.session_state.job_profile}**")
        
        st.divider()
        st.markdown("### 📹 Webcam Feed")
        # Camera input acts as a mirror/feed
        st.camera_input("Webcam", label_visibility="hidden")
        
        if st.button("End Interview", type="primary"):
            st.session_state.interview_active = False
            st.rerun()

    # Dynamic CSS based on Dark Mode
    if dark_mode:
        # Dark Theme Colors
        bg_gradient = "#000000" # Pitch Black
        sidebar_bg = "#121212" # Very dark gray
        text_color = "#ffffff"
        card_bg = "#1e1e1e"
        user_msg_bg = "#1e3a8a" 
        user_border = "#3b82f6"
        assistant_msg_bg = "#2d2d2d"
        assistant_border = "#a855f7"
        header_color = "#ffffff"
        shadow = "rgba(255,255,255,0.05)"
    else:
        # Light Theme Colors
        bg_gradient = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
        sidebar_bg = "#ffffff"
        text_color = "#1f2937"
        card_bg = "#ffffff"
        user_msg_bg = "#eff6ff"
        user_border = "#3b82f6"
        assistant_msg_bg = "#f3f4f6"
        assistant_border = "#a855f7"
        header_color = "#111827"
        shadow = "rgba(0,0,0,0.1)"

    st.markdown(f"""
    <style>
    .stApp {{
        background: {bg_gradient};
        color: {text_color};
    }}
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        border-right: 1px solid rgba(255,255,255,0.1);
    }}
    .custom-card {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px {shadow};
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .user-msg {{
        background-color: {user_msg_bg};
        padding: 15px;
        border-radius: 15px 15px 0 15px;
        margin: 10px 0;
        border-left: 4px solid {user_border};
        color: {text_color};
    }}
    .assistant-msg {{
        background-color: {assistant_msg_bg};
        padding: 15px;
        border-radius: 15px 15px 15px 0;
        margin: 10px 0;
        border-left: 4px solid {assistant_border};
        color: {text_color};
    }}
    h1, h2, h3 {{
        color: {header_color} !important;
        font-family: 'Inter', sans-serif;
    }}
    .stButton>button {{
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    /* Hide Camera Input Button to make it look more like a feed */
    button[kind="primaryFormSubmit"] {{
        display: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Main Interface
    st.title("🎙️ AI Virtual Interviewer")
    st.markdown("### Master your interview skills with real-time AI feedback")

    # Auto-play Audio if available
    if 'audio_autoplay' in st.session_state and st.session_state.audio_autoplay:
        b64 = st.session_state.audio_autoplay
        md = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
        st.session_state.audio_autoplay = None # Clear after playing

    # NOTE: Chat History hidden during interview as per request
    # It will be shown at the end with the report

    # Current Question Display
    if st.session_state.current_question:
        # Hidden: Question count indication and progress bar
        # st.progress((st.session_state.question_count + 1) / 7)
        
        st.markdown(f"""
        <div class="custom-card" style="border-left: 5px solid #a855f7;">
            <p style="font-size: 1.2rem;">{st.session_state.current_question}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Repeat Question Button
        if st.button("🔊 Repeat Question"):
            audio_b64 = text_to_speech(st.session_state.current_question)
            st.session_state.audio_autoplay = audio_b64
            st.rerun()

    # Audio Recording Section
    st.markdown("### 🎤 Record your answer")
    
    # Create a container for the recorder to keep it stable
    recorder_container = st.container()
    
    with recorder_container:
        audio = mic_recorder(
            start_prompt="Start Recording",
            stop_prompt="Stop Recording",
            just_once=False,
            use_container_width=False,
            format="webm",
            key=f"recorder_{st.session_state.question_count}" 
        )

    if audio:
        # Playback user audio
        st.audio(audio['bytes'])
        
        # Process the audio
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if st.button("Submit Answer", type="primary"):
            with st.spinner("Transcribing audio..."):
                text = transcribe_audio(audio['bytes'], api_key=api_key)
            
            st.success("Response recorded!")
            st.markdown(f"**You said:** _{text}_")
            
            # Save to history
            st.session_state.chat_history.append((st.session_state.current_question, text))
            st.session_state.question_count += 1
            
            # Check if interview is done
            if st.session_state.question_count >= 7:
                st.success("Interview Completed! Generating Report...")
                st.balloons() # Animation
                with st.spinner("Analyzing your responses..."):
                    evaluation_data = evaluate_interview(
                        st.session_state.job_profile, 
                        st.session_state.chat_history, 
                        api_key, 
                        "Gemini"
                    )
                    st.session_state.evaluation = evaluation_data
                    
                    # Save session (extract markdown for compatibility or save whole dict)
                    # We'll save the whole dict now
                    save_session(st.session_state.job_profile, st.session_state.chat_history, evaluation_data)
                    
                    # Check for Motivational Message
                    if evaluation_data.get("recommendation") == "No Hire" and evaluation_data.get("motivational_message"):
                        msg = evaluation_data["motivational_message"]
                        audio_b64 = text_to_speech(msg)
                        st.session_state.audio_autoplay = audio_b64
                    
                    st.session_state.current_question = None
                    st.rerun()
            else:
                # Generate next question
                with st.spinner("Generating next question..."):
                    q = get_ai_question(st.session_state.job_profile, st.session_state.chat_history, api_key, "Gemini")
                    st.session_state.current_question = q
                    
                    # Generate Audio for next question
                    audio_b64 = text_to_speech(q)
                    st.session_state.audio_autoplay = audio_b64
                    
                    st.rerun()

    # Display Evaluation Report & History
    if st.session_state.evaluation:
        st.balloons() # Animation on report load
        st.markdown("""
        <div class="custom-card">
            <h2>📊 Interview Evaluation Report</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Handle evaluation display (it's now a dict)
        if isinstance(st.session_state.evaluation, dict):
            st.markdown(st.session_state.evaluation.get("report_markdown", "Error loading report."))
        else:
            st.markdown(st.session_state.evaluation) # Fallback for old sessions
        
        st.divider()
        st.subheader("📝 Interview Transcript")
        for q, a in st.session_state.chat_history:
            st.markdown(f"""
            <div class="assistant-msg">
                <strong>🤖 AI:</strong><br>{q}
            </div>
            <div class="user-msg">
                <strong>👤 You:</strong><br>{a}
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("Start New Interview"):
            st.session_state.interview_active = False
            st.rerun()
