import joblib
import streamlit as st
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai

GOOGLE_GENAI_API_KEY = "AIzaSyAMB5wU-VRF-ynl-UIqGMrd0BJnIhtm1tM"  # Replace with your API Key
genai.configure(api_key=GOOGLE_GENAI_API_KEY)
# ✅ Load Firebase
# if not firebase_admin._apps:
#     cred = credentials.Certificate("firebase_key.json")
#     firebase_admin.initialize_app(cred)
# db = firestore.client()

# ✅ Load the trained model once
model_path = 'cyberbullying_model.pkl'
pipe = joblib.load(model_path)

# ✅ Hardcoded Perspective API Key
PERSPECTIVE_API_KEY = "AIzaSyB113fKzZfa4iqpcs63wbHRRo1CGC5uWBA"
PERSPECTIVE_URL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"

# ✅ Function to analyze toxicity
def analyze_toxicity(text):
    payload = {
        "comment": {"text": text},
        "languages": ["en"],
        "requestedAttributes": {"TOXICITY": {}}
    }
    response = requests.post(f"{PERSPECTIVE_URL}?key={PERSPECTIVE_API_KEY}", json=payload)
    data = response.json()
    return data["attributeScores"]["TOXICITY"]["summaryScore"]["value"] * 10

# ✅ Function to classify the type of cyberbullying
def classify_cyberbullying(text):
    prediction = pipe.predict([text])
    return prediction[0]

def rewrite_post(text):
    """ Uses Google's GenAI (Gemini API) to rewrite a flagged post in a neutral/positive tone. """
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
    The following text may contain offensive or inappropriate content:

    "{text}"

    Please rewrite it in a more positive, neutral, and respectful tone while maintaining its original intent.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# ✅ Function to handle the post
def handle_toxicity(text, toxicity_score, cyberbullying_type):
    if toxicity_score > 6:
        rewritten_text = rewrite_post(text)
        return f"🚫 **Post Blocked:** Contains excessive toxicity! ({cyberbullying_type}) \n**New Version:** {rewritten_text}", "red"
    elif 4 < toxicity_score <= 6:
        # db.collection("flagged_posts").add({
        #     "post": text,
        #     "toxicity_score": toxicity_score,
        #     "cyberbullying_type": cyberbullying_type
        # })
        rewritten_text = rewrite_post(text)
        return f"⚠️ **Post Flagged:** This may need review. ({cyberbullying_type}) \n**New Version:** {rewritten_text}", "orange"
    else:
        # db.collection("approved_posts").add({
        #     "post": text,
        #     "toxicity_score": toxicity_score,
        #     "cyberbullying_type": cyberbullying_type
        # })
        return f"✅ **Post Approved & Saved to Firebase.** ({cyberbullying_type})", "green"

# ✅ Streamlit UI
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
            cyberbullying_type = classify_cyberbullying(user_input)
            decision, color = handle_toxicity(user_input, toxicity_score, cyberbullying_type)

        st.progress(toxicity_score / 10)
        st.markdown(f"**🔍 Toxicity Score:** `{toxicity_score:.2f}/10`")
        st.markdown(f"**💡 Cyberbullying Type:** `{cyberbullying_type}`")
        st.markdown(f"<p style='color:{color}; font-size: 20px; font-weight: bold;'>{decision}</p>", unsafe_allow_html=True)
    else:
        st.error("Please enter a post to analyze.")
