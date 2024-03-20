import streamlit as st
import requests
import re


def fetch_data():
    user_id = 3
    url = f"http://127.0.0.1:8000/get_one_news_to_learn?user_id={user_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from API. Status code: {response.status_code}")
        return None

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

    data = fetch_data()
    if data:
        show_news(data)

        col1, col2 = st.columns(2)
        with col1:
            thumb_up = st.button("👍 I'm interested")
        with col2:
            thumb_down = st.button("👎 I'm not interested")

        if thumb_up:
            st.success("You were interested in this news.")

        elif thumb_down:
            st.error("You weren't interested in this news.")



if __name__ == "__main__":
    main()
