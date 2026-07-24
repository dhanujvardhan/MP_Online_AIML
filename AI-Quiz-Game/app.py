# ---------------- IMPORTS ----------------
import streamlit as st
import json
import random
import time
import base64
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
import google.generativeai as genai
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# ---------------- GEMINI API ----------------



load_dotenv()
# ---------------- FIREBASE SETUP ----------------

if not firebase_admin._apps:

    firebase_creds = json.loads(
        os.getenv("FIREBASE_CREDENTIALS")
    )

    cred = credentials.Certificate(
        firebase_creds
    )

    firebase_admin.initialize_app(cred)

db = firestore.client()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-3.5-flash"
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Quiz Game",
    page_icon="🧠",
    layout="centered"
)

# ---------------- DARK UI CSS ----------------
st.markdown("""
<style>

body {
    background-color: #0f172a;
}

.stApp {
    background: linear-gradient(to right, #0f172a, #111827);
    color: white;
}

/* Title */
.title {
    text-align: center;
    font-size: 55px;
    font-weight: bold;
    color: #38bdf8;
    margin-bottom: 20px;
}

/* Score Box */
.score-box {
    padding: 20px;
    border-radius: 18px;
    background-color: #1e293b;
    margin-bottom: 20px;
    text-align: center;
    font-size: 24px;
    color: white;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.6);
}

/* Stats Box */
.stats-box {
    padding: 18px;
    border-radius: 18px;
    background-color: #172033;
    margin-bottom: 20px;
    text-align: center;
    font-size: 20px;
    color: white;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.5);
}

/* Question Box */
.question-box {
    padding: 25px;
    border-radius: 18px;
    background-color: #1e293b;
    margin-top: 20px;
    margin-bottom: 20px;
    color: white;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.5);
}

/* Timer */
.timer-box {
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    color: #facc15;
    margin-bottom: 20px;
}

/* Radio */
.stRadio > div {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 15px;
}

/* Button */
.stButton>button {
    width: 100%;
    background-color: #38bdf8;
    color: black;
    font-size: 22px;
    font-weight: bold;
    border-radius: 12px;
    padding: 12px;
    border: none;
}

.stButton>button:hover {
    background-color: #0ea5e9;
    color: white;
}

/* Game Over */
.game-over {
    padding: 25px;
    border-radius: 20px;
    background-color: #1e293b;
    text-align: center;
    font-size: 28px;
    color: white;
    box-shadow: 0px 0px 20px rgba(0,0,0,0.7);
}

/* Leaderboard */
.leaderboard {
    padding: 20px;
    border-radius: 18px;
    background-color: #1e293b;
    margin-top: 20px;
    color: white;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.5);
}

</style>
""", unsafe_allow_html=True)

# ---------------- PLAY SOUND FUNCTION ----------------
def autoplay_audio(file_path):

    with open(file_path, "rb") as f:
        data = f.read()

    b64 = base64.b64encode(data).decode()

    audio_id = random.randint(1, 9999999)

    md = f"""
    <audio id="{audio_id}" autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """

    st.markdown(md, unsafe_allow_html=True)

# ---------------- GAME OVER SOUND ----------------
def game_over_sound():

    autoplay_audio("sounds/gameover.mp3")

# ---------------- AI QUESTION GENERATOR ----------------
def generate_ai_question(category, difficulty):

    prompt = f"""
    Generate 1 MCQ question for quiz game.

    Category: {category}
    Difficulty: {difficulty}

    Return ONLY valid JSON format like this:

    {{
      "question": "Your Question",
      "options": ["A", "B", "C", "D"],
      "answer": "Correct Answer"
    }}
    """

    try:

        response = model.generate_content(prompt)

        text = response.text.strip()

        # REMOVE ```json
        text = text.replace("```json", "")
        text = text.replace("```", "")

        question_data = json.loads(text)

        return question_data

    except Exception as e:

        st.warning("⚠️ AI Limit Reached — Using Offline Questions")

        return None


