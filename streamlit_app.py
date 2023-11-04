import streamlit as st
from google.oauth2 import service_account
from PIL import Image

import io
import os

# Imports the Google Cloud client library
from google.cloud import vision

from paddleocr import PaddleOCR

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
            image_context={'language_hints': ['ja']}
        )

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

def test_paddleocr():

    ocr = PaddleOCR(use_angle_cls=True, use_gpu=False, lang="japan")

    img_path = './images/4565.0.jpg'
    result = ocr.ocr(img_path, cls=True)[0]

    for line in result:
        print(line)

#where_req = ('first_color = True',)
#print(' AND '.join(where_req))

# image = Image.open('./app/static/logo2.png')
#st.image(image)

test_gcv()
test_paddleocr()
