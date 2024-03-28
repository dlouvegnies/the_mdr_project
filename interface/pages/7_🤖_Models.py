import streamlit as st
from account import clean_cache



if 'user_id' not in st.session_state:
    st.info("You are not logged in. Please log in or sign up to access this feature.")

    if st.button("Log In"):
        st.write('<meta http-equiv="refresh" content="0;URL=http://localhost:8501/Log_in">', unsafe_allow_html=True)

    if st.button("Sign Up"):
        st.write('<meta http-equiv="refresh" content="0;URL=http://localhost:8501/Sign_up">', unsafe_allow_html=True)

    st.stop()
else:
    st.title("🤖 Models")

    models = st.radio('Select a model that fits your needs', ('Auto',
                                        'TFIDF Vectorizer & NearestNeighbors',
                                        'CamemBERT & Cosine Similarity',
                                        'CamemBERT & Jaccard Similarity',
                                        'CamemBERT & Euclidean Distance',
                                        'CamemBERT & Manhattan Distance'),
                    index=st.session_state.index)

    st.success(f'{models} selected')

    if models == 'Auto':
        st.session_state['model'] = 'cosine'
        st.session_state['index'] = 0
        clean_cache()
    elif models == 'TFIDF Vectorizer & NearestNeighbors':
        st.session_state['model'] = 'tfidf'
        st.session_state['index'] = 1
        clean_cache()
    elif models == 'CamemBERT & Cosine Similarity':
        st.session_state['model'] = 'cosine'
        st.session_state['index'] = 2
        clean_cache()
    elif models == 'CamemBERT & Jaccard Similarity':
        st.session_state['model'] = 'jaccard'
        st.session_state['index'] = 3
        clean_cache()
    elif models == 'CamemBERT & Euclidean Distance':
        st.session_state['model'] = 'euclidean'
        st.session_state['index'] = 4
        clean_cache()
    elif models == 'CamemBERT & Manhattan Distance':
        st.session_state['model'] = 'manhattan'
        st.session_state['index'] = 5
        clean_cache()
