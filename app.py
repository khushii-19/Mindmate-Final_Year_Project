from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are an AI physcologist. 
- Always reply in very short and casual sentences.    
- Keep the tone friendly and supportive 
-also if user talks in hinglish talk in hinglish and
- talk just like friend and give short replies only to make comfortable like whatsapp
-also dont give answers in points yr 
-dont talk in urdu only hinglish and english
-thoda emotionally ek pshycologist h tu ok.  
"""


model = genai.GenerativeModel("gemini-2.0-flash")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json["message"]

        
        prompt = f"{SYSTEM_PROMPT}\nUser: {user_input}\nAI:"

        response = model.generate_content(prompt)

        return jsonify({"reply": response.text})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"reply": " Sorry, I had trouble responding. Please try again."})

if __name__ == "__main__":
    app.run(debug=True)
