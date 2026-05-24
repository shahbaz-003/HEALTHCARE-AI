import streamlit as st
from pymongo import MongoClient
import pandas as pd
from groq import Groq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Healthcare AI", page_icon="🧬", layout="wide")

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

# ---------------- SECRETS ----------------

MONGO_URL = st.secrets["MONGO_URL"]

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# ---------------- DATABASE ----------------

client = MongoClient(MONGO_URL)

db = client["healthcare_db"]

# ---------------- GROQ ----------------

client_ai = Groq(api_key=GROQ_API_KEY)
# ---------------- DATABASE ----------------
db = client["healthcare_db"]

chat_history = db["chat_history"]
fitness = db["fitness"]
reminders = db["reminders"]
goals = db["goals"]
medical_history = db["medical_history"]
ayurvedic_chat_history = db["ayurvedic_chat_history"]

chat_sessions_db = db["chat_sessions"]
# =====================================================
# 💬 LOAD CHAT SESSIONS FROM MONGODB
# =====================================================

if "chat_sessions" not in st.session_state:

    st.session_state.chat_sessions = {}

    # -------- LOAD NORMAL CHATS --------
chats = chat_history.find()

for chat in chats:

    # -------- SKIP INVALID DATA --------
    if "user" not in chat or "bot" not in chat:

        continue

    chat_name = chat.get(
        "chat",
        "Chat 1"
    )

    if chat_name not in st.session_state.chat_sessions:

        st.session_state.chat_sessions[
            chat_name
        ] = []

    # -------- USER MESSAGE --------
    st.session_state.chat_sessions[
        chat_name
    ].append({

        "role": "user",

        "content": chat.get("user", "")
    })

    # -------- BOT MESSAGE --------
    st.session_state.chat_sessions[
        chat_name
    ].append({

        "role": "assistant",

        "content": chat.get("bot", "")
    })

    # -------- LOAD AYURVEDIC CHATS --------
ayurvedic_chats = ayurvedic_chat_history.find()

for chat in ayurvedic_chats:

    # -------- SKIP INVALID DATA --------
    if "user" not in chat or "bot" not in chat:

        continue

    chat_name = chat.get(
        "chat",
        "Ayurvedic Chat"
    )

    if chat_name not in st.session_state.chat_sessions:

        st.session_state.chat_sessions[
            chat_name
        ] = []

    # -------- USER MESSAGE --------
    st.session_state.chat_sessions[
        chat_name
    ].append({

        "role": "user",

        "content": chat.get("user", "")
    })

    # -------- BOT MESSAGE --------
    st.session_state.chat_sessions[
        chat_name
    ].append({

        "role": "assistant",

        "content": chat.get("bot", "")
    })
# =====================================================
# 💬 CURRENT CHAT
# =====================================================

if "current_chat" not in st.session_state:

    st.session_state.current_chat = "Chat 1"

# -------- CREATE DEFAULT CHAT --------
if len(st.session_state.chat_sessions) == 0:

    st.session_state.chat_sessions[
        "Chat 1"
    ] = []


# ---------------- AI ----------------
def ai_chatbot(text):
    response = client_ai.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a healthcare assistant."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

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

# =====================================================
# 💬 CHAT SESSION STATE
# =====================================================

if "chat_sessions" not in st.session_state:

    st.session_state.chat_sessions = {}

if "current_chat" not in st.session_state:

    st.session_state.current_chat = "Chat 1"

# -------- DEFAULT CHAT --------
if len(st.session_state.chat_sessions) == 0:

    st.session_state.chat_sessions["Chat 1"] = []
# ---------------- SIDEBAR ----------------
st.sidebar.title("💬 Chats")

# ➕ New Chat
if st.sidebar.button("➕ New Chat"):
    new_id = f"Chat {len(st.session_state.chat_sessions)+1}"
    st.session_state.chat_sessions[new_id] = []
    st.session_state.current_chat = new_id
    st.rerun()

st.sidebar.markdown("### Your Chats")

# FIXED CHAT SWITCHING
for i, chat in enumerate(st.session_state.chat_sessions):
    if st.sidebar.button(chat, key=f"chat_{i}"):
        st.session_state.current_chat = chat
        st.rerun()

