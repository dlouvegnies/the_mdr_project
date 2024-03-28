import streamlit as st
from news_page import reset_user_profile
from account import clean_cache


if 'user_id' not in st.session_state:
    st.info("You are not logged in. Please log in or sign up to access this feature.")

    if st.button("Log In"):
        st.write('<meta http-equiv="refresh" content="0;URL=http://localhost:8501/Log_in">', unsafe_allow_html=True)

    if st.button("Sign Up"):
        st.write('<meta http-equiv="refresh" content="0;URL=http://localhost:8501/Sign_up">', unsafe_allow_html=True)

    st.stop()
else:
    st.title("♻️ Reset all my profile")
    st.error("Are you sure you want to delete all information from your profile? This action is irreversible.")
    popup_button = st.button("Reset", type='primary')
    if popup_button:
        reset_user_profile(st.session_state['user_id'])
        clean_cache()
        st.success("Reset done")
