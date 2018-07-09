import requests
import re
import random
import configparser
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from imgurpython import ImgurClient

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
config = configparser.ConfigParser()
config.read("config.ini")

line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])
client_id = config['imgur_api']['Client_ID']
client_secret = config['imgur_api']['Client_Secret']
album_id = config['imgur_api']['Album_ID']
API_Get_Image = config['other_api']['API_Get_Image']


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # print("body:",body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'

def venue():
    return "National Taiwan University of Science and Technology\n國立台灣科技大學\nNo.43, Keelung Rd., Sec.4, Da'an Dist., Taipei, Taiwan\n台灣台北市大安區基隆路四段43號"

def susenews():
    target_url = 'https://www.suse.com/c/news/'
    print('Start parsing news ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    date_lst = []
    subject_lst = []

    for i in soup.select('div .col-sm-3 p.date'):
        date_lst.append(i.getText())
    for j in soup.select('div .col-sm-8 .content'):
        subject_lst.append(j.getText())
    for k in range(len(date_lst)):
        content += u'\u2022' + " " + date_lst[k].replace('\t','').replace('\n','') + '\n'
        if k != len(date_lst) - 1:
            content += subject_lst[k].replace('\n','') + '\n\n'
        else:
            content += subject_lst[k].replace('\n','')
    return content

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
    if event.message.text == "Logo":
        client = ImgurClient(client_id, client_secret)
        images = client.get_album_images(album_id)
        index = random.randint(0, len(images) - 1)
        url = images[index].link
        #line_bot_api.reply_message(
        #    event.reply_token,
        #    TextSendMessage(text=url))
        image_message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        line_bot_api.reply_message(
            event.reply_token, image_message)
        return 0
    if event.message.text == "Venue":
        content = venue()
        #line_bot_api.reply_message(
        #    event.reply_token,
        #    TextSendMessage(text=content))
        image_message = ImageSendMessage(
            original_content_url='https://charleswang.us/opensuse-line-bot/taiwan-tech5.jpg',
            preview_image_url='https://charleswang.us/opensuse-line-bot/taiwan-tech3.jpg'
        )
        #line_bot_api.reply_message(
        #    event.reply_token, image_message)
        message = LocationSendMessage(
            title='台灣科技大學國際大樓',
            address='10607 臺北市大安區基隆路 4 段 43 號',
            latitude=25.013162196759016,
            longitude=121.54029257962338
        )
        line_bot_api.reply_message(event.reply_token, message)

        #line_bot_api.push_message(
        #    event.push_token,
        #    TextSendMessage(text=content))
        #line_bot_api.replySticker(event.reply_token, { packageId: '1', stickerId: '1' })
        return 0
    if event.message.text == "YouTube":
        target_url = 'https://www.youtube.com/user/opensusetv/videos'
        rs = requests.session()
        res = rs.get(target_url, verify=False)
        soup = BeautifulSoup(res.text, 'html.parser')
        seqs = ['https://www.youtube.com{}'.format(data.find('a')['href']) for data in soup.select('.yt-lockup-title')]
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text=seqs[random.randint(0, len(seqs) - 1)]),
                TextSendMessage(text=seqs[random.randint(0, len(seqs) - 1)])
            ])
        return 0
    if event.message.text == "News":
        content = susenews()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if event.message.text == "About":
        content = "openSUSE 亞洲高峰會是 openSUSE 社群 ( 即:貢獻者跟使用者 ) 很重要的活動之一，那些平常都在線上交流的人，現在可以一起面對面，與來自世界各地的高手進行交流，社群成員將會分享他們最新的知識、經驗，並學習關於 openSUSE FLOSS 的技術。這次在台北的活動是 openSUSE 亞洲高峰會的第五次，繼 2014 年首次的亞洲高峰會是在北京之後，過去的亞洲高峰有來自中國、台灣、印度、印度尼西亞、日本、南韓等國的參加。" 
        content += "\n\nRegistration: https://coscup2018.kktix.cc/events/coscup2018regist"
        content += "\n\nLINE Bot Created by:\nCharles Wang (cwang@suse.com)"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Hello from openSUSE.Asia Summit 2018!"))

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    print("package_id:", event.message.package_id)
    print("sticker_id:", event.message.sticker_id)
    # ref. https://developers.line.me/media/messaging-api/sticker_list.pdf
    sticker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 100, 101, 102, 103, 104, 105, 106,
                   107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
                   126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 401, 402]
    index_id = random.randint(0, len(sticker_ids) - 1)
    sticker_id = str(sticker_ids[index_id])
    print(index_id)
    sticker_message = StickerSendMessage(
        package_id='1',
        sticker_id=sticker_id
    )
    line_bot_api.reply_message(
        event.reply_token,
        sticker_message)


if __name__ == '__main__':
    app.run()
