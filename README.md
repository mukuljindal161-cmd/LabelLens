# 🏷️ LabelLens

LabelLens is an AI-powered product label analyzer that uses Gemini to analyze product labels and explain ingredients, nutrition, allergens, additives, and other important information. Users can ask follow-up questions and send the final analysis to their email.

## 🚀 Run Locally

### 1. Clone the repository
```bash
git clone [<your-github-repo-url>](https://github.com/mukuljindal161-cmd/LabelLens)
cd LabelLens
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

Activate it:

Windows:
```bash
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add secrets
Create:

.streamlit/secrets.toml

Add:

GEMINI_API_KEY = "your-gemini-api-key"
GMAIL_ADDRESS = "your-gmail@gmail.com"
GMAIL_APP_PASSWORD = "your-gmail-app-password"

### 5. Run the app
streamlit run app.py

Open the local URL shown in the terminal.


**Note:** Never commit `.streamlit/secrets.toml` to GitHub.

## Project Status

**Status:** 🚀 Completed

👨‍💻 Developer
Mukul Jindal

GitHub: https://github.com/mukuljindal161-cmd

LinkedIn: https://www.linkedin.com/in/mukuljindal07/

⭐ Feel free to explore and share your feedback!
