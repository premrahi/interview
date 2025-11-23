# AI Virtual Interviewer - Project Documentation

## 1. Project Overview
The **AI Virtual Interviewer** is an intelligent, interactive web application designed to simulate real-world job interviews. It uses advanced Generative AI to conduct voice-based interviews, evaluate candidate responses, and provide detailed feedback. The system is designed to help users practice and improve their interview skills in a stress-free environment.

## 2. Technology Stack
The project is built using a modern Python-based stack:

*   **Frontend & UI**: [Streamlit](https://streamlit.io/) - Used for building the interactive web interface, managing session state, and handling real-time updates.
*   **Large Language Model (LLM)**: [Google Gemini (via LangChain)](https://python.langchain.com/) - Powers the intelligence of the interviewer. It generates context-aware questions and evaluates answers.
*   **Speech-to-Text (STT)**: [Google Gemini API / SpeechRecognition](https://pypi.org/project/SpeechRecognition/) - Converts the user's spoken audio into text for the AI to process.
*   **Text-to-Speech (TTS)**: [edge-tts](https://github.com/rany2/edge-tts) - Provides high-quality, neural voice output (specifically an Indian English accent) to make the AI speak.
*   **Audio Processing**: [Pydub](https://pypi.org/project/pydub/) - Handles audio file manipulation and format conversion.
*   **Environment Management**: [python-dotenv](https://pypi.org/project/python-dotenv/) - Securely manages API keys and configuration.

## 3. Key Features
*   **Personalized Login**: Users enter their name and select a specific job role (e.g., Data Scientist, Web Developer).
*   **Voice Interaction**: The interview is entirely voice-based. The AI speaks the questions, and the user records their answers.
*   **Realistic AI Persona**: The AI uses a natural-sounding Indian English voice and greets the user by name.
*   **Dynamic Questioning**: Questions are generated dynamically based on the chosen role and the context of previous answers.
*   **Real-time Feedback**: Users can hear their own recorded responses before submitting.
*   **Motivational Support**: If the final result is "No Hire", the AI provides an encouraging motivational message.
*   **Comprehensive Evaluation**: At the end, a detailed report is generated covering strengths, weaknesses, and a hiring recommendation.

## 4. How It Works (Workflow)

### Step 1: Initialization
- The app launches and loads environment variables (API Keys).
- It initializes the session state to track the interview progress, chat history, and user details.

### Step 2: Login & Setup
- The user is presented with a login screen.
- They input their **Name** and select a **Job Profile**.
- Upon clicking "Start Interview", the app transitions to the interview interface.

### Step 3: The Interview Loop
1.  **Greeting & First Question**: The AI generates a time-aware greeting (e.g., "Good Morning") and asks the first question: *"Tell me about yourself."*
2.  **TTS Generation**: The text is sent to the `edge-tts` engine, which generates an audio file. This audio is automatically played in the browser.
3.  **User Response**:
    - The user clicks "Start Recording" and speaks their answer.
    - The audio is captured and sent to the backend.
    - The system transcribes the audio to text using the Gemini API.
4.  **Submission**: The user reviews their answer (optional playback) and clicks "Submit".
5.  **Next Question**:
    - The answer is saved to the chat history.
    - The history is sent to the Gemini LLM to generate the *next* relevant question.
    - This cycle repeats for 7 questions.

### Step 4: Completion & Evaluation
- After the 7th question, the interview concludes.
- **Evaluation**: The entire interview transcript is sent to the LLM with a prompt to act as a "Hiring Manager".
- **Report Generation**: The LLM returns a structured JSON containing:
    - A Markdown report (Strengths, Weaknesses, Rating).
    - A Hiring Recommendation (Hire/No Hire).
    - A Motivational Message (if applicable).
- **Display**: The user sees balloons (animation), reads the report, and sees the full transcript of the conversation.
- **Motivational TTS**: If the user wasn't hired, the AI speaks the motivational message to encourage them.

## 5. Project Structure
*   `app.py`: The main entry point. Handles the UI, user input, and application flow.
*   `utils.py`: Contains helper functions for:
    - `get_ai_question()`: Calling the LLM for questions.
    - `transcribe_audio()`: Converting speech to text.
    - `text_to_speech()`: Generating audio from text.
    - `evaluate_interview()`: Generating the final report.
*   `data/`: Directory where interview sessions and reports are saved as JSON files.
*   `.env`: Stores the `GOOGLE_API_KEY`.
*   `requirements.txt`: Lists all Python dependencies.

## 6. Future Enhancements
- **Video Analysis**: Analyze facial expressions and body language via the camera feed.
- **Resume Parsing**: Upload a resume to tailor questions even further.
- **Multiple Languages**: Support for interviews in languages other than English.
