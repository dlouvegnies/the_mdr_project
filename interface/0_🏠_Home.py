import streamlit as st

def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://cdn.discordapp.com/attachments/1008571086411145308/1222491584344358912/raphael_1993_un_logo_pour_notre_projet_en_data_science_qui_a_po_c0e9313d-77b3-4288-be0e-ac511476ebd5.png?ex=66166902&is=6603f402&hm=2a1e4a2799df81f176856e70255758aa0161b88b8d79be67a106e81804a2375b&);
                background-repeat: no-repeat;
                padding-top: 120px;
                background-position: 60px 20px;
                background-size: contain;
                max-width: 330px;
                max-height: 200px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "The MDR Project";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def main():
    add_logo()
    if 'username' in st.session_state:
        st.sidebar.write(st.session_state.username)
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
