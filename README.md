# 🌶️ StreetByte

<img width="1846" height="967" alt="image" src="https://github.com/user-attachments/assets/0bba009a-7fc9-4962-9999-0a240d42c058" />


Welcome to **StreetByte**, your ultimate AI-powered companion for discovering the most mouth-watering street food spots around the city! This web application combines data analytics, machine learning, and natural language processing to serve you the best food recommendations tailored to your city and budget.

---

## ✨ Features

### 🎙️ AI-Powered Sentiment Analysis
We don't just look at simple star ratings. StreetByte employs **VADER Sentiment Analysis** on real customer reviews to figure out how people *actually* feel about a food spot. Vendor badges (Positive/Neutral/Negative) help you see the vibe at a glance!

### 📊 Smart Composite Scoring Engine
Say goodbye to basic sorting! Our custom recommendation engine calculates a `Composite Score` for each street food item based on:
- **🌟 Rating (40%)**: The golden standard of quality.
- **❤️ Sentiment (40%)**: Emotional feedback from real reviews.
- **🔥 Popularity (20%)**: Driven by the raw volume of reviews left by the crowd.

### 💸 Budget-Friendly Filters
Craving something delicious but sticking to a budget? Just enter your maximum budget and your city. StreetByte will ensure you grab the best bites without breaking the bank.

### 🛡️ Built for Security
We take security seriously so you can focus on the food:
- Strict **Rate Limiting** (via Flask-Limiter) to prevent API abuse.
- Complete Server-Side input validation and output sanitisation.
- Robust **Content Security Policy (CSP)** to neutralize XSS attacks.
- Secure environment configuration for sensitive variables.

### ⚡ Lightning Fast & User Friendly
- **Pre-loaded Datasets**: Machine learning data is pre-processed and cached when the app starts, guaranteeing instant first-request gratification.
- **Paginated Results**: Say goodbye to endless scrolling. Browse beautifully paginated food recommendations.
- **Multi-page Architecture**: Distinct, clean HTML views for Home, Results, About, and more!
- **Legacy JSON API**: Built-in REST endpoints (`/api/v1/recommend`, `/api/v1/cities`) for seamless external integrations.

---

## 🛠️ Technology Stack

- **Backend Development**: Python 3.x, Flask
- **Data Science**: Pandas, NumPy, Scikit-Learn
- **Natural Language Processing (NLP)**: VADER Sentiment Analysis
- **Security & Limits**: Flask-Limiter, python-dotenv
- **Frontend**: HTML5, CSS3, Jinja2 Templates

---

## 🚀 Getting Started

Follow these instructions to get your local copy up and running, so you can start hunting for your next great meal!

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your system.

### 2. Installation
Clone the repository and install the required packages:

```bash
# Create a virtual environment (optional but recommended)
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup
Before you launch, set up your secure environment keys:
1. Rename `.env.example` to `.env`
2. Open `.env` and configure your `SECRET_KEY` and any other required settings.

### 4. Run the App!
Start up the engine:

```bash
python run.py
```

Look out for the terminal message: `✅ Dataset loaded and scored successfully!`. Open your browser and navigate to `http://localhost:5000` to start exploring.

---

## 🤝 Contributing

Got a killer street food spot to add, or an idea to improve the scoring engine? Contributions are always welcome! Pull requests are encouraged. 

---

**Bon Appétit!** 🍔🌮🍜 Let StreetByte guide you to food paradise!
