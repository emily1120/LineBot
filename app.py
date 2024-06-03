from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import time
import traceback
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

def QA_response(text):
    client = QuestionAnsweringClient(endpoint, credential)
    with client:
        question=text
        output = client.get_answers(
            question = question,
            project_name=knowledge_base_project,
            deployment_name=deployment
        )
    return output.answers[0].answer

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#訊息處理
words_dict = {
    "你最近的睡眠如何？": "我的睡眠質量很差，經常失眠。",
    "你有什麼讓你感到壓力的事情嗎？": "工作壓力和家庭責任讓我感到非常壓力大。",
    "你最近感覺到焦慮嗎？": "是的，我經常感到焦慮，特別是在晚上。",
    "你有什麼讓你感到快樂的活動嗎？": "我喜歡聽音樂和散步，這些讓我感到放鬆。",
    "你有過抑鬱的經歷嗎？": "有，我有時會感到非常沮喪，對未來感到無望。",
    "你有尋求過專業的心理幫助嗎？": "我以前沒有，但現在我覺得我需要尋求專業幫助。",
    "你如何應對壓力和焦慮？": "我嘗試通過運動和冥想來應對壓力，但有時效果不大。",
    "你對未來有什麼擔憂嗎？": "我擔心我的工作穩定性和家庭財務狀況。",
    "你有支持系統嗎？": "我有一些親密的朋友和家人，他們在我需要時會支持我。",
    "你對心理諮商有什麼期望？": "我希望通過心理諮商能夠找到更好的方法來應對壓力和焦慮。"
}

# 設置一個全局變量來跟踪狀態
user_state = {}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text

    # 如果收到 "結束"，回覆結束訊息並重置狀態
    if msg == "結束":
        reply_msg = "聊天已結束。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))
        if user_id in user_state:
            del user_state[user_id]
        return

    # 如果使用者狀態不存在或為新狀態，回應 "請輸入心理相關問題："
    if user_id not in user_state or user_state[user_id] == "new":
        reply_msg = f"'{msg}'，請輸入心理相關問題："
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))
        user_state[user_id] = "asked"  # 更新狀態為已詢問
    else:
        # 如果訊息在字典中，回應對應答案
        if msg in words_dict:
            ans = words_dict[msg]
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ans))
        else:
            error_msg = "抱歉，我暫時無法回答你的問題，請再次輸入問題："
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=error_msg))

    # 繼續維持狀態為已詢問
    user_state[user_id] = "asked"

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
