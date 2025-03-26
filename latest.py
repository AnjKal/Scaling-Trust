import streamlit as st
import requests
import firebase_admin
import random
from firebase_admin import credentials, firestore

# Load Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Perspective API Key
PERSPECTIVE_API_KEY = "AIzaSyB113fKzZfa4iqpcs63wbHRRo1CGC5uWBA"
PERSPECTIVE_URL = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"

# Avatar generator (random avatars for users)
AVATAR_URLS = [
    "https://avatars.dicebear.com/api/bottts/",
    "https://avatars.dicebear.com/api/personas/",
    "https://avatars.dicebear.com/api/fun-emoji/"
]

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

def handle_toxicity(username, text, toxicity_score):
    """ Handles the post based on toxicity level and saves it. """
    avatar = random.choice(AVATAR_URLS) + username  # Generate avatar for user
    post_data = {
        "username": username,
        "avatar": avatar,
        "post": text,
        "toxicity_score": toxicity_score,
        "likes": 0,
        "comments": []
    }
    
    if toxicity_score > 6:
        return "🚫 **Post Blocked:** Contains excessive toxicity!", "red"
    elif toxicity_score < 4:
        db.collection("flagged_posts").add(post_data)
        return "⚠️ **Post Flagged:** This may need review.", "orange"
    else:
        db.collection("approved_posts").add(post_data)
        return "✅ **Post Approved & Saved to Firebase.**", "green"

# Streamlit UI
st.set_page_config(page_title="Toxicity Checker", layout="wide")
st.title("🛡️ AI-Powered Social Media Toxicity Checker")

# Sidebar - Settings
st.sidebar.title("⚙️ Settings")
st.sidebar.write("Adjust settings here if needed.")

# User Input Section
username = st.text_input("👤 Enter your username:", max_chars=15)
user_input = st.text_area("💬 Enter your post:", height=100)

if st.button("Analyze & Post"):
    if username.strip() and user_input.strip():
        with st.spinner("Analyzing toxicity..."):
            toxicity_score = analyze_toxicity(user_input)
            decision, color = handle_toxicity(username, user_input, toxicity_score)

        st.progress(toxicity_score / 10)
        st.markdown(f"**🔍 Toxicity Score:** `{toxicity_score:.2f}/10`")
        st.markdown(f"<p style='color:{color}; font-size: 20px; font-weight: bold;'>{decision}</p>", unsafe_allow_html=True)
    else:
        st.error("Please enter both a username and a post!")

# Display Posts Section
st.subheader("📢 Social Media Feed")

def display_posts(collection_name, title, color):
    st.markdown(f"### {title}")
    posts = db.collection(collection_name).stream()

    for post in posts:
        post_data = post.to_dict()
        col1, col2 = st.columns([1, 5])

        with col1:
            st.image(avatar, width=50)

        with col2:
            st.markdown(f"**{post_data['username']} **")
            st.write(post_data["post"])
            st.progress(post_data["toxicity_score"] / 10)
            st.write(f"**Toxicity Score:** `{post_data['toxicity_score']:.2f}/10`")
            
            # Like Button
            if st.button(f"👍 {post_data.get('likes', 0)} Likes", key=f"like_{post.id}"):
                db.collection(collection_name).document(post.id).update({"likes": post_data["likes"] + 1})

            # Comment Section
            comment = st.text_input(f"💬 Add a comment on {post.id}", key=f"comment_{post.id}")
            if st.button("Post Comment", key=f"post_comment_{post.id}"):
                if comment:
                    updated_comments = post_data["comments"]
                    updated_comments.append(f"{username}: {comment}")
                    db.collection(collection_name).document(post.id).update({"comments": updated_comments})

            # Show existing comments
            if post_data["comments"]:
                st.markdown("**Comments:**")
                for cmt in post_data["comments"]:
                    st.markdown(f"- {cmt}")

# Display Approved and Flagged Posts
display_posts("approved_posts", "✅ Approved Posts", "green")
display_posts("flagged_posts", "⚠️ Flagged Posts", "orange")
