import streamlit as st
import requests
from datetime import datetime
import re
import os
from ml_logic.params import USER_ID, SERVICE_URL, MODE, LOCAL_URL

base_url = SERVICE_URL if MODE == 'SERVICE' else LOCAL_URL

def login_page():
    st.title("Login")
    # Formulaire de connexion
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        api_url = os.path.join(base_url, 'login')
        data = {'username': username,
                  'password': password}
        response = requests.post(api_url, json=data)

        if response.status_code == 200:
            st.write("GOOOD")
            pass
        else:
            st.error(f"Failed to login from API. Status code: {response.status_code}")
            return None

# Fonction pour la page d'inscription
def signup_page():
    st.title("Sign Up")
    # Formulaire d'inscription
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        api_url = os.path.join(base_url, 'signup')
        data = {'username': username,
                  'password': password}
        response = requests.post(api_url, params=data)

        if response.status_code == 200:
            # AFFICHER LA PAGE TU ES INSCRIT C'est bon
            pass
        else:
            st.error(f"Failed to signup from API. Status code: {response.status_code}")
            return None
