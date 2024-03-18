import streamlit as st
import pandas as pd

# User credentials
USER_CREDENTIALS = {
    "user1": "password1",
    "user2": "password2"
}

# Create a sample dataframe
data = {
    'Title': ['BRUNO LE MAIRE ESTIME QUE LE PLEIN EMPLOI EST INATTEIGNABLE À "MODÈLE SOCIAL CONSTANT"', 'Title 2', 'Title 3'],
    'Image': ['https://upload.wikimedia.org/wikipedia/commons/8/86/Bruno_Le_Maire_in_2022.jpg', 'https://example.com/image2.jpg', 'https://example.com/image3.jpg'],
    'Description': ['''La promesse d'Emmanuel Macron de parvenir au plein emploi en 2027 a du plomb dans l'aile. Invité ce lundi sur France Inter, Bruno Le Maire s'est lui-même montré sceptique quant à la capacité de l'exécutif à atteindre cet objectif. "Nous n'y arriverons pas à modèle social constant", a assuré le ministre de l'Économie.
                    Je regarde ce qu'il s'est passé depuis plusieurs décennies. Le plein emploi en France, c'est 7%. Dans les autres pays développés, c'est 5%. Donc, il faut s'interroger, se demander pourquoi l'écart est de deux points entre le plein emploi en France et le plein emploi dans les autres pays", a-t-il déclaré.''', 'Description of news 2', 'Description of news 3'],
    'Link': ['https://www.bfmtv.com/economie/emploi/bruno-le-maire-estime-que-le-plein-emploi-est-inatteignable-a-modele-social-constant_AV-202403180309.html', 'https://example.com/link2', 'https://example.com/link3']
}
df = pd.DataFrame(data)

# Index to track the current news
index = 0

# Function to show news
def show_news(index):
    st.subheader('News 📰')
    st.image(df['Image'][index], width=300)  # Adjust width as needed
    st.write(f"Title: {df['Title'][index]}")
    st.write("Description:")
    st.write(df['Description'][index])
    st.write("Link:")
    st.write(df['Link'][index])

# Function to authenticate user
def authenticate(username, password):
    if username in USER_CREDENTIALS:
        if USER_CREDENTIALS[username] == password:
            return True
    return False

# Main function
def main():
    st.title("User Authentication")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.success("Login successful!")
            st.title("THE MDR PROJECT")
            st.markdown("---")
            st.write("")
            show_news(index)

            col1, col2 = st.columns(2)
            with col1:
                thumb_up = st.button("👍 I'm interested")
            with col2:
                thumb_down = st.button("👎 I'm not interested")

            if thumb_up:
                st.success("You were interested in this news.")
            elif thumb_down:
                st.error("You weren't interested in this news.")
        else:
            st.error("Authentication failed. Please try again.")

# Run the app
if __name__ == "__main__":
    main()