st.sidebar.markdown("---")

option = st.sidebar.selectbox(
    "Choose Option",
    [
        "Chatbot",
        "Medication",
        "Fitness",
        "Dashboard",
        "Report",
        "Goals",
        "Medical History",
        "Ayurvedic",
        "Diet",
        "Doctor Recommendation",
        "Upload Data"
    ]
)

# =====================================================
# 💬 SIDEBAR CHAT HISTORY
# =====================================================

st.sidebar.markdown("---")

st.sidebar.subheader("💬 Chat History")

# -------- NEW CHAT BUTTON --------
if st.sidebar.button(
    "➕ New Chat",
    key="new_chat_button"
):

    new_chat = f"Chat {len(st.session_state.chat_sessions)+1}"

    st.session_state.chat_sessions[
        new_chat
    ] = []

    st.session_state.current_chat = new_chat

# -------- SHOW ALL CHATS --------
for chat in st.session_state.chat_sessions.keys():

    # CURRENT CHAT HIGHLIGHT
    if chat == st.session_state.current_chat:

        st.sidebar.markdown(
            f"🟢 **{chat}**"
        )

    # CHAT BUTTON
    if st.sidebar.button(
        chat,
        key=f"chat_{chat}"
    ):

        st.session_state.current_chat = chat
# =====================================================
# 🧬 APP TITLE
# =====================================================

