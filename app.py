from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 計數器用來追蹤訊息數量
message_counter = 0

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global message_counter  # 使用全域變數計數器
    text1=event.message.text

  # 每次收到訊息時，計數器加一
    message_counter += 1
    
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "user", "content": text1}
        ],
        model="gpt-4o-mini-2024-07-18",
        temperature = 0.5,
    )
    try:
        ret = response['choices'][0]['message']['content'].strip()
    except:
        ret = '發生錯誤！'
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=ret))

    # 可選：每次發送訊息後，打印出目前的計數
    print(f"已發送至OpenAI的訊息數量: {message_counter}")
if __name__ == '__main__':
    app.run()
