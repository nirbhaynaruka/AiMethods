import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv # New: Import load_dotenv

load_dotenv() # New: Load environment variables from .env file

app = Flask(__name__)
# IMPORTANT: Configure CORS to only allow requests from your frontend domain.
# For local testing, you might use "http://localhost:8000" or similar.
# For production, set this to "https://aimethods.co"
CORS(app, resources={r"/generate-ai-advantage": {"origins": "https://aimethods.co"}}) # For local testing: "http://127.0.0.1:5000" or "http://localhost:5000"

# --- Gemini API Configuration ---
# Your API key MUST be stored as an environment variable for security!
# DO NOT hardcode your API key here. It is now loaded from .env for local dev.
try:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    # In a real app, you might want to log this and/or make the app fail fast.
    GEMINI_API_KEY = None # Ensure it's None if not set

# Initialize the generative model
model = genai.GenerativeModel('gemini-2.0-flash')

@app.route('/generate-ai-advantage', methods=['POST'])
def generate_ai_advantage():
    if not GEMINI_API_KEY:
        return jsonify({"error": "Server API key not configured."}), 500

    data = request.get_json()
    user_input = data.get('userInput')

    if not user_input:
        return jsonify({"error": "User input is required."}), 400

    # REVISED LLM PROMPT (from index.html) for backend consistency
    prompt = f"""As an expert in AI workflow optimization for businesses, analyze the following user input describing their role or a business challenge. Suggest brief, direct suggestions (3-5 concise paragraphs or bullet points) on how AiMethods (premium AI prompts and custom AI solutions) can help them, focusing on practical AI applications and benefits. Avoid markdown characters (*, #) in the output.

    User Input: "{user_input}"

    Suggestions:"""

    try:
        # Call Gemini API securely from the backend
        response = model.generate_content(prompt)
        ai_suggestion = response.text
        return jsonify({"suggestion": ai_suggestion})
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return jsonify({"error": "Failed to generate AI advantage. Please try again later."}), 500

@app.route('/')
def home():
    return "AI Methods Backend is running. Access /generate-ai-advantage via POST."

if __name__ == '__main__':
    # For local development:
    # Set your GEMINI_API_KEY environment variable before running.
    # To run: python app.py
    app.run(host='0.0.0.0', port=5000, debug=True)
    # In production, use a WSGI server like Gunicorn.
