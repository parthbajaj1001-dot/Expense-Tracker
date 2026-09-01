import streamlit as st
from supabase import create_client
import hashlib

# --- Supabase Connection ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def signup_user(username, password):
    # Pehle check karo username already hai ya nahi
    existing = supabase.table("users").select("username").eq("username", username).execute()

    if existing.data:
        return False, "Ye username already liya hua hai."

    supabase.table("users").insert({
        "username": username,
        "password_hash": hash_password(password)
    }).execute()

    return True, "Account ban gaya! Ab login karo."


def login_user(username, password):
    result = supabase.table("users").select("password_hash").eq("username", username).execute()

    if not result.data:
        return False

    stored_hash = result.data[0]["password_hash"]
    return stored_hash == hash_password(password)