import streamlit as st
import requests
from datetime import datetime
import os
from params import SERVICE_URL, MODE, LOCAL_URL
from news_page import add_logo


base_url = SERVICE_URL if MODE == 'SERVICE' else LOCAL_URL

def login_page():
    st.title("🧑‍💻 Login")
    add_logo()
    # Formulaire de connexion
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        api_url = os.path.join(base_url, 'login')
        data = {'username': username,
                  'password': password}
        response = requests.post(api_url, json=data)

        if response.status_code == 200:
            data_received = response.json()
            st.success(f"Welcome {data_received['result']['username']['0']}, you are logged! 🫡")
            st.session_state['user_id'] = data_received['result']['user_id']['0']
            st.session_state['username'] = data_received['result']['username']['0']
            st.session_state['model'] = 'cosine'
            st.session_state['index'] = 0
        else:
            st.error(f"Failed to login from API. Status code: {response.status_code}")
            return None

# Fonction pour la page d'inscription
def signup_page():
    st.title("📄 Sign Up")
    add_logo()
    # Formulaire d'inscription
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        api_url = os.path.join(base_url, 'signup')
        data = {'username': username,
                  'password': password}
        response = requests.post(api_url, json=data)

        if response.status_code == 200:
            st.success(f"Welcome {username}, you are sign up! 🫡")


        else:
            st.error(f"Failed to signup from API. Status code: {response.status_code}")
            return None

def clean_cache():
    api_url = os.path.join(base_url, 'clear_one_user_cache')
    params = {'user_id': st.session_state['user_id']}

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to clear cache. Status code: {response.status_code}")
        return None
