import streamlit as st
from PIL import Image

#where_req = ('first_color = True',)
#print(' AND '.join(where_req))

st.markdown("./app/static/logo.png")
st.markdown("""
    <style>
    .my-text {
        color: white;
        font-size: 24px;
        background-color: #008080;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    <p class='my-text'>Hello World!<br>
    <img src="./app/static/logo.png" height="150" width="150" style="vertical-align:middle;"></p>
    """, unsafe_allow_html=True)
image = Image.open('./app/static/logo.png')
st.image(image)
