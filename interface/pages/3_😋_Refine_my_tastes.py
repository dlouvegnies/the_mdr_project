import streamlit as st
from interface.news_page import display_learning

if 'user_id' not in st.session_state:
    st.info("You are not logged in. Please log in or sign up to access this feature.")

    if st.button("Log In"):
        st.write('<meta http-equiv="refresh" content="0;URL=http://localhost:8501/Log_in">', unsafe_allow_html=True)

    if st.button("Sign Up"):
        st.write('<meta http-equiv="refresh" content="0;URL=http://localhost:8501/Sign_up">', unsafe_allow_html=True)

    st.stop()
else:
    display_learning(st.session_state.user_id)
