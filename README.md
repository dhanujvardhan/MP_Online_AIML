# 🚀 AI & Machine Learning Repository

Welcome to the ultimate **Artificial Intelligence and Machine Learning** repository! This repository contains a curated collection of state-of-the-art applications, reinforcement learning agents, custom neural networks, and machine learning pipelines.

---

## 📂 Repository Structure & Overview

```text
MP_Online_AIML/
│
├── 🧠 AI-Quiz-Game/                        # Dynamic Streamlit AI Quiz Application
├── 🤖 rag_chatbot/                          # 100% Local RAG Document Q&A App
├── 🏎️ Cart_Pole RL agent Traning/           # DQN agent balancing a CartPole in Gymnasium
│
├── 📊 adult_census_income_classification.ipynb   # Income prediction using census data
├── 🔬 Cancer_Detection.ipynb                 # Brain tumor MRI image classification (CNN)
├── 🐶 Image_Classification.ipynb             # Dog vs. Cat image classifier (CNN)
├── 🚀 Lunar_Lander_DQN.ipynb                 # Deep Q-Network landing spacecraft (RL)
├── 🎬 Movie_Recommendation_System.ipynb      # Content/Collaborative Filtering recommender
└── 🐯 Wildlife_Face_Recognition.ipynb        # Amur Tiger Identification (Transfer Learning)
```

---

## 🛠️ Complete Project Directory

| Project Name | Type | Key Technologies | Description |
| :--- | :--- | :--- | :--- |
| [🧠 AI Quiz Game](file:///C:/Users/dhanu/Downloads/MP_Online_AIML-main/MP_Online_AIML-main/AI-Quiz-Game) | **Full Web App** | Python, Streamlit, Gemini AI, Firebase | AI-generated, adaptive-difficulty quiz game with live leaderboards and analytics. |
| [🤖 Local RAG Chatbot](file:///C:/Users/dhanu/Downloads/MP_Online_AIML-main/MP_Online_AIML-main/rag_chatbot) | **Full-Stack App** | FastAPI, FAISS, PyPDF, Hugging Face (`flan-t5-base`) | Fully local, offline Document Q&A bot (no external APIs or cloud databases). |
| [🏎️ CartPole DQN Agent](file:///C:/Users/dhanu/Downloads/MP_Online_AIML-main/MP_Online_AIML-main/Cart_Pole%20RL%20agent%20Traning) | **RL Training** | PyTorch, Gymnasium (`CartPole-v1`), Python | Deep Q-Network balancing a pole on a cart using experience replay & double networks. |
| [📊 Income Classification](file:///C:/Users/dhanu/Downloads/MP_Online_AIML-main/MP_Online_AIML-main/adult_census_income_classification.ipynb) | **ML Notebook** | Scikit-Learn, Pandas, Seaborn, Matplotlib | Classifier predicting if income >$50k. Solves class imbalance and compares models. |
| [🔬 Brain Cancer Detection](file:///C:/Users/dhanu/Downloads/MP_Online_AIML-main/MP_Online_AIML-main/Cancer_Detection.ipynb) | **DL Notebook** | TensorFlow, Keras Sequential API, NumPy | Convolutional Neural Network (CNN) identifying brain tumors in MRI images. |
| [🐶 Cats & Dogs Classifier](file:///C:/Users/dhanu/Downloads/MP_Online_AIML-main/MP_Online_AIML-main/Image_Classification.ipynb) | **DL Notebook** | TensorFlow, Keras CNN, Augmentation | Binary CNN image classifier training pipeline for Cat vs. Dog recognition. |
| [🚀 Lunar Lander DQN](file:///C:/Users/dhanu/Downloads/MP_Online_AIML-main/MP_Online_AIML-main/Lunar_Lander_DQN.ipynb) | **RL Notebook** | PyTorch, Gymnasium (`LunarLander-v3`) | Reinforcement Learning agent solving spacecraft landings with deep networks. |
| [🎬 Movie Recommender](file:///C:/Users/dhanu/Downloads/MP_Online_AIML-main/MP_Online_AIML-main/Movie_Recommendation_System.ipynb) | **ML Notebook** | Scikit-Learn (TF-IDF, SVD), Cosine Similarity | Recommendation system matching user-item ratings and similarity structures. |
| [🐯 Wildlife Face Recog.](file:///C:/Users/dhanu/Downloads/MP_Online_AIML-main/MP_Online_AIML-main/Wildlife_Face_Recognition.ipynb) | **DL Transfer** | MobileNetV2, Keras, pandas, PIL | Transfer learning pipeline identifying individual wild Amur Tigers. |

---

## 🌟 Featured Applications

### 1. 🧠 AI Quiz Game (Streamlit + Firebase + Gemini AI)
A gamified Streamlit dashboard that adapts quiz difficulties based on user input accuracy.
* **Features:** Google Gemini API adaptively changes question complexity (Easy, Medium, Hard); Firebase Firestore logs live user scoring; Matplotlib visualizes accuracy trends.
* **Launch:**
  ```bash
  cd AI-Quiz-Game
  pip install -r requirements.txt
  streamlit run app.py
  ```

### 2. 🤖 Local RAG Chatbot (FastAPI + Hugging Face)
A document search-and-chat interface running 100% locally on consumer hardware.
* **Features:** Hugging Face `sentence-transformers` for offline embeddings; FAISS for indexing; local `google/flan-t5-base` LLM for context-grounded Q&A.
* **Launch:**
  ```bash
  cd rag_chatbot/backend
  pip install -r requirements.txt
  uvicorn main:app --reload --port 8000
  ```
  Then double-click `rag_chatbot/frontend/index.html` to open the GUI in your browser.

---

## 🔬 Reinforcement Learning & Deep Learning Highlights

### 🕹️ Gymnasium RL Agent Training
* **Lunar Lander (`Lunar_Lander_DQN.ipynb`):** Implements a PyTorch DQN agent utilizing a Replay Buffer and target networks to land a spacecraft successfully in Gym's continuous environment.
* **CartPole (`Cart_Pole RL agent Traning/cartpole_dqn.ipynb`):** Traditional control task solved via a PyTorch-based Deep Q-Network, complete with generated animations showing agent behaviors.

### 🖼️ Computer Vision & Transfer Learning
* **Wildlife Recognition (`Wildlife_Face_Recognition.ipynb`):** Automates identification of rare individual tigers by freezing pre-trained MobileNetV2 convolutional backbones and training classification layers on the Amur Tiger dataset.
* **Medical MRI Classification (`Cancer_Detection.ipynb`):** A customized CNN stack engineered to segment and identify brain tumor tissue on clinical MRI data.

---

## 👩‍💻 Author
**Dhanuj Vardhan Goyal**  
*B.Tech CSE (AI & ML)*  
* GitHub: [@dhanujvardhan](https://github.com/dhanujvardhan)
