import streamlit as st
import streamlit.components.v1 as components
from news_page import add_logo

st.title('📽️ Google Slides')
add_logo()
components.iframe(src="https://docs.google.com/presentation/d/e/2PACX-1vSVFTNaLUYn9w4tSECUaNsvhHbOgDBRGgY5duLUV6lXbPeV0nA67YijfZXEr5tR8UOuBJYVhdMweVk1/embed?start=true&loop=false&delayms=60000", height=500)
