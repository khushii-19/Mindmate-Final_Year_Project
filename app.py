from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ✅ Step 1: Add your Gemini API key here
genai.configure(api_key="AIzaSyCkBGQQEoTvuFVwLYQ7C1J5nEgw9yc32-4")

# ✅ Step 2: Define your system prompt (persona + rules)
SYSTEM_PROMPT = """
You are an AI physcologist. 
- Always reply in very short and casual sentences.  
- If giving therapies, give only two short suggestions at a time.  
- Always ask the user at least one follow-up question.  
- Keep the tone friendly and supportive 
-also if user talks in hinglish talk in hinglish and
- talk just like friend and give short replies only to make comfortable like whatsapp
-also dont give answers in points yr 
-dont talk in urdu only hinglish and english
-thoda emotionally ek pshycologist h tu ok.  
"""

# ✅ Step 3: Initialize model
model = genai.GenerativeModel("gemini-2.0-flash")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json["message"]

        # Combine system prompt + user message
        prompt = f"{SYSTEM_PROMPT}\nUser: {user_input}\nAI:"

        # Send message to Gemini
        response = model.generate_content(prompt)

        # Send back reply
        return jsonify({"reply": response.text})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"reply": "⚠️ Sorry, I had trouble responding. Please try again."})

if __name__ == "__main__":
    app.run(debug=True)
