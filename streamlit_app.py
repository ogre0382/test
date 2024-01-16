import cv2
import threading
import time
import easyocr
import io
import logging
import matplotlib.pyplot as plt
import os
#os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import keras_ocr

import re
import string
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
from google.cloud import vision # Imports the Google Cloud client library
from google.oauth2 import service_account
from icecream import ic
from PIL import Image
from streamlit import session_state as ss
from tqdm import tqdm

def init_ss(key,value=None):
    if key not in ss: ss[key] = value

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
    reader = easyocr.Reader(lang_list=['en'], verbose=False)#日本語：ja, 英語：en
    img = cv2.imread('./images/oMhuTTOL0Vc&t=5725s.jpg', 0)
    h,w = img.shape[0],img.shape[1]
    img_btmL = img[int(h*0.6):int(h),int(0):int(w*0.5)]
    txt=''
    for ocr_res in reader.readtext(img_btmL, allowlist='irt'+string.ascii_uppercase, detail=0):
        txt+=ocr_res
    print('test_easyocr: ', re.sub(' ', '', txt))

#where_req = ('first_color = True',)
#print(' AND '.join(where_req))

# image = Image.open('./app/static/logo2.png')
#st.image(image)

def test_cpu_count():
    ic(os.cpu_count())
    ic(len(os.sched_getaffinity(0)) )

#https://qiita.com/Toyo_m/items/992b0dcf765ad3082d0b
#その並列処理待った！　「Python 並列処理」でググったあなたに捧ぐasync, threading, multiprocessingのざっくりとした説明
def write_mail(number):
    print(f"書き込み({number})番目：こんにちは")
    st.write(f"書き込み({number})番目：こんにちは")
    time.sleep(0.03)
    print(f"書き込み({number}番目)：げんきですか？")
    st.write(f"書き込み({number}番目)：げんきですか？")
    time.sleep(0.03)
    print(f"書き込み({number}番目)：さようなら")
    st.write(f"書き込み({number}番目)：さようなら")
    time.sleep(0.03)

def send_mail(number):
    print(f"送付({number}番目)")
    st.write(f"送付({number}番目)")
    time.sleep(5)

def check_response(number):
    hoge=0
    # 無駄な計算
    for i in range(1, 100000000):
        hoge += i/3 + i/5 + i/7 + i/9 + i/11
    print(f"確認OK({number}番目)")
    st.write(f"確認OK({number}番目)")

def task(thread_num):
    write_mail(thread_num)
    send_mail(thread_num)
    check_response(thread_num)

def test_thred():
    ic(threading.active_count())
    start_time=time.time()
    t1 = threading.Thread(target=task, args=(1,))# 引数を与える時はこんな感じで
    t2 = threading.Thread(target=task, args=(2,))
    t3 = threading.Thread(target=task, args=(3,))
    #https://github.com/streamlit/docs/issues/87#issuecomment-1641496741
    #Add documentation about how to use Streamlit with multiple threads. #87
    t1 = add_script_run_ctx(t1)
    t1.start()
    #t1.join()
    t2 = add_script_run_ctx(t2)
    t2.start()
    #t2.join()
    t3 = add_script_run_ctx(t3)
    t3.start()
    #t3.join()
    ic(threading.active_count())
    t1.join()
    t2.join()
    t3.join()
    print(f"かかった時間：{time.time()-start_time}s")
    st.write(f"かかった時間：{time.time()-start_time}s")

def test_bar():
    count=0
    count_end=28
    proc = {'find_game_start':False, 'get_fighter_name':False, 'find_game_end': False, 'get_game_result':False}
    total = 514
    initial = 0
    bar = tqdm(total=total, leave=False, initial=initial)
    my_bar = st.progress(0)
    bar_text = ''
    with st.expander("See results of the image processing"):
        stc = st.columns([5,5])
    for sec in range(initial, total): #range(9820,10005): #range(3364,3960): # range(4325,4775) #ge-gs=30 range(20000,20090) #gs-ge=57
        mess = f"Xk28pn-xRwc:"
        st_bar_text = f"Image processing in progress. Please wait. | {mess} {int(round((sec+1)/total,2)*100)}% ({sec+1}/{total} sec)"
        my_bar.progress((sec+1)/total, text=st_bar_text)
        bar.set_description(bar_text)
        bar.update(1)
        if not proc['find_game_start'] and not proc['get_fighter_name'] and not proc['find_game_end'] and not proc['get_game_result']:
            bar_text = f'{mess} -> count from {count} to {count_end}'
            proc['find_game_start'], count = skip_img_proc(count, count_end)
            if not proc['find_game_start']: continue
        if proc['find_game_start'] and proc['get_fighter_name'] and not proc['find_game_end'] and not proc['get_game_result']:
            proc['find_game_end'], count = skip_img_proc(count, count_end, False)
            bar_text = f'{mess} -> count from {count} to {count_end*2}'
            if not proc['find_game_end']: continue
        if proc['find_game_start'] and not proc['get_fighter_name'] and not proc['find_game_end'] and not proc['get_game_result']:
            bar_text = f'{mess} -> find_game_start'
            proc['get_fighter_name'], count = skip_img_proc(count, count_end+10)
            if not proc['get_fighter_name']: continue
            if proc['find_game_start'] and proc['get_fighter_name'] and not proc['find_game_end'] and not proc['get_game_result']:
                bar_text = f'{mess} -> get_fighter_name'
                count=0
                stc[0].write(sec)
        if proc['find_game_start'] and proc['get_fighter_name'] and proc['find_game_end']and not proc['get_game_result']:
            bar_text = f'{mess} -> find_game_end'
            proc['get_game_result'], count = skip_img_proc(count, count_end+10, False)
            if not proc['get_game_result']: continue
            if proc['find_game_start'] and proc['get_fighter_name'] and proc['find_game_end'] and proc['get_game_result']:
                bar_text = f'{mess} -> get_game_result'
                for key in proc.keys(): proc[key] = False
                count=0
                stc[1].write(sec)
        time.sleep(1)

