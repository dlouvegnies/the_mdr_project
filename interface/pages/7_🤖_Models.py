import streamlit as st

st.subheader("Select a model that fits your needs")

models = st.radio('Select your model', ('Auto',
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
elif models == 'TFIDF Vectorizer & NearestNeighbors':
    st.session_state['model'] = 'tfidf'
    st.session_state['index'] = 1
elif models == 'CamemBERT & Cosine Similarity':
    st.session_state['model'] = 'cosine'
    st.session_state['index'] = 2
elif models == 'CamemBERT & Jaccard Similarity':
    st.session_state['model'] = 'jaccard'
    st.session_state['index'] = 3
elif models == 'CamemBERT & Euclidean Distance':
    st.session_state['model'] = 'euclidean'
    st.session_state['index'] = 4
elif models == 'CamemBERT & Manhattan Distance':
    st.session_state['model'] = 'manhattan'
    st.session_state['index'] = 5
