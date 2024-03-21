import streamlit as st
import requests
from datetime import datetime
import re
import os
from ml_logic.params import USER_ID, SERVICE_URL, MODE, LOCAL_URL

base_url = SERVICE_URL if MODE == 'SERVICE' else LOCAL_URL
def login_page():
    st.title("Login")
    # Formulaire de connexion
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Logique pour vérifier les informations d'identification et effectuer la connexion
        pass

# Fonction pour la page d'inscription
def signup_page():
    st.title("Sign Up")
    # Formulaire d'inscription
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        # Logique pour créer un nouveau compte utilisateur
        pass

# Fonction principale pour gérer la navigation entre les pages
def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ("Login", "Sign Up"))

    if selection == "Login":
        login_page()
    elif selection == "Sign Up":
        signup_page()

if __name__ == "__main__":
    main()


def fetch_news_to_learn(user_id):
    api_url = os.path.join(base_url, 'get_one_news_to_learn')
    params = {'user_id': user_id}

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from API. Status code: {response.status_code}")
        return None

def fetch_news_to_evaluate(user_id):
    api_url = os.path.join(base_url, 'get_one_news_to_evaluate')
    params = {'user_id': user_id}

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from API. Status code: {response.status_code}")
        return None


def save_learning_feedback(news, feedback, user_id):
    api_url = os.path.join(base_url, 'save_one_learning')
    today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "review_id": [1],
        "user_id": [user_id],
        "news_id": [news['news_id']['0']],
        "like_the_news": [feedback],
        "good_recommendation": [None],
        "updated_date": [today_date]
    }
    print(data)
    response = requests.post(api_url, json=data)
    if response.status_code == 200:
        pass
    else:
        st.error(f"Failed save data from API. Status code: {response.status_code}")
    return response

def save_recommendation_feedback(news, feedback, user_id):
    api_url = os.path.join(base_url, 'save_one_evaluation')
    today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "review_id": [1],
        "user_id": [user_id],
        "news_id": [news['news_id']],
        "like_the_news": [None],
        "good_recommendation": [feedback],
        "updated_date": [today_date]
    }
    print(data)
    response = requests.post(api_url, json=data)
    if response.status_code == 200:
        pass
    else:
        st.error(f"Failed save data from API. Status code: {response.status_code}")
    return response

def clean_html_tags(text_html):
    texte_sans_html = re.sub(r'<[^>]+>', '', str(text_html))
    return texte_sans_html


def show_random_news(data):
    if data:
        st.subheader('News 📰')
        st.write(f"**Title:** {data['title']['0']}")
        st.write("**Description:**")
        st.write(clean_html_tags(data['description']['0']))
        st.write("**Link:**")
        st.write(data['link']['0'])
        st.write("**Image:**")
        if data['image']['0']:
            st.image(data['image']['0'], width=300)
        else:
            st.image("https://cdn.generationvoyage.fr/2020/04/journaux-britanniques-et-am%C3%A9ricains-768x421.jpg",width=400)
    else:
        st.error("No data available")


def show_recommended_news(news):
        st.subheader('News 📰')
        st.write(f"**Title:** {news['title']}")
        st.write("**Description:**")
        st.write(clean_html_tags(news['description']))
        st.write("**Link:**")
        st.write(news['link'])
        st.write("**Image:**")
        if news['image']:
            st.image(news['image'], width=300)
        else:
            st.image("https://cdn.generationvoyage.fr/2020/04/journaux-britanniques-et-am%C3%A9ricains-768x421.jpg",width=400)


def display_learning():
    st.title("THE MDR PROJECT")

    data = fetch_news_to_learn(USER_ID)
    if data:
        show_random_news(data)

        col1, col2 = st.columns(2)
        with col1:
            thumb_up = st.button("👍 I'm interested")
        with col2:
            thumb_down = st.button("👎 I'm not interested")

        if thumb_up:
            st.success("You were interested in this news.")
            test = save_learning_feedback(data, True, USER_ID)
            st.write(test)

        elif thumb_down:
            st.error("You weren't interested in this news.")
            save_learning_feedback(data, False, USER_ID)


def display_recommendation():
    st.title("THE MDR PROJECT")

    data = fetch_news_to_evaluate(USER_ID)
    if data:
        news = next(iter(data.values()))
        show_recommended_news(news)

        col1, col2 = st.columns(2)
        with col1:
            thumb_up = st.button("👍 I like this recommendation")
        with col2:
            thumb_down = st.button("👎 I don't like this recommendation")

        if thumb_up:
            st.success("You were interested in this news.")
            test = save_recommendation_feedback(news, True, USER_ID)
            st.write(test)

        elif thumb_down:
            st.error("You weren't interested in this news.")
            save_recommendation_feedback(news, False, USER_ID)


def main():
    st.sidebar.markdown(f"""
    # The MDR Project
    """)

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
