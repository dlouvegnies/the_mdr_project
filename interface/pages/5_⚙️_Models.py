import streamlit as st

st.subheader("Select a model that fits your needs")

models = st.radio('Select your model', ('Auto',
                                     'TFIDF Vectorizer & NearestNeighbors',
                                     'CamemBERT & Cosine Similarity',
                                     'CamemBERT & Jaccard Similarity',
                                     'CamemBERT & Euclidean Distance',
                                     'CamemBERT & Manhattan Distance'))

st.success(f'{models} selected')

if models == 'Auto':
    st.session_state['model'] = 'cosine'
elif models == 'TFIDF Vectorizer & NearestNeighbors':
    st.session_state['model'] = 'tfidf'
elif models == 'CamemBERT & Cosine Similarity':
    st.session_state['model'] = 'cosine'
elif models == 'CamemBERT & Jaccard Similarity':
    st.session_state['model'] = 'jaccard'
elif models == 'CamemBERT & Euclidean Distance':
    st.session_state['model'] = 'euclidean'
elif models == 'CamemBERT & Manhattan Distance':
    st.session_state['model'] = 'manhattan'
