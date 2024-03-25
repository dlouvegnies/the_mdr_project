import streamlit as st
import requests
from datetime import datetime
import re
import os
#from ml_logic.params import SERVICE_URL, MODE, LOCAL_URL

from interface.news_page import display_learning, display_recommendation
from interface.account import login_page, signup_page

MODE="SERVICE"
SERVICE_URL="https://mdr-gzqmj6mx3q-ew.a.run.app"
LOCAL_URL = ""

base_url = SERVICE_URL if MODE == 'SERVICE' else LOCAL_URL

def main():
    st.sidebar.markdown(f"""
    # The MDR Project
    """)

    st.title("THE MDR PROJECT 🤣")

    st.subheader("Welcome to the best recommendation system 🤗")

    st.subheader("Our team is absolutely beautiful 😍")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.title("M")
        st.image("Mathieu.jpeg")
    with col2:
        st.title("D")
        st.image("Denis.jpeg")
    with col3:
        st.title("R")
        st.image("Raphael.jpeg")



if __name__ == "__main__":
    main()
