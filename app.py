%%writefile app.py
import streamlit as st
from pymongo import MongoClient
import pandas as pd
from groq import Groq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Healthcare AI", page_icon="🧬", layout="wide")

# ---------------- SECRETS ----------------
MONGO_URL = st.secrets["MONGO_URL"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# ---------------- DATABASE ----------------
client = MongoClient(MONGO_URL)
db = client["healthcare_db"]

chat_history = db["chat_history"]
fitness = db["fitness"]
reminders = db["reminders"]
goals = db["goals"]
medical_history = db["medical_history"]

# ---------------- AI ----------------
client_ai = Groq(api_key=GROQ_API_KEY)

def ai_chatbot(text):
    response = client_ai.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a healthcare assistant."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

# ---------------- UI DESIGN ----------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #f6d365, #fda085, #a1c4fd);
}
h1 {
    text-align:center;
    color:#2c3e50;
}
.stButton>button {
    background-color: #ff7e5f;
    color: white;
    border-radius: 10px;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ff9a9e, #fad0c4);
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {"Chat 1": []}

# ---------------- DATA ----------------
ayurvedic_data = {
    "cold": ["Tulsi", "Ginger Tea"],
    "stress": ["Ashwagandha"],
    "immunity": ["Turmeric", "Amla"]
}

diet_data = {
    "weight loss": {"Breakfast": "Oats", "Lunch": "Roti + Dal", "Dinner": "Soup"},
    "diabetes": {"Breakfast": "Brown Bread", "Lunch": "Vegetables", "Dinner": "Salad"}
}

doctor_data = {
    "fever": "General Physician",
    "diabetes": "Endocrinologist",
    "skin": "Dermatologist"
}

# ---------------- SIDEBAR ----------------
st.sidebar.title("💬 Chats")

if st.sidebar.button("➕ New Chat"):
    new_id = f"Chat {len(st.session_state.chat_sessions)+1}"
    st.session_state.chat_sessions[new_id] = []
    st.session_state.current_chat = new_id
    st.rerun()

st.sidebar.markdown("### Your Chats")

for i, chat in enumerate(st.session_state.chat_sessions):
    if st.sidebar.button(chat, key=f"chat_{i}"):
        st.session_state.current_chat = chat
        st.rerun()

st.sidebar.markdown("---")

option = st.sidebar.selectbox(
    "⚙️ Features",
    ["Chatbot","Medication","Fitness","Dashboard","Report","Goals","Medical History",
     "Upload Data","Ayurvedic","Diet","Doctor"]
)

# ---------------- TITLE ----------------
st.markdown("<h1>🧬 Smart Healthcare AI</h1>", unsafe_allow_html=True)

# ---------------- CHATBOT ----------------
if option == "Chatbot":
    chat_id = st.session_state.current_chat
    messages = st.session_state.chat_sessions.get(chat_id, [])

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask health question...")

    if user_input:
        messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        response = ai_chatbot(user_input)

        messages.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.write(response)

        st.session_state.chat_sessions[chat_id] = messages

        chat_history.insert_one({
            "chat": chat_id,
            "user": user_input,
            "bot": response
        })

# ---------------- MEDICATION ----------------
elif option == "Medication":
    med = st.text_input("Medicine")
    if st.button("Save"):
        reminders.insert_one({"medicine": med})
        st.success("Saved!")

# ---------------- FITNESS ----------------
elif option == "Fitness":
    steps = st.number_input("Steps", 0)
    cal = st.number_input("Calories", 0)

    if st.button("Save"):
        fitness.insert_one({"steps": steps, "calories": cal})
        st.success("Saved!")

# ---------------- DASHBOARD ----------------
elif option == "Dashboard":
    data = list(fitness.find())
    if data:
        df = pd.DataFrame(data)
        col1, col2 = st.columns(2)
        col1.metric("Steps", df["steps"].sum())
        col2.metric("Avg", round(df["steps"].mean(),2))
        st.line_chart(df[["steps","calories"]])

# ---------------- REPORT ----------------
elif option == "Report":
    data = list(fitness.find())
    if data:
        df = pd.DataFrame(data)
        avg = df["steps"].mean()

        if avg < 3000:
            st.warning("Low Activity")
        elif avg < 7000:
            st.info("Moderate")
        else:
            st.success("Excellent")

# ---------------- GOALS ----------------
elif option == "Goals":
    goal = st.number_input("Set Goal", 0)
    if st.button("Save"):
        goals.insert_one({"goal": goal})
        st.success("Saved!")

# ---------------- MEDICAL HISTORY ----------------
elif option == "Medical History":
    name = st.text_input("Name")
    disease = st.text_input("Disease")
    ins = st.text_input("Insurance")

    if st.button("Save"):
        medical_history.insert_one({"name":name,"disease":disease,"insurance":ins})
        st.success("Saved!")

# ---------------- UPLOAD ----------------
elif option == "Upload Data":
    file = st.file_uploader("Upload JSON/CSV", type=["json","csv"])
    if file:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
            st.write(df)

# ---------------- AYURVEDIC ----------------
elif option == "Ayurvedic":
    sym = st.text_input("Enter problem")
    if sym in ayurvedic_data:
        for r in ayurvedic_data[sym]:
            st.write("🌿", r)

# ---------------- DIET ----------------
elif option == "Diet":
    goal = st.text_input("Goal")
    if goal in diet_data:
        d = diet_data[goal]
        st.write("Breakfast:", d["Breakfast"])
        st.write("Lunch:", d["Lunch"])
        st.write("Dinner:", d["Dinner"])

# ---------------- DOCTOR ----------------
elif option == "Doctor":
    sym = st.text_input("Symptom")
    if sym in doctor_data:
        st.write("Doctor:", doctor_data[sym])