def skip_img_proc(count, count_end=28, interval=True):
    #time.sleep(1)
    if not interval: count_end*=2
    count+=1
    if count==count_end: return True, count
    else: return False, count

def set_disabled(disabled):
    ss[disabled] = True

def test_btn():
    init_ss('d_resize_btn', False)
    if st.button('Resize the frame(image)', on_click=set_disabled, args=('d_resize_btn',), disabled=ss.d_resize_btn):
        st.button('Ready?')

def test_st_stop():
    name = st.text_input('Name')
    if not name:
        st.warning('Please input a name.')
        st.stop()
    st.success('Thank you for inputting a name.')

def test_st_empty():
    with st.empty():
        for seconds in range(60):
            st.write(f"⏳ {seconds} seconds have passed")
            time.sleep(1)
        st.write("✔️ 1 minute over!")

def test_st_empty2():
    placeholder = st.empty()

    # Replace the placeholder with some text:
    placeholder.text("Hello")

    # Replace the text with a chart:
    placeholder.line_chart({"data": [1, 5, 2, 6]})

    # Replace the chart with several elements:
    # with placeholder.container():
    #     st.write("This is one element")
    #     st.write("This is another")

    # Clear all those elements:
    #placeholder.empty()

def update_slider():
    ss.slider = ss.numeric
def update_numin():
    ss.numeric = ss.slider            

def test_update_slider_numin():
    val = st.number_input('Input', value = 0, key = 'numeric', on_change = update_slider)


    slider_value = st.slider('slider', min_value = 0, 
                            value = val, 
                            max_value = 5,
                            step = 1,
                            key = 'slider', on_change= update_numin)

#"Bad 'setIn' index XX (should be between [0, X])" when using st.experimental_memo in thread #5402
#https://github.com/streamlit/streamlit/issues/5402
def test_add_script_run_ctx():

    #@st.experimental_memo(ttl=1)
    st.cache_data
    def function1(interval):
        interval = interval / 4
        logging.info("sleeping for %s seconds", interval)
        time.sleep(interval)
        logging.info("done sleeping for %s seconds", interval)
        return interval


    def main():
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format)

        threads = []
        for index in range(25):
            x = threading.Thread(target=function1, args=(index,))
            # Hack to remove the following logging messages:
            #    `Thread 'Thread-123': missing ScriptRunContext`
            # see https://github.com/streamlit/streamlit/issues/1326
            add_script_run_ctx(x)
            threads.append(x)
            x.start()

        logging.info("Waiting for threads to finish")
        for thread in threads:
            thread.join()

        logging.info("done")
        st.write("done")

    main()

def test_regexp():
    allowlist='irt'+string.ascii_uppercase
    print(f'[^{allowlist}]')
    
    print(re.sub('[.& ]', '', 'Mr. GAME & WATCH'))

def test_keras_ocr():
    # keras-ocr will automatically download pretrained
    # weights for the detector and recognizer.
    # pipeline = keras_ocr.pipeline.Pipeline()
    
    # Get a set of three example images
    # img = cv2.imread('./images/oMhuTTOL0Vc&t=5725s.jpg', 0)
    # h,w = img.shape[0],img.shape[1]
    # img_btmL = img[int(h*0.6):int(h),int(0):int(w*0.5)]
    # img = keras_ocr.tools.read(img_btmL)
    #img = keras_ocr.tools.read('./images/oMhuTTOL0Vc&t=5725s.jpg')
    # print(type(img))

    # Each list of predictions in prediction_groups is a list of
    # (word, box) tuples.
    # prediction_groups = pipeline.recognize([img.crop((0, h*0.6, w*0.5, h))])

    # Print the predictions
    # txt=''
    # for ocr_res in prediction_groups[0]:
    #     txt+=ocr_res
    # print('test_keras_ocr: ', re.sub(' ', '', txt))


    # keras-ocr will automatically download pretrained
    # weights for the detector and recognizer.
    # pipeline = keras_ocr.pipeline.Pipeline()

    # Get a set of three example images
    # images = [
    #     keras_ocr.tools.read(url) for url in [
    #         'https://upload.wikimedia.org/wikipedia/commons/b/bd/Army_Reserves_Recruitment_Banner_MOD_45156284.jpg',
    #         #'https://upload.wikimedia.org/wikipedia/commons/e/e8/FseeG2QeLXo.jpg',
    #         'https://upload.wikimedia.org/wikipedia/commons/b/b4/EUBanana-500x112.jpg'
    #     ]
    # ]

    # images = [keras_ocr.tools.read('https://upload.wikimedia.org/wikipedia/commons/b/b4/EUBanana-500x112.jpg')]

    # Each list of predictions in prediction_groups is a list of
    # (word, box) tuples.
    # prediction_groups = pipeline.recognize(images)

    # Plot the predictions
    # fig, axs = plt.subplots(nrows=len(images), figsize=(20, 20))
    # for ax, image, predictions in zip(axs, images, prediction_groups):
    #   keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)
    
    # for predictions in prediction_groups:
    #     print(len(predictions))
    #     for predict in predictions:
    #         print(predict[0])
    
    print('message check for keras-ocr')

if __name__ == '__main__':
    #test_gcv()
    test_easyocr()
    #test_cpu_count()
    #test_thread()
    #test_bar()
    #test_btn()
    #test_st_stop()
    #test_st_empty()
    #test_st_empty2()
    #test_update_slider_numin()
    #test_add_script_run_ctx()
    #test_regexp()
    test_keras_ocr()