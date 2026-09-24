import streamlit as st
from supabase import create_client
import hashlib
import random

# --- Supabase Connection ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def suggest_usernames(base_username, count=3):
    suggestions = []
    attempts = 0

    while len(suggestions) < count and attempts < 20:
        attempts += 1
        candidate = f"{base_username}{random.randint(1, 999)}"
        existing = supabase.table("users").select("username").eq("username", candidate).execute()
        if not existing.data:
            suggestions.append(candidate)

    return suggestions


def signup_user(username, password):
    # Pehle check karo username already hai ya nahi
    existing = supabase.table("users").select("username").eq("username", username).execute()

    if existing.data:
        suggestions = suggest_usernames(username)
        return False, "Ye username already liya hua hai.", suggestions

    supabase.table("users").insert({
        "username": username,
        "password_hash": hash_password(password)
    }).execute()

    return True, "Account ban gaya! Ab login karo.", []


def login_user(username, password):
    result = supabase.table("users").select("password_hash").eq("username", username).execute()

    if not result.data:
        return False

    stored_hash = result.data[0]["password_hash"]
    return stored_hash == hash_password(password)