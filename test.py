import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Perspective API Key
PERSPECTIVE_API_KEY = "AIzaSyB113fKzZfa4iqpcs63wbHRRo1CGC5uWBA"
PERSPECTIVE_URL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"

def analyze_toxicity(text):
    """ Sends text to Perspective API and returns toxicity score. """
    payload = {
        "comment": {"text": text},
        "languages": ["en"],
        "requestedAttributes": {"TOXICITY": {}}
    }
    response = requests.post(f"{PERSPECTIVE_URL}?key={PERSPECTIVE_API_KEY}", json=payload)
    data = response.json()
    return data["attributeScores"]["TOXICITY"]["summaryScore"]["value"] * 10  # Scale 0-10

def handle_toxicity(text, toxicity_score):
    """ Handles the post based on toxicity level. """
    if toxicity_score > 6:
        return "🚫 **Post Blocked:** Contains excessive toxicity!", "red"
    elif toxicity_score > 4 and toxicity_score <6:
        db.collection("flagged_posts").add({"post": text, "toxicity_score": toxicity_score})
        return "⚠️ **Post Flagged:** This may need review.", "orange"
    else:
        db.collection("approved_posts").add({"post": text, "toxicity_score": toxicity_score})
        return "✅ **Post Approved & Saved to Firebase.**", "green"

# Streamlit UI
st.set_page_config(page_title="Toxicity Checker", layout="wide")
st.markdown("""
    <style>
        .stTextArea textarea {font-size: 18px;}
        .stButton button {background-color: #4CAF50; color: white; font-size: 18px;}
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("⚙️ Settings")
st.sidebar.write("Adjust settings here if needed.")

st.title("🛡️ AI-Powered Social Media Toxicity Checker")
st.write("Enter a post below and analyze its toxicity in real-time.")

user_input = st.text_area("💬 Enter your post:", height=150)
if st.button("Analyze Post"):
    if user_input.strip():
        with st.spinner("Analyzing toxicity..."):
            toxicity_score = analyze_toxicity(user_input)
            decision, color = handle_toxicity(user_input, toxicity_score)
        
        st.progress(toxicity_score / 10)
        st.markdown(f"**🔍 Toxicity Score:** `{toxicity_score:.2f}/10`")
        st.markdown(f"<p style='color:{color}; font-size: 20px; font-weight: bold;'>{decision}</p>", unsafe_allow_html=True)
    else:
        st.error("Please enter a post to analyze.")
