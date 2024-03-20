import streamlit as st
import requests
from datetime import date
import re
from ml_logic.params import USER_ID

def fetch_news_to_learn(user_id):
    api_url = "http://127.0.0.1:8000/get_one_news_to_learn"
    params = {'user_id': user_id}

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from API. Status code: {response.status_code}")
        return None

def save_learning_feedback(news, feedback, user_id):
    api_url = "http://127.0.0.1:8000/save_one_learning"
    today_date = date.today().strftime("%Y-%m-%d")

    data = {
        "review_id": [1],
        "user_id": [user_id],
        "news_id": [news['news_id']['0']],
        "like_the_news": [feedback],
        "good_recommendation": [None],
        "updated_date": [today_date]
    }

    response = requests.post(api_url, json=data)
    if response.status_code == 200:
        pass
    else:
        st.error(f"Failed save data from API. Status code: {response.status_code}")
    return response

def clean_html_tags(text_html):
    texte_sans_html = re.sub(r'<[^>]+>', '', str(text_html))
    return texte_sans_html

def show_news(data):
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

def main():
    st.title("THE MDR PROJECT")

    data = fetch_news_to_learn(USER_ID)
    if data:
        show_news(data)

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

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ("Selection", "Recommendations"))

    if selection == "Selection":
        st.sidebar.write("You're viewing selected articles.")
        

    elif selection == "Recommendations":
        st.sidebar.write("You're viewing recommendations.")


if __name__ == "__main__":
    main()
