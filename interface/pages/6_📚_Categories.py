import streamlit as st
import pandas as pd
import requests

import os
from params import SERVICE_URL, MODE, LOCAL_URL


base_url = SERVICE_URL if MODE == 'SERVICE' else LOCAL_URL

def get_categories(user_id):
    api_url = os.path.join(base_url, 'get_one_user_category')
    params = {'user_id': user_id}

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from API. Status code: {response.status_code}")
        return None

def save_user_categories_one(user_id,category_id,on):
    api_url = os.path.join(base_url, 'save_user_category')
    params = {'user_id': st.session_state.user_id,'category_id': category_id,'on': on}

    response = requests.post(api_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from API. Status code: {response.status_code}")
        return None



if 'user_id' not in st.session_state:
    st.info("You are not logged in. Please log in or sign up to access this feature.")

    if st.button("Log In"):
        st.write('<meta http-equiv="refresh" content="0;URL=http://localhost:8501/Log_in">', unsafe_allow_html=True)

    if st.button("Sign Up"):
        st.write('<meta http-equiv="refresh" content="0;URL=http://localhost:8501/Sign_up">', unsafe_allow_html=True)

    st.stop()
else:

    st.subheader("Select the categories you like")
    df_categories = pd.DataFrame(get_categories(st.session_state.user_id))
    #print(df_categories)
    # Afficher les cases à cocher pour chaque catégorie
    st.write("Sélectionnez les catégories :")


    for index, row in df_categories.iterrows():
        category_id = row['category_id']
        categorie = row['cat_name']
        user_id = row['user_id']

        if user_id!='':
            checkbox_value = st.checkbox(categorie.capitalize(), key=index,value=True)
        else:
            checkbox_value = st.checkbox(categorie.capitalize(), key=index,value=False)

        if checkbox_value:
            #Coché
            save_user_categories_one(user_id,category_id,1)
        else:
            #décochée
            save_user_categories_one(user_id,category_id,0)
