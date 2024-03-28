import streamlit as st
import requests
from datetime import datetime
import re
import os
from params import SERVICE_URL, MODE, LOCAL_URL
import pandas as pd


base_url = SERVICE_URL if MODE == 'SERVICE' else LOCAL_URL

mapping_id_to_cat = {
    3: 'technologie',
    4: 'politique',
    5: 'sport',
    6: 'economie',
    8: 'general',
    9: 'emploi',
    11: 'management',
    12: 'presse'
}

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
        st.subheader(f"{data['title']['0']}")
        datetime_obj = datetime.fromisoformat(data['added_date']['0'])
        date_only = datetime_obj.date()
        st.write(f"***{data['source']['0']} - {mapping_id_to_cat[data['category_id']['0']]} - {date_only}***")
        st.write('')
        st.write(clean_html_tags(data['description']['0']))
        st.write('')
        _, col2, _, _, _, _ = st.columns(6)
        with col2:
            if data['image']['0']:
                st.image(data['image']['0'], width=300)
            else:
                st.image("https://cdn.generationvoyage.fr/2020/04/journaux-britanniques-et-am%C3%A9ricains-768x421.jpg",width=400)
        st.write('')
        st.link_button('Click here to see the news', data['link']['0'])
    else:
        st.error("No data available")


def show_recommended_news(news):
        st.subheader(f"{news['title']}")
        datetime_obj = datetime.fromisoformat(news['added_date'])
        date_only = datetime_obj.date()
        st.write(f"***{news['source']} - {mapping_id_to_cat[news['category_id']]} - {date_only}***")
        st.write('')
        st.write(clean_html_tags(news['description']))
        st.write('')
        _, col2, _, _, _, _ = st.columns(6)
        with col2:
            if news['image']:
                st.image(news['image'], width=300)
            else:
                st.image("https://cdn.generationvoyage.fr/2020/04/journaux-britanniques-et-am%C3%A9ricains-768x421.jpg",width=400)
        st.write('')
        st.link_button('Click here to see the news', news['link'])

def display_learning(user_id):
    st.title("👩‍🎓 What I like")
    add_logo()

    if 'previous_news' not in st.session_state:
        st.session_state['previous_news'] = None
    else:
        st.session_state.previous_news = st.session_state.current_news

    data = fetch_news_to_learn(user_id)
    st.session_state['current_news'] = data
    if data:
        show_random_news(data)
        st.write('')
        col1, col2 = st.columns(2)
        with col1:
            thumb_up = st.button("👍 I'm interested")
        with col2:
            thumb_down = st.button("👎 I'm not interested")

        if thumb_up:
            st.success("You were interested in this news.")
            save_learning_feedback(st.session_state.previous_news, True, user_id)

        elif thumb_down:
            st.error("You weren't interested in this news.")
            save_learning_feedback(st.session_state.previous_news, False, user_id)


def display_recommendation(user_id):
    st.title("🤩 What I should like")
    add_logo()

    if 'previous_news' not in st.session_state:
        st.session_state['previous_news'] = None
    else:
        st.session_state.previous_news = st.session_state.current_news

    if st.session_state.model == 'tfidf':
        data = fetch_news_to_evaluate(user_id)
    else:
        data = fetch_news_to_evaluate_with_bert(user_id, st.session_state['model'])


    if data:
        news = next(iter(data.values()))
        st.session_state['current_news'] = news
        show_recommended_news(news)
        st.write('')
        col1, col2 = st.columns(2)
        with col1:
            thumb_up = st.button("👍 I like this recommendation")
        with col2:
            thumb_down = st.button("👎 I don't like this recommendation")

        if thumb_up:
            st.success("You were interested in this news.")
            save_recommendation_feedback(st.session_state.previous_news, True, user_id)

        elif thumb_down:
            st.error("You weren't interested in this news.")
            save_recommendation_feedback(st.session_state.previous_news, False, user_id)



def reset_user_profile(user_id):
    api_url = os.path.join(base_url, 'reset')
    params = {'user_id': user_id}

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from API. Status code: {response.status_code}")
        return None

def search_page():
    st.title("🔍 Search")
    add_logo()
    # Formulaire d'inscription
    keywords = st.text_area('Find a news from keywords')
    if st.button("Search"):
        api_url = os.path.join(base_url, 'search')
        data = {'keywords': keywords}
        response = requests.post(api_url, json=data)

        if response.status_code == 200:
            data_received = response.json()
            reco_df = pd.DataFrame(data_received['result'])
            st.dataframe(reco_df,
                         column_config={
                        "title": "News title",
                        "description": "Description",
                        "url": st.column_config.LinkColumn("App URL"),
                        "link": st.column_config.LinkColumn(
                        "Link", display_text="Open news"
                        ),
                        "source": "Source"
                        },
                         hide_index=True)
        else:
            st.error(f"Failed to fetch data from API. Status code: {response.status_code}")
            return None

def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://www.louvegnies.com/mdr/Logo-removebg.png);
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
