# 💰 AI Expense Tracker

An AI-powered expense tracking web app that understands **natural language** (text or voice) and automatically converts it into structured expense data — built with Python, Streamlit, and Google Gemini.

## ✨ Features

- **Natural language input** — type or speak your expense like *"200 rupees on chai and 500 on uber"*, and the AI extracts amount, category, and description automatically
- **Voice input** — record your expense using your microphone; no typing needed
- **Multiple expenses at once** — mention several expenses in a single sentence, and each gets logged separately
- **User authentication** — signup/login system with hashed passwords (SQLite)
- **Per-user data isolation** — each user only sees their own expenses
- **Auto-categorization** — expenses are sorted into categories (Food, Travel, Shopping, Bills, Entertainment, Other)
- **Live summary** — total spend and category-wise breakdown, updated in real time
- **Export data** — download your expenses as CSV or Excel (.xlsx)

## 🛠️ Tech Stack

- **Frontend/Backend:** Python, Streamlit
- **AI Model:** Google Gemini API (`google-genai`)
- **Database:** SQLite (user accounts), CSV (expense records)
- **Other libraries:** pandas, openpyxl

## 🚀 How It Works

1. User logs in or signs up
2. User types or speaks an expense in natural language
3. The Gemini API parses the input and returns structured JSON (amount, category, description)
4. The app saves each expense to a CSV file, tagged with the logged-in user's username
5. A live dashboard shows totals, category breakdowns, and a full expense table
6. Users can export their data as CSV or Excel anytime

## 📦 Running Locally

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/expense-tracker.git
cd expense-tracker

# Install dependencies
pip install streamlit google-genai pandas openpyxl

# Add your Gemini API key
# Create a file: .streamlit/secrets.toml
# Add this line inside it:
# GEMINI_API_KEY = "your-api-key-here"

# Run the app
streamlit run web1.py
```

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com/).

## 🔒 Security Notes

- Passwords are hashed (SHA-256) before storing — never stored in plain text
- API keys are kept in `.streamlit/secrets.toml`, which is excluded from version control via `.gitignore`
- Each user can only view their own expense data

## 📌 Future Improvements

- Migrate from CSV to a proper relational database (PostgreSQL) for scalability
- Add expense editing/deletion
- Add date-range filters and spending charts
- Deploy as a Progressive Web App (PWA) for mobile use

## 📄 License

This project is open source and available for learning purposes.
