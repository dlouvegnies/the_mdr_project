import streamlit as st
from interface.news_page import display_recommendation

st.write(st.session_state["user_id"])
display_recommendation(st.session_state.user_id)
