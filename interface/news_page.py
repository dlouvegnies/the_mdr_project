import streamlit as st
import requests
from datetime import datetime
import re
import os
from params import SERVICE_URL, MODE, LOCAL_URL


base_url = SERVICE_URL if MODE == 'SERVICE' else LOCAL_URL

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

def fetch_news_to_evaluate_with_bert(user_id, method):
    api_url = os.path.join(base_url, 'get_one_reco_by_bert')
    params = {'user_id': user_id, 'method': method}

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
        #"review_id": [1], NEEDED FOR BQ
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
        #"review_id": [1], NEEDED FOR BQ
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
        st.write(f"**News ID:** {news['news_id']}")
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


def display_learning(user_id):
    st.title("THE MDR PROJECT")

    data = fetch_news_to_learn(user_id)
    if data:
        show_random_news(data)

        col1, col2 = st.columns(2)
        with col1:
            thumb_up = st.button("👍 I'm interested")
        with col2:
            thumb_down = st.button("👎 I'm not interested")

        if thumb_up:
            st.success("You were interested in this news.")
            test = save_learning_feedback(data, True, user_id)
            st.write(test)

        elif thumb_down:
            st.error("You weren't interested in this news.")
            save_learning_feedback(data, False, user_id)


def display_recommendation(user_id):
    st.title("THE MDR PROJECT")
    if st.session_state.model == 'tfidf':
        data = fetch_news_to_evaluate(user_id)
    else:
        data = fetch_news_to_evaluate_with_bert(user_id, st.session_state['model'])
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
            test = save_recommendation_feedback(news, True, user_id)
            st.write(test)

        elif thumb_down:
            st.error("You weren't interested in this news.")
            save_recommendation_feedback(news, False, user_id)

def reset_user_profile(user_id):
    api_url = os.path.join(base_url, 'reset')
    params = {'user_id': user_id}

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from API. Status code: {response.status_code}")
        return None
