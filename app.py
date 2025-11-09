from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import google.generativeai as genai
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

from models import db, User, Chat

# Load environment variables
load_dotenv()
app = Flask(__name__)

# Secret key for session/flash
app.secret_key=os.getenv("SECRET_KEY","AIzaSyAHrGQqoCCC5GZjvBNp_J38BepCdg1XfJg")

# Google Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction="""
        You are an AI psychologist.
        - Always reply in short and casual sentences.
        - Only give 1 sugeestion at one time
        - Friendly, supportive WhatsApp-like tone.
        - If user talks in Hinglish, reply in Hinglish.
        - Don’t answer in points.
        - No Urdu.
        - Be a little emotional like a psychologist friend.
    """
)

# Database (SQLite for dev, can switch to MySQL later)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:ajay1234@localhost:3306/mindmate_db"


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# yahan apna model banao
#class ChatHistory(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    user = db.Column(db.String(100))
#    bot = db.Column(db.String(100))

#  Yeh zaroori hai (context ke andar database tables create karna)
with app.app_context():
    db.create_all()

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- Routes ----------------
@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("index.html", user=current_user)
    return render_template("index.html", user=None)


@app.route("/register", methods=["POST"])
def register():
    

    fullname=request.form["fullname"]
    username = request.form["username"]
    email = request.form["email"]
    phone = request.form["phone"]
    dob = request.form["dob"]
    gender = request.form["gender"]
    password = request.form["password"]
    print(fullname, username, email, password)

    #user = User.query.filter_by(email=email).first()
    if User.query.filter_by(email=email).first():
        flash("Email already exists!")
        return redirect(url_for("index"))

    hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")
    new_user = User(fullname=fullname, username=username, email=email, phone=phone, dob=dob, gender=gender, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)  # direct login after register
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for("dashboard"))
    else:
        flash("Invalid email or password")
        return redirect(url_for("index"))
    
@app.route("/dashboard")
@login_required
def dashboard():
    # Pass current_user object to template
    return render_template("dashboard.html", user=current_user)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Get form data sent by JavaScript
        data = request.get_json()
        current_user.bio = data.get('bio')
        current_user.city = data.get('city')
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully!'})

    return render_template('profile.html', user=current_user)





@app.route("/chatbot")
@login_required
def chatbot():
    chats = Chat.query.filter_by(user_id=current_user.id).all()
    return render_template("chatbot.html", username=current_user.username, chats=chats)



@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message.strip():
            return jsonify({"error": "Message cannot be empty"}), 400

        # Send only user message (system_instruction is already bound to model)
        response = model.generate_content(user_message)

        bot_reply = getattr(response, "text", "No reply from AI")

        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)})




@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# with app.app_context():
#     db.create_all()
#     print(" Database created successfully!")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5501)