# ---------------- LOAD QUESTIONS ----------------
with open("questions.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

# # ---------------- LEADERBOARD FILE ----------------
# LEADERBOARD_FILE = "leaderboard.json"

# if not os.path.exists(LEADERBOARD_FILE):

#     with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
#         json.dump([], f)

# ---------------- SESSION STATE ----------------
if "score" not in st.session_state:
    st.session_state.score = 0

if "difficulty" not in st.session_state:
    st.session_state.difficulty = "easy"

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "correct_answers" not in st.session_state:
    st.session_state.correct_answers = 0

if "wrong_answers" not in st.session_state:
    st.session_state.wrong_answers = 0

if "game_over" not in st.session_state:
    st.session_state.game_over = False

if "leaderboard_saved" not in st.session_state:
    st.session_state.leaderboard_saved = False

if "category" not in st.session_state:
    st.session_state.category = None

if "last_question" not in st.session_state:
    st.session_state.last_question = ""


# ---------------- ANALYTICS ----------------
if "score_history" not in st.session_state:
    st.session_state.score_history = []

if "difficulty_history" not in st.session_state:
    st.session_state.difficulty_history = []

# ---------------- CATEGORY SELECTION ----------------
if st.session_state.category is None:

    st.markdown(
        """
        <div class="question-box">
            <h1 style='text-align:center; color:#38bdf8;'>
                📚 Select Quiz Category
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    category = st.selectbox(
        "Choose Category",
        [
            "Python",
            "AI",
            "DBMS",
            "ML",
            "Aptitude",
            "Cyber Security"
        ]
    )

    if st.button("🚀 Start Quiz"):

        st.session_state.category = category

        # GENERATE AI QUESTION
        ai_question = generate_ai_question(
            category,
            "easy"
        )

        # FALLBACK OFFLINE QUESTION
        if ai_question:

            st.session_state.current_question = ai_question

        else:

            category_questions = [
                q for q in questions
                if q["category"] == category
            ]

            st.session_state.current_question = random.choice(
                category_questions
            )

        st.session_state.start_time = time.time()

        st.rerun()

    st.stop()
# ---------------- GAME STATS ----------------
total_questions = (
    st.session_state.correct_answers +
    st.session_state.wrong_answers
)

if total_questions > 0:
    accuracy = int(
        (st.session_state.correct_answers / total_questions) * 100
    )
else:
    accuracy = 0

MAX_QUESTIONS = 10


if not st.session_state.game_over:
    st_autorefresh(interval=1000, key="timer_refresh")
# ---------------- TITLE ----------------
st.markdown(
    '<div class="title">🧠 AI Quiz Game</div>',
    unsafe_allow_html=True
)

# ---------------- SCORE BOX ----------------
st.markdown(
    f"""
    <div class="score-box">
        🏆 Score: {st.session_state.score}
        <br><br>
        🎯 Difficulty: {st.session_state.difficulty.upper()}
        <br><br>
        📚 Category: {st.session_state.category}
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- PROGRESS BAR ----------------
st.progress(accuracy / 100)

# ---------------- STATS BOX ----------------
st.markdown(
    f"""
    <div class="stats-box">
        ✅ Correct Answers: {st.session_state.correct_answers}
        <br><br>
        ❌ Wrong Answers: {st.session_state.wrong_answers}
        <br><br>
        📊 Accuracy: {accuracy}%
        <br><br>
        📚 Questions Attempted: {total_questions}/{MAX_QUESTIONS}
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# ================== GAME OVER SCREEN =====================
# =========================================================



if total_questions >= MAX_QUESTIONS:
    st.session_state.game_over = True

if st.session_state.game_over:

    if "balloons_shown" not in st.session_state:
        st.balloons()
        st.session_state.balloons_shown = True

    game_over_sound()

    st.markdown(
        f"""
        <div class="game-over">
            🏁 GAME OVER
            <br><br>
            🏆 Final Score: {st.session_state.score}
            <br><br>
            📊 Accuracy: {accuracy}%
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- PERFORMANCE SUMMARY ----------------
    st.subheader("📋 Performance Summary")

    if accuracy >= 80:
        st.success("🔥 Excellent Performance!")
    elif accuracy >= 50:
        st.info("👍 Good Job!")
    else:
        st.warning("📚 Keep Practicing!")

    # ================= CHARTS =================

    col1, col2 = st.columns(2)

    # ---------------- BAR CHART ----------------
    with col1:

        st.subheader("📊 Accuracy")

        chart_data = pd.DataFrame({
            "Result": ["Correct", "Wrong"],
            "Count": [
                st.session_state.correct_answers,
                st.session_state.wrong_answers
            ]
        })

        fig1, ax1 = plt.subplots(figsize=(4, 3))

        ax1.bar(
            chart_data["Result"],
            chart_data["Count"]
        )

        st.pyplot(fig1)

    # ---------------- PIE CHART ----------------
    with col2:

        st.subheader("🥧 Result Pie")

        fig2, ax2 = plt.subplots(figsize=(4, 3))

        pie_values = [
            st.session_state.correct_answers,
            st.session_state.wrong_answers
        ]

        if sum(pie_values) == 0:

            ax2.text(
                0.5,
                0.5,
                "No Data",
                ha='center',
                va='center',
                fontsize=14
            )

            ax2.axis('off')

        else:

            ax2.pie(
                pie_values,
                labels=["Correct", "Wrong"],
                autopct='%1.1f%%'
            )

            ax2.axis('equal')

        st.pyplot(fig2)

    # ================= SECOND ROW =================

    col3, col4 = st.columns(2)

    # ---------------- SCORE TREND ----------------
    with col3:

        st.subheader("📈 Score Trend")

        fig3, ax3 = plt.subplots(figsize=(4, 3))

        if len(st.session_state.score_history) > 0:

            ax3.plot(
                st.session_state.score_history,
                marker='o'
            )

        else:

            ax3.text(
                0.5,
                0.5,
                "No Data",
                ha='center',
                va='center'
            )

        st.pyplot(fig3)

    # ---------------- DIFFICULTY CHART ----------------
    with col4:

        st.subheader("🎯 Difficulty")

        difficulty_counts = {
            "easy": st.session_state.difficulty_history.count("easy"),
            "medium": st.session_state.difficulty_history.count("medium"),
            "hard": st.session_state.difficulty_history.count("hard")
        }

        fig4, ax4 = plt.subplots(figsize=(4, 3))

        ax4.bar(
            difficulty_counts.keys(),
            difficulty_counts.values()
        )

        st.pyplot(fig4)

    # ---------------- PLAYER NAME ----------------
    player_name = st.text_input(
        "👤 Enter Your Name"
    )

    # ---------------- SAVE SCORE ----------------
   
    if st.button("💾 Save Score"):

        if player_name.strip():

            db.collection("leaderboard").add({
                "name": player_name,
                "score": st.session_state.score
            })

            st.success("🏆 Score Saved Successfully!")

        else:
            st.error("Enter Name First")

    # ---------------- SHOW LEADERBOARD ----------------
    st.write("DEBUG START")
 
    leaderboard_ref = db.collection("leaderboard") \
        .order_by("score", direction=firestore.Query.DESCENDING) \
        .limit(10)

    leaderboard = leaderboard_ref.stream()

    st.markdown(
        """
        <div class="leaderboard">
            <h2>🏆 TOP PLAYERS</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    rank = 1


    players = list(leaderboard)

    st.write("Total Records:", len(players))


    for player in players:

        player_data = player.to_dict()

        st.write(
            player_data["name"],
            player_data["score"]
        )
    # for player in leaderboard:

    #     player_data = player.to_dict()

    #     st.markdown(
    #         f"""
    #         ✅ #{rank} — {player_data['name']} :
    #         {player_data['score']} Points
    #         """
    #     )

    #     rank += 1

    # ---------------- RESTART BUTTON ----------------
    if st.button("🔄 Restart Game"):
        st.session_state.asked_questions = []
        st.session_state.score = 0
        st.session_state.correct_answers = 0
        st.session_state.wrong_answers = 0
        st.session_state.difficulty = "easy"
        st.session_state.game_over = False
        st.session_state.current_question = random.choice(
            questions
        )

        st.session_state.start_time = time.time()
        st.session_state.category = None
        st.session_state.score_history = []
        st.session_state.balloons_shown = False
        st.session_state.difficulty_history = []

        st.rerun()

    st.stop()

# =========================================================
# ================== QUIZ SECTION ==========================
# =========================================================
if st.session_state.game_over:
    st.stop()
# ---------------- FILTER QUESTIONS ----------------
filtered_questions = [
    q for q in questions
    if q["difficulty"] == st.session_state.difficulty
    and q["category"] == st.session_state.category
]

# ---------------- FALLBACK 1 ----------------
if len(filtered_questions) == 0:

    filtered_questions = [
        q for q in questions
        if q["category"] == st.session_state.category
    ]

# ---------------- FALLBACK 2 ----------------
if len(filtered_questions) == 0:

    filtered_questions = questions

# ---------------- TRACK ASKED QUESTIONS ----------------
if "asked_questions" not in st.session_state:

    st.session_state.asked_questions = []

# ---------------- REMOVE REPEATED QUESTIONS ----------------
available_questions = [
    q for q in filtered_questions
    if q["question"] not in st.session_state.asked_questions
]

# ---------------- RESET IF ALL USED ----------------
if len(available_questions) == 0:

    st.session_state.asked_questions = []

    available_questions = filtered_questions

# ---------------- CURRENT QUESTION SAFETY ----------------
if (
    "current_question" not in st.session_state
    or st.session_state.current_question not in available_questions
):

    st.session_state.current_question = random.choice(
        available_questions
    )

# ---------------- FINAL QUESTION ----------------
question = st.session_state.current_question

# if question["question"] != st.session_state.last_question:

#     st.session_state.start_time = time.time()

#     st.session_state.last_question = question["question"]

# ---------------- QUESTION BOX ----------------
st.markdown(
    f"""
    <div class="question-box">
        <h2>{question["question"]}</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- TIMER ----------------
elapsed_time = int(
    time.time() - st.session_state.start_time
)

time_left = max(15 - elapsed_time, 0)

st.markdown(
    f"""
    <div class="timer-box">
        ⏳ Time Left: {time_left} sec
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- TIME OVER ----------------
if time_left == 0:

    st.error("⏰ Time Over!")

    autoplay_audio("sounds/wrong.mp3")

    st.session_state.score -= 1
    st.session_state.wrong_answers += 1

    st.session_state.score_history.append(
        st.session_state.score
    )

    st.session_state.difficulty_history.append(
        st.session_state.difficulty
    )

    # ADD CURRENT QUESTION TO USED LIST
    st.session_state.asked_questions.append(
        question["question"]
    )

    # REMOVE CURRENT QUESTION
    available_questions = [
        q for q in available_questions
        if q["question"] != question["question"]
    ]

    # AI QUESTION
    next_question = generate_ai_question(
        st.session_state.category,
        st.session_state.difficulty
    )

    # FALLBACK OFFLINE QUESTION
    if next_question is None:

        if len(available_questions) > 0:

            next_question = random.choice(
                available_questions
            )

        else:

            # RESET USED QUESTIONS
            st.session_state.asked_questions = []

            filtered_questions = [
                q for q in questions
                if q["category"] == st.session_state.category
            ]

            next_question = random.choice(
                filtered_questions
            )

    st.session_state.current_question = next_question

    st.session_state.start_time = time.time()

    st.rerun()

# ---------------- OPTIONS ----------------
selected_option = st.radio(
    "Choose your answer:",
    question["options"],
    key=f"radio_{total_questions}"
)

# ---------------- SUBMIT BUTTON ----------------
if st.button("🚀 Submit Answer"):

    # ---------------- CORRECT ANSWER ----------------
    if selected_option == question["answer"]:

        st.success("✅ Correct Answer!")

        autoplay_audio("sounds/correct.mp3")

        st.session_state.score += 1
        st.session_state.correct_answers += 1

    # ---------------- WRONG ANSWER ----------------
    else:

        st.error(
            f"❌ Wrong! Correct Answer: {question['answer']}"
        )

        autoplay_audio("sounds/wrong.mp3")

        st.session_state.score -= 1
        st.session_state.wrong_answers += 1

    # ---------------- SAVE ANALYTICS ----------------
    st.session_state.score_history.append(
        st.session_state.score
    )

    st.session_state.difficulty_history.append(
        st.session_state.difficulty
    )

    # ---------------- AI DIFFICULTY ----------------
    if st.session_state.score <= 1:

        st.session_state.difficulty = "easy"

    elif 2 <= st.session_state.score <= 4:

        st.session_state.difficulty = "medium"

    else:

        st.session_state.difficulty = "hard"

    # ---------------- FILTER AGAIN ----------------
    filtered_questions = [
        q for q in questions
        if q["difficulty"] == st.session_state.difficulty
        and q["category"] == st.session_state.category
    ]

    # ---------------- FALLBACK ----------------
    if len(filtered_questions) == 0:

        filtered_questions = [
            q for q in questions
            if q["category"] == st.session_state.category
        ]

    # ---------------- REMOVE USED QUESTIONS ----------------
    available_questions = [
        q for q in filtered_questions
        if q["question"] not in st.session_state.asked_questions
    ]

    # ---------------- RESET IF ALL USED ----------------
    if len(available_questions) == 0:

        st.session_state.asked_questions = []

        available_questions = filtered_questions

    # ---------------- NEXT QUESTION ----------------
    # ADD CURRENT QUESTION TO USED LIST
    st.session_state.asked_questions.append(
        question["question"]
    )

    # REMOVE CURRENT QUESTION
    available_questions = [
        q for q in available_questions
        if q["question"] != question["question"]
    ]

    # AI QUESTION
    next_question = generate_ai_question(
        st.session_state.category,
        st.session_state.difficulty
    )

    # FALLBACK OFFLINE QUESTION
    if next_question is None:

        if len(available_questions) > 0:

            next_question = random.choice(
                available_questions
            )

        else:

            # RESET USED QUESTIONS
            st.session_state.asked_questions = []

            filtered_questions = [
                q for q in questions
                if q["category"] == st.session_state.category
            ]

            next_question = random.choice(
                filtered_questions
            )

    st.session_state.current_question = next_question

    # st.session_state.asked_questions.append(
    #     next_question["question"]
    # )

    # ---------------- RESET TIMER ----------------
    st.session_state.start_time = time.time()
    

    # time.sleep(0.5)

    st.rerun()