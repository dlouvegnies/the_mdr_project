import streamlit as st
import requests
from datetime import datetime
import re
import os
from ml_logic.params import USER_ID, SERVICE_URL, MODE, LOCAL_URL

from interface.news_page import display_learning, display_recommendation
from interface.account import login_page, signup_page

base_url = SERVICE_URL if MODE == 'SERVICE' else LOCAL_URL

def main():
    st.sidebar.markdown(f"""
    # The MDR Project
    """)
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ("Login", "Sign Up"))

    if selection == "Login":
        login_page()
    elif selection == "Sign Up":
        signup_page()

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ("Selection", "Recommendations"))

    if selection == "Selection":
        st.sidebar.write("You're viewing selected articles.")

        display_learning()


    elif selection == "Recommendations":
        st.sidebar.write("You're viewing recommendations.")

        display_recommendation()

if __name__ == "__main__":
    main()
