import streamlit as st
from google import genai
from google.genai import types
import json
import csv
import os
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
from auth import init_db, signup_user, login_user

init_db()

st.set_page_config(page_title="Expense Tracker", page_icon="💰")

# ========================================================
# PART 1: LOGIN / SIGNUP (Ye sabse pehle chalega)
# ========================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("💰 AI Expense Tracker")
    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if login_user(login_username, login_password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = login_username
                st.rerun()
            else:
                st.error("Galat username ya password.")

    with tab2:
        signup_username = st.text_input("Naya Username", key="signup_user")
        signup_password = st.text_input("Naya Password", type="password", key="signup_pass")
        if st.button("Signup"):
            if signup_username and signup_password:
                success, message = signup_user(signup_username, signup_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Username aur password dono bharo.")

    st.stop()

# ========================================================
# PART 2: YAHAN SE NEECHE SIRF LOGIN HONE KE BAAD CHALEGA
# ========================================================

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
FILENAME = "expenses.csv"

st.title("💰 AI Expense Tracker")
st.write("Ek ya kai expenses likho ya bolo, AI khud alag-alag samajh lega!")

st.sidebar.write(f"👋 Welcome, **{st.session_state['username']}**")
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.rerun()


# --- Function 1: Text Se Expense(s) Nikalna ---
def extract_expenses(user_text):
    prompt = f"""Tum ek expense tracker assistant ho. User ke message mein ek ya ek se zyada expenses ho sakte hain. Har expense ko alag identify karo aur sabko ek JSON LIST mein return karo, koi extra text nahi, koi markdown backticks nahi.

Format: [{{"amount": number, "category": "Food/Travel/Shopping/Bills/Entertainment/Other", "description": "short text"}}, ...]

Agar sirf ek hi expense ho, tab bhi ek-item wali list return karo.

User ka message: {user_text}"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


# --- Function 2: Audio Se Expense(s) Nikalna ---
def extract_expenses_from_audio(audio_bytes):
    prompt = """Ye audio sunke, ek ya ek se zyada expenses bataye gaye ho sakte hain. Har expense ko alag identify karo aur sabko ek JSON LIST mein return karo, koi extra text nahi, koi markdown backticks nahi.

Format: [{"amount": number, "category": "Food/Travel/Shopping/Bills/Entertainment/Other", "description": "short text"}, ...]

Agar sirf ek hi expense ho, tab bhi ek-item wali list return karo."""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            prompt,
            types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
        ]
    )
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


# --- Function 3: Ek Expense Save Karna (User Ke Naam Ke Saath) ---
def save_expense(expense):
    file_exists = os.path.isfile(FILENAME)
    with open(FILENAME, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Username", "Date", "Amount", "Category", "Description"])
        writer.writerow([
            st.session_state["username"],
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            expense["amount"],
            expense["category"],
            expense["description"]
        ])


# --- Function 4: Multiple Expenses Save Karna ---
def save_multiple_expenses(expense_list):
    for expense in expense_list:
        save_expense(expense)


# --- Function 5: Excel Banana ---
def create_excel(rows, excel_filename):
    df = pd.DataFrame(rows)
    df.to_excel(excel_filename, index=False)

    wb = load_workbook(excel_filename)
    ws = wb.active
    ws.column_dimensions["A"].width = 15  # Username
    ws.column_dimensions["B"].width = 18  # Date
    ws.column_dimensions["C"].width = 12  # Amount
    ws.column_dimensions["D"].width = 15  # Category
    ws.column_dimensions["E"].width = 30  # Description
    wb.save(excel_filename)


# --- UI: Text Se Expense(s) Add Karna ---
st.subheader("⌨️ Type Karke Add Karo")
st.caption("Ek ya kai expenses ek saath likh sakte ho, jaise: '200 chai pe aur 500 uber pe kharch kiye'")

with st.form(key="text_form", clear_on_submit=True):
    user_input = st.text_input("Apna expense likho:", placeholder="jaise: 200 chai pe aur 500 uber pe kharch kiye")
    submitted = st.form_submit_button("Add Expense")

    if submitted and user_input:
        try:
            results = extract_expenses(user_input)
            save_multiple_expenses(results)
            st.success(f"✅ {len(results)} expense(s) save ho gaye!")
            for r in results:
                st.write(f"— ₹{r['amount']} | {r['category']} | {r['description']}")
        except Exception as e:
            st.error(f"❌ Kuch samajh nahi aaya: {e}")


# --- UI: Mic Se Expense(s) Add Karna ---
st.divider()
st.subheader("🎙️ Bol Ke Add Karo")
st.caption("Ek ya kai expenses ek saath bol sakte ho")

audio_value = st.audio_input("Mic se apna expense bolo")

if audio_value:
    audio_bytes = audio_value.getvalue()
    audio_id = hash(audio_bytes)

    if st.session_state.get("last_audio_id") != audio_id:
        st.session_state["last_audio_id"] = audio_id
        try:
            with st.spinner("Sun raha hoon..."):
                results = extract_expenses_from_audio(audio_bytes)
                save_multiple_expenses(results)
            st.success(f"✅ {len(results)} expense(s) save ho gaye!")
            for r in results:
                st.write(f"— ₹{r['amount']} | {r['category']} | {r['description']}")
        except Exception as e:
            st.error(f"❌ Kuch samajh nahi aaya: {e}")


# --- Summary Section (Sirf Is User Ka Data) ---
st.divider()
st.subheader("📊 Summary")

if os.path.isfile(FILENAME):
    total = 0
    category_totals = {}
    user_rows = []

    with open(FILENAME, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Username"] == st.session_state["username"]:
                user_rows.append(row)
                amount = float(row["Amount"])
                total += amount
                category = row["Category"]
                category_totals[category] = category_totals.get(category, 0) + amount

    if user_rows:
        st.metric("Total Kharch", f"₹{total}")

        for cat, amt in category_totals.items():
            st.write(f"**{cat}**: ₹{amt}")

        st.divider()
        st.subheader("📋 Tumhare Saare Expenses")
        st.table(user_rows)

        # --- Download Section ---
        st.divider()
        st.subheader("📥 Data Download Karo")

        col1, col2 = st.columns(2)

        with col1:
            df_csv = pd.DataFrame(user_rows)
            csv_data = df_csv.to_csv(index=False)
            st.download_button(
                label="⬇️ CSV Download Karo",
                data=csv_data,
                file_name="my_expenses.csv",
                mime="text/csv"
            )

        with col2:
            create_excel(user_rows, "my_expenses.xlsx")
            with open("my_expenses.xlsx", "rb") as f:
                st.download_button(
                    label="⬇️ Excel Download Karo",
                    data=f,
                    file_name="my_expenses.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.info("Abhi tak koi expense add nahi hua.")
else:
    st.info("Abhi tak koi expense add nahi hua.")