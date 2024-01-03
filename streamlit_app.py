import easyocr
import io
import os
import streamlit as st
from google.cloud import vision # Imports the Google Cloud client library
from google.oauth2 import service_account
from icecream import ic
from PIL import Image

# Google CloudのCloud Vision APIで画像から日本語の文字抽出をしてみた
# https://dev.classmethod.jp/articles/google-cloud_vision-api/
def test_gcv():
    # Instantiates a client
    credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
    client = vision.ImageAnnotatorClient(credentials=credentials)

    # The name of the image file to annotate
    file_name = os.path.abspath('./images/4565.0.jpg')

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # Performs label detection on the image file
    response =  client.document_text_detection(
            image=image,
            image_context={'language_hints': ['en']}
        )
    
    print(response)

    # レスポンスからテキストデータを抽出
    output_text = ''
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    output_text += ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                output_text += '\n'
    print(output_text)
    st.write(output_text)

# pythonライブラリEasyOCRをWindowsにインストールする
# https://qiita.com/1_MCZ_1/items/3870714ebca9be8d9afe
def test_easyocr():
    reader = easyocr.Reader(['en'])#日本語：ja, 英語：en
    result = reader.readtext('./images/4565.0.jpg')

    for text in result:
        print(text)
        st.write(text)

#where_req = ('first_color = True',)
#print(' AND '.join(where_req))

# image = Image.open('./app/static/logo2.png')
#st.image(image)

def test_cpu_count():
    ic(os.cpu_count())
    ic(len(os.sched_getaffinity(0)) )

#test_gcv()
#test_easyocr()
test_cpu_count()
