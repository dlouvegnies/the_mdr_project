import streamlit as st
from interface.news_page import display_learning

display_learning(st.session_state.user_id)
