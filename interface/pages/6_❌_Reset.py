import streamlit as st
from news_page import reset_user_profile


st.title("Reset all my profile")
st.error("Are you sure you want to delete all information from your profile? This action is irreversible.")
popup_button = st.button("Reset", type='primary')
if popup_button:
    reset_user_profile(st.session_state['user_id'])
    st.success("Reset done")