st.markdown(
    """
    <h1 style='
    text-align: center;
    color: #14b8a6;
    font-size: 50px;
    '>
    🧬 Smart Healthcare AI
    </h1>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 🤖 NORMAL AI CHATBOT FUNCTION
# =========================================================

def ai_chatbot(user_query):

    response = client_ai.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[

            {
                "role": "system",

                "content": """

                You are a professional AI Healthcare Assistant.

                Help users with:
                - General health questions
                - Symptoms
                - Fitness advice
                - Diet suggestions
                - Medicine guidance
                - Healthy lifestyle tips

                Give short, clear, and safe answers.

                Always recommend consulting doctors for serious conditions.

                """
            },

            {
                "role": "user",
                "content": user_query
            }
        ]
    )

    return response.choices[0].message.content


# =========================================================
# 🌿 AYURVEDIC AI CHATBOT FUNCTION
# =========================================================

def ayurvedic_ai_chatbot(user_query):

    response = client_ai.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[

            {
                "role": "system",

                "content": """

                You are an expert Ayurvedic healthcare assistant.

                Help users with:
                - Ayurvedic medicines
                - Herbal remedies
                - Home remedies
                - Yoga suggestions
                - Natural healing
                - Indian diet recommendations
                - Wellness tips

                Answer professionally and safely.

                Do not replace real doctors.

                """
            },

            {
                "role": "user",
                "content": user_query
            }
        ]
    )

    return response.choices[0].message.content


# =========================================================
# 🤖 CHATBOT SECTION
# =========================================================

# =========================================================
# 🤖 CHATBOT SECTION
# =========================================================

if option == "Chatbot":

    st.header("🤖 AI Healthcare Assistant")

    # -------- CURRENT CHAT --------
    chat_id = st.session_state.current_chat

    # -------- GET CHAT MESSAGES --------
    messages = st.session_state.chat_sessions.get(
        chat_id,
        []
    )

    # -------- DISPLAY OLD CHATS --------
    for msg in messages:

        with st.chat_message(msg["role"]):

            st.write(msg["content"])

    # -------- USER INPUT --------
    user_input = st.chat_input(
        "Ask health question..."
    )

    # -------- PROCESS USER INPUT --------
    if user_input:

        # ===== SAVE USER MESSAGE =====
        messages.append({
            "role": "user",
            "content": user_input
        })

        # ===== DISPLAY USER MESSAGE =====
        with st.chat_message("user"):

            st.write(user_input)

        # ===== AI RESPONSE =====
        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    response = ai_chatbot(
                        user_input
                    )

                    st.write(response)

                except Exception as e:

                    response = f"Error: {e}"

                    st.error(response)

        # ===== SAVE AI RESPONSE =====
        messages.append({
            "role": "assistant",
            "content": response
        })

        # ===== SAVE CHAT SESSION =====
        st.session_state.chat_sessions[
            chat_id
        ] = messages

        # ===== SAVE TO MONGODB =====
        chat_history.insert_one({

            "chat": chat_id,

            "user": user_input,

            "bot": response
        })
# =========================================================
# 🌿 AYURVEDIC CHATBOT SECTION
# =========================================================

elif option == "Ayurvedic":

    st.header("🌿 Ayurvedic AI Assistant")

    st.write("""
    Ask about:
    - Ayurvedic medicines
    - Herbs
    - Yoga
    - Home remedies
    - Natural healing
    """)

    # -------- CHAT HISTORY --------
    ayurvedic_messages = st.session_state.get(
        "ayurvedic_messages",
        []
    )

    # -------- DISPLAY CHAT --------
    for msg in ayurvedic_messages:

        with st.chat_message(msg["role"]):

            st.write(msg["content"])

    # -------- USER INPUT --------
    user_input = st.chat_input(
        "Ask Ayurvedic Question..."
    )

    # -------- PROCESS --------
    if user_input:

        # USER MESSAGE
        ayurvedic_messages.append({

            "role": "user",

            "content": user_input
        })

        with st.chat_message("user"):

            st.write(user_input)

        # AI RESPONSE
        with st.chat_message("assistant"):

            with st.spinner(
                "Generating Ayurvedic Advice..."
            ):

                try:

                    response = ayurvedic_ai_chatbot(
                        user_input
                    )

                    st.write(response)

                except Exception as e:

                    response = f"Error: {e}"

                    st.error(response)

        # SAVE RESPONSE
        ayurvedic_messages.append({

            "role": "assistant",

            "content": response
        })

        st.session_state[
            "ayurvedic_messages"
        ] = ayurvedic_messages

    st.markdown("---")

    st.warning("""
    ⚠️ Ayurvedic advice is for educational purposes only.

    Consult doctors for serious conditions.
    """)

# ---------------- MEDICATION ----------------
elif option == "Medication":

    st.header("💊 Advanced Medication Manager")

    medicine_name = st.text_input("Medicine Name")

    medicine_type = st.selectbox(
        "Medicine Type",
        ["Tablet", "Syrup", "Capsule", "Injection"]
    )

    # -------- TABLETS --------
    if medicine_type == "Tablet" or medicine_type == "Capsule":

        quantity = st.number_input(
            "Number of Tablets/Capsules",
            min_value=1,
            step=1
        )

        dosage = f"{quantity} Tablet(s)"

    # -------- SYRUP --------
    elif medicine_type == "Syrup":

        syrup_ml = st.number_input(
            "Syrup Quantity (ml)",
            min_value=1
        )

        dosage = f"{syrup_ml} ml"

    # -------- INJECTION --------
    else:

        dosage = st.text_input("Injection Dosage")

    # -------- TIME --------
    medicine_time = st.time_input("Reminder Time")

    # -------- SAVE --------
    if st.button("Save Medication"):

        reminders.insert_one({
            "medicine": medicine_name,
            "type": medicine_type,
            "dosage": dosage,
            "time": str(medicine_time)
        })

        st.success("✅ Medication Saved Successfully!")

    # -------- SHOW SAVED MEDICATIONS --------
    st.subheader("📋 Saved Medications")

    med_data = list(reminders.find())

    if med_data:

        df = pd.DataFrame(med_data)

        if "_id" in df.columns:
            df = df.drop("_id", axis=1)

        st.dataframe(df)
# ---------------- FITNESS ----------------
elif option == "Fitness":

    st.header("🏃 Smart Fitness Tracker")

    steps = st.number_input("Steps Walked", min_value=0)

    calories = st.number_input("Calories Burned", min_value=0)

    duration = st.number_input("Workout Duration (Minutes)", min_value=0)

    water = st.number_input("Water Intake (Litres)", min_value=0.0)

    weight = st.number_input("Current Weight (kg)", min_value=0.0)

    exercise = st.selectbox(
        "Exercise Type",
        ["Walking", "Running", "Gym", "Yoga", "Cycling"]
    )

    # -------- DISTANCE --------
    distance = round(steps * 0.0008, 2)

    st.write(f"📏 Estimated Distance: {distance} km")

    # -------- SAVE --------
    if st.button("Save Fitness"):

        fitness.insert_one({
            "steps": steps,
            "calories": calories,
            "duration": duration,
            "water": water,
            "weight": weight,
            "exercise": exercise,
            "distance": distance
        })

        st.success("✅ Fitness Data Saved!")

    # -------- SHOW DATA --------
    st.subheader("📊 Fitness Records")

    data = list(fitness.find())

    if data:

        df = pd.DataFrame(data)

        if "_id" in df.columns:
            df = df.drop("_id", axis=1)

        st.dataframe(df)

        # -------- ANALYTICS --------
        st.subheader("📈 Fitness Analytics")

        st.line_chart(df[["steps", "calories"]])

        # -------- FITNESS STATUS --------
        avg_steps = df["steps"].mean()

        if avg_steps < 3000:
            st.warning("⚠️ Low Activity")
        elif avg_steps < 7000:
            st.info("👍 Moderate Activity")
        else:
            st.success("🔥 Excellent Activity")
# ---------------- DASHBOARD ----------------
elif option == "Dashboard":

    st.header("📊 Smart Health Dashboard")

    data = list(fitness.find())

    if data:

        df = pd.DataFrame(data)

        # -------- REMOVE ID --------
        if "_id" in df.columns:
            df = df.drop("_id", axis=1)

        # -------- METRICS --------
        total_steps = int(df["steps"].sum())
        avg_steps = round(df["steps"].mean(), 2)
        total_calories = int(df["calories"].sum())

        avg_water = round(df["water"].mean(), 2) if "water" in df.columns else 0

        total_duration = int(df["duration"].sum()) if "duration" in df.columns else 0

        # -------- METRIC CARDS --------
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("👣 Total Steps", total_steps)

        col2.metric("🔥 Calories", total_calories)

        col3.metric("💧 Avg Water", f"{avg_water} L")

        col4.metric("⏱ Workout Time", f"{total_duration} min")

        st.markdown("---")

        # -------- GOAL PROGRESS --------
        goal = 10000

        progress = min(total_steps / goal, 1.0)

        st.subheader("🎯 Daily Goal Progress")

        st.progress(progress)

        st.write(f"{round(progress * 100, 2)}% of daily goal completed")

        # -------- CHARTS --------
        st.subheader("📈 Activity Trends")

        st.line_chart(df[["steps", "calories"]])

        # -------- WATER CHART --------
        if "water" in df.columns:
            st.subheader("💧 Water Intake")

            st.bar_chart(df["water"])

        # -------- RECENT RECORDS --------
        st.subheader("📋 Recent Fitness Records")

        st.dataframe(df.tail())

        # -------- FITNESS STATUS --------
        st.subheader("🏅 Fitness Status")

        if avg_steps < 3000:
            st.warning("⚠️ Low Activity Level")

        elif avg_steps < 7000:
            st.info("👍 Moderate Activity")

        else:
            st.success("🔥 Excellent Fitness Level")

        # -------- HEALTH SCORE --------
        st.subheader("❤️ Health Score")

        score = 0

        if avg_steps > 7000:
            score += 40

        if avg_water >= 2:
            score += 30

        if total_duration >= 30:
            score += 30

        st.metric("Health Score", f"{score}/100")

        # -------- AI SUGGESTIONS --------
        st.subheader("🤖 Smart Suggestions")

        if avg_water < 2:
            st.warning("Drink more water 💧")

        if avg_steps < 5000:
            st.warning("Increase physical activity 🚶")

        if total_duration < 20:
            st.warning("Try longer workouts 🏃")

# ---------------- REPORT ----------------
elif option == "Report":

    st.header("📄 Smart Health Report")

    data = list(fitness.find())

    if data:

        df = pd.DataFrame(data)

        # -------- REMOVE ID --------
        if "_id" in df.columns:
            df = df.drop("_id", axis=1)

        # -------- CALCULATIONS --------
        avg_steps = round(df["steps"].mean(), 2)

        total_steps = int(df["steps"].sum())

        avg_calories = round(df["calories"].mean(), 2)

        avg_water = round(df["water"].mean(), 2) if "water" in df.columns else 0

        avg_duration = round(df["duration"].mean(), 2) if "duration" in df.columns else 0

        # -------- REPORT SUMMARY --------
        st.subheader("📊 Health Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("👣 Avg Steps", avg_steps)

        col2.metric("🔥 Avg Calories", avg_calories)

        col3.metric("💧 Avg Water", f"{avg_water} L")

        col4.metric("⏱ Avg Workout", f"{avg_duration} min")

        st.markdown("---")

        # -------- ACTIVITY STATUS --------
        st.subheader("🏅 Activity Level")

        if avg_steps < 3000:

            st.warning("⚠️ Low Activity Level")

            activity_msg = """
            You are currently less active.

            🔹 Walk at least 30 minutes daily
            🔹 Avoid sitting for long hours
            🔹 Try light exercises or yoga
            🔹 Increase water intake
            """

        elif avg_steps < 7000:

            st.info("👍 Moderate Activity Level")

            activity_msg = """
            Your activity level is average.

            🔹 Increase daily walking
            🔹 Maintain regular workouts
            🔹 Eat balanced meals
            🔹 Sleep at least 7 hours
            """

        else:

            st.success("🔥 Excellent Activity Level")

            activity_msg = """
            Great job maintaining fitness!

            🔹 Continue regular exercise
            🔹 Maintain healthy diet
            🔹 Stay hydrated
            🔹 Keep tracking your health
            """

        st.write(activity_msg)

        st.markdown("---")

        # -------- WATER ANALYSIS --------
        st.subheader("💧 Water Intake Analysis")

        if avg_water < 2:
            st.warning("You should drink more water.")

            st.write("""
            Recommended:
            - Drink 2-3 litres daily
            - Carry water bottle
            - Avoid dehydration
            """)

        else:
            st.success("Good hydration level!")

        st.markdown("---")

        # -------- WORKOUT ANALYSIS --------
        st.subheader("🏃 Workout Analysis")

        if avg_duration < 20:

            st.warning("Workout duration is low.")

            st.write("""
            Suggestions:
            - Try 30 min workouts
            - Add cardio exercises
            - Do stretching daily
            """)

        else:

            st.success("Good workout consistency!")

        st.markdown("---")

        # -------- HEALTH SCORE --------
        st.subheader("❤️ Health Score")

        score = 0

        # Steps
        if avg_steps >= 7000:
            score += 40
        elif avg_steps >= 4000:
            score += 20

        # Water
        if avg_water >= 2:
            score += 30

        # Workout
        if avg_duration >= 30:
            score += 30

        st.metric("Overall Health Score", f"{score}/100")

        # -------- FINAL HEALTH STATUS --------
        if score < 40:
            st.error("❌ Health Needs Improvement")

        elif score < 70:
            st.info("👍 Fair Health Condition")

        else:
            st.success("🔥 Healthy Lifestyle")

        st.markdown("---")

        # -------- HEALTH TIPS --------
        st.subheader("🌿 Tips to Stay Healthy")

        tips = [
            "🥗 Eat balanced nutritious food",
            "🚶 Walk daily",
            "💧 Drink enough water",
            "😴 Sleep 7-8 hours",
            "🏃 Exercise regularly",
            "🧘 Reduce stress",
            "🍎 Eat fruits and vegetables",
            "📵 Reduce screen time"
        ]

        for tip in tips:
            st.write(tip)

        st.markdown("---")

        # -------- REPORT TABLE --------
        st.subheader("📋 Recent Fitness Records")

        st.dataframe(df.tail())

    else:

        st.warning("No fitness data available.")
# ---------------- GOALS ----------------
elif option == "Goals":

    st.header("🎯 Smart Health Goals")

    # -------- GOAL INPUTS --------
    step_goal = st.number_input(
        "Daily Step Goal",
        min_value=0,
        value=10000
    )

    water_goal = st.number_input(
        "Daily Water Goal (Litres)",
        min_value=0.0,
        value=2.0
    )

    workout_goal = st.number_input(
        "Workout Goal (Minutes)",
        min_value=0,
        value=30
    )

    weight_goal = st.number_input(
        "Target Weight (kg)",
        min_value=0.0
    )

    # -------- SAVE GOALS --------
    if st.button("Save Goals"):

        goals.insert_one({
            "step_goal": step_goal,
            "water_goal": water_goal,
            "workout_goal": workout_goal,
            "weight_goal": weight_goal
        })

        st.success("✅ Goals Saved Successfully!")

    st.markdown("---")

    # -------- FETCH FITNESS DATA --------
    fitness_data = list(fitness.find())

    goal_data = list(goals.find())

    if fitness_data and goal_data:

        df = pd.DataFrame(fitness_data)

        latest_goal = goal_data[-1]

        # -------- CURRENT VALUES --------
        current_steps = df["steps"].sum()

        current_water = df["water"].mean() if "water" in df.columns else 0

        current_workout = df["duration"].mean() if "duration" in df.columns else 0

        current_weight = df["weight"].mean() if "weight" in df.columns else 0

        # -------- PROGRESS CALCULATIONS --------
        step_progress = min(current_steps / latest_goal["step_goal"], 1.0)

        water_progress = min(current_water / latest_goal["water_goal"], 1.0)

        workout_progress = min(current_workout / latest_goal["workout_goal"], 1.0)

        # -------- DISPLAY PROGRESS --------
        st.subheader("📊 Goal Progress")

        # Steps
        st.write(f"👣 Steps Goal: {current_steps}/{latest_goal['step_goal']}")
        st.progress(step_progress)

        # Water
        st.write(f"💧 Water Goal: {round(current_water,2)}/{latest_goal['water_goal']} L")
        st.progress(water_progress)

        # Workout
        st.write(f"🏃 Workout Goal: {round(current_workout,2)}/{latest_goal['workout_goal']} min")
        st.progress(workout_progress)

        st.markdown("---")

        # -------- ACHIEVEMENT SYSTEM --------
        st.subheader("🏅 Achievement Status")

        total_score = (
            step_progress +
            water_progress +
            workout_progress
        ) / 3

        if total_score < 0.5:

            st.warning("⚠️ Beginner Level")

            st.write("""
            Suggestions:
            - Walk more daily
            - Drink more water
            - Increase physical activity
            """)

        elif total_score < 1:

            st.info("👍 Active Lifestyle")

            st.write("""
            Great progress!

            Keep maintaining consistency.
            """)

        else:

            st.success("🔥 Fitness Champion!")

            st.write("""
            Excellent work!

            You are achieving your goals consistently.
            """)

        st.markdown("---")

        # -------- SMART RECOMMENDATIONS --------
        st.subheader("🤖 Smart Recommendations")

        if step_progress < 1:
            remaining = latest_goal["step_goal"] - current_steps

            st.warning(f"🚶 Walk {remaining} more steps to reach your goal.")

        if water_progress < 1:
            st.warning("💧 Increase your water intake.")

        if workout_progress < 1:
            st.warning("🏃 Try longer workouts.")

        # -------- MOTIVATION --------
        st.subheader("🌟 Daily Motivation")

        motivation_quotes = [
            "Small progress is still progress 💪",
            "Your health is your greatest wealth ❤️",
            "Stay consistent and trust the process 🔥",
            "Every step counts 🚶"
        ]

        import random

        st.info(random.choice(motivation_quotes))

    else:

        st.warning("No fitness or goals data available.")

# ---------------- MEDICAL HISTORY ----------------
elif option == "Medical History":

    st.header("🏥 Smart Medical History")

    # -------- PERSONAL INFO --------
    st.subheader("👤 Personal Information")

    name = st.text_input("Full Name")

    age = st.number_input("Age", min_value=0)

    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Other"]
    )

    blood_group = st.selectbox(
        "Blood Group",
        ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    )

    phone = st.text_input("Phone Number")

    emergency_contact = st.text_input("Emergency Contact")

    st.markdown("---")

    # -------- MEDICAL DETAILS --------
    st.subheader("🩺 Medical Details")

    disease = st.text_area(
        "Diseases / Conditions",
        placeholder="Diabetes, BP, Asthma..."
    )

    allergies = st.text_area(
        "Allergies",
        placeholder="Penicillin, Dust..."
    )

    medications = st.text_area(
        "Current Medications",
        placeholder="Dolo 650, Insulin..."
    )

    family_history = st.text_area(
        "Family Medical History",
        placeholder="Heart Disease, Diabetes..."
    )

    st.markdown("---")

    # -------- INSURANCE --------
    st.subheader("🏥 Insurance Details")

    insurance_provider = st.text_input("Insurance Provider")

    policy_number = st.text_input("Policy Number")

    st.markdown("---")

    # -------- DOCTOR INFO --------
    st.subheader("👨‍⚕️ Doctor Details")

    doctor_name = st.text_input("Doctor Name")

    last_checkup = st.date_input("Last Checkup Date")

    st.markdown("---")

    # -------- FILE UPLOAD --------
    st.subheader("📄 Upload Medical Reports")

    uploaded_file = st.file_uploader(
        "Upload Reports",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    st.markdown("---")

    # -------- SAVE --------
    if st.button("Save Medical History"):

        medical_history.insert_one({

            "name": name,
            "age": age,
            "gender": gender,
            "blood_group": blood_group,
            "phone": phone,
            "emergency_contact": emergency_contact,

            "disease": disease,
            "allergies": allergies,
            "medications": medications,
            "family_history": family_history,

            "insurance_provider": insurance_provider,
            "policy_number": policy_number,

            "doctor_name": doctor_name,
            "last_checkup": str(last_checkup),

            "uploaded_report": uploaded_file.name if uploaded_file else "No File"
        })

        st.success("✅ Medical History Saved Successfully!")

    st.markdown("---")

    # -------- SHOW RECORDS --------
    st.subheader("📋 Saved Medical Records")

    records = list(medical_history.find())

    if records:

        df = pd.DataFrame(records)

        if "_id" in df.columns:
            df = df.drop("_id", axis=1)

        st.dataframe(df)

    st.markdown("---")

    # -------- HEALTH ALERTS --------
    st.subheader("⚠️ Smart Health Alerts")

    disease_lower = disease.lower()

    if "diabetes" in disease_lower:
        st.warning("""
        🍬 Diabetes Advice:
        - Reduce sugar intake
        - Exercise regularly
        - Monitor blood sugar
        """)

    if "bp" in disease_lower or "blood pressure" in disease_lower:
        st.warning("""
        ❤️ BP Advice:
        - Reduce salt intake
        - Avoid stress
        - Check BP regularly
        """)

    if "asthma" in disease_lower:
        st.warning("""
        🌬 Asthma Advice:
        - Avoid dust/smoke
        - Carry inhaler
        - Exercise carefully
        """)

    # -------- HEALTH SCORE --------
    st.subheader("❤️ Health Risk Analysis")

    risk_score = 0

    if disease:
        risk_score += 30

    if allergies:
        risk_score += 20

    if age > 50:
        risk_score += 30

    if family_history:
        risk_score += 20

    st.metric("Risk Score", f"{risk_score}/100")

    if risk_score < 30:
        st.success("✅ Low Health Risk")

    elif risk_score < 70:
        st.info("⚠️ Moderate Health Risk")

    else:
        st.error("❌ High Health Risk")
# ---------------- UPLOAD ----------------
elif option == "Upload Data":
    file = st.file_uploader("Upload JSON/CSV", type=["json","csv"])
    if file:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
            st.write(df)

# ---------------- AYURVEDIC ----------------
# =========================================================
# 🌿 AYURVEDIC CHATBOT SECTION
# =========================================================

elif option == "Ayurvedic":

    st.header("🌿 Ayurvedic AI Assistant")

    st.write("""
    Ask about:
    - Ayurvedic medicines
    - Herbs
    - Home remedies
    - Yoga
    - Natural healing
    """)

    # -------- AYURVEDIC CHAT ID --------
    ayur_chat_id = "Ayurvedic Chat"

    # -------- CREATE CHAT IF NOT EXISTS --------
    if ayur_chat_id not in st.session_state.chat_sessions:

        st.session_state.chat_sessions[
            ayur_chat_id
        ] = []

    # -------- GET MESSAGES --------
    ayurvedic_messages = st.session_state.chat_sessions[
        ayur_chat_id
    ]

    # -------- DISPLAY OLD CHATS --------
    for msg in ayurvedic_messages:

        with st.chat_message(msg["role"]):

            st.write(msg["content"])

    # -------- USER INPUT --------
    user_input = st.chat_input(
        "Ask Ayurvedic Question..."
    )

    # -------- PROCESS --------
    if user_input:

        # ===== SAVE USER MESSAGE =====
        ayurvedic_messages.append({

            "role": "user",

            "content": user_input
        })

        # ===== DISPLAY USER MESSAGE =====
        with st.chat_message("user"):

            st.write(user_input)

        # ===== AI RESPONSE =====
        with st.chat_message("assistant"):

            with st.spinner(
                "Generating Ayurvedic Advice..."
            ):

                try:

                    response = ayurvedic_ai_chatbot(
                        user_input
                    )

                    st.write(response)

                except Exception as e:

                    response = f"Error: {e}"

                    st.error(response)

        # ===== SAVE RESPONSE =====
        ayurvedic_messages.append({

            "role": "assistant",

            "content": response
        })

        # ===== SAVE SESSION =====
        st.session_state.chat_sessions[
            ayur_chat_id
        ] = ayurvedic_messages

        # ===== SAVE TO MONGODB =====
        ayurvedic_chat_history.insert_one({

            "chat": ayur_chat_id,

            "user": user_input,

            "bot": response
        })

    st.markdown("---")

    st.warning("""
    ⚠️ Ayurvedic advice is for educational purposes only.

    Consult doctors for serious conditions.
    """)

# ---------------- DIET ----------------
elif option == "Diet":

    st.header("🥗 Indian Diet Planner")

    goal = st.selectbox(
        "Choose Goal",
        [
            "Weight Loss",
            "Weight Gain",
            "Diabetes",
            "Immunity",
            "Fitness"
        ]
    )

    diet_plans = {

        "Weight Loss": [
            "🥗 Salad",
            "🍵 Green Tea",
            "🚫 Avoid junk food"
        ],

        "Weight Gain": [
            "🥛 Milk",
            "🍌 Banana",
            "🥜 Nuts"
        ],

        "Diabetes": [
            "🥬 Green vegetables",
            "🚫 Reduce sugar",
            "🌾 Whole grains"
        ],

        "Immunity": [
            "🍊 Fruits",
            "🌿 Tulsi Tea",
            "🥛 Turmeric Milk"
        ],

        "Fitness": [
            "🍗 Protein rich foods",
            "🥚 Eggs",
            "🍚 Healthy carbs"
        ]
    }

    st.subheader(f"📋 Diet Plan for {goal}")

    for item in diet_plans[goal]:

        st.write(item)

# ---------------- DOCTOR RECOMMENDATION ----------------
elif option == "Doctor Recommendation":

    st.header("👨‍⚕️ Doctor Recommendation")

    city = st.text_input("Enter Your City")

    speciality = st.selectbox(
        "Choose Speciality",
        [
            "General",
            "Cardiologist",
            "Dermatologist",
            "Ayurvedic",
            "Orthopedic"
        ]
    )

    if city:

        st.subheader(
            f"Doctors in {city}"
        )

        doctors = [

            {
                "name": "Dr. Sharma",
                "speciality": speciality,
                "rating": "4.8⭐"
            },

            {
                "name": "Dr. Reddy",
                "speciality": speciality,
                "rating": "4.7⭐"
            },

            {
                "name": "Dr. Patel",
                "speciality": speciality,
                "rating": "4.9⭐"
            }
        ]

        for doc in doctors:

            st.success(
                f"""
                👨‍⚕️ {doc['name']}

                🩺 {doc['speciality']}

                ⭐ {doc['rating']}
                """
            )
