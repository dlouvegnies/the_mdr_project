import streamlit as st

from news_page import add_logo


def main():
    add_logo()
    if 'username' in st.session_state:
        st.success("Raph")
    else:
        st.error("Mathieu")

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
