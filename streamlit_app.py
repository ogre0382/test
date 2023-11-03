import streamlit as st
import sqlite3
from PIL import Image

conn = sqlite3.connect('./static/TEST.db')

cur = conn.cursor()  # カーソルを作成
cur.execute('CREATE TABLE IF NOT EXISTS persons(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING)')  # tableを作成する指示

conn.commit()  # commit()した時点でDBファイルが更新されます
conn.close()

st.image('./static/logo2.png')
st.image('./static/gameset2.png')
