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
    "我最近的睡眠如何？": "你可能需要一些改善睡眠質量的方法，例如建立規律的作息時間和創建舒適的睡眠環境。",
    "我該如何應對壓力和焦慮？": "你可以嘗試通過運動和冥想來應對壓力，並尋找一些讓你感到放鬆的活動。",
    "我最近感覺到焦慮，該怎麼辦？": "你可以試著進行深呼吸練習，或者與信任的人談談你的感受。",
    "有什麼讓我感到快樂的活動嗎？": "你可以嘗試參加一些你喜歡的活動，比如聽音樂、散步或閱讀，這些都能幫助你感到快樂。",
    "我感覺有些抑鬱，怎麼辦？": "與朋友或家人談談你的感受，並考慮尋求專業的心理幫助，這樣能幫助你走出抑鬱。",
    "我是否需要尋求專業的心理幫助？": "如果你感覺到持續的壓力或情緒低落，尋求專業的心理幫助會是個不錯的選擇。",
    "我應該如何管理壓力？": "嘗試找到一些讓你放鬆的活動，例如運動、冥想或愛好，這些能幫助你減少壓力。",
    "我對未來感到擔憂，該怎麼辦？": "與朋友或家人分享你的擔憂，並制定一些可行的計劃來應對未來的挑戰。",
    "我有支持系統嗎？": "你有一些親密的朋友和家人，他們在你需要時會支持你，讓你不會感到孤單。",
    "我希望通過心理諮商獲得什麼？": "心理諮商可以幫助你找到更好的方法來應對壓力和焦慮，提升你的整體幸福感。"
}

# 設置一個全局變量來跟踪狀態
user_state = {}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text

    # 如果收到 "結束"，回覆結束訊息並重置狀態
    if msg == "結束":
        reply_msg = "聊天已結束，祝福您擁有快樂的一天。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))
        if user_id in user_state:
            del user_state[user_id]
        return

    # 如果使用者狀態不存在或為新狀態，回應 "請輸入心理相關問題："
    if user_id not in user_state or user_state[user_id] == "new":
        reply_msg = f"{msg}，請輸入心理相關問題："
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))
        user_state[user_id] = "asked"  # 更新狀態為已詢問
    else:
        # 如果訊息在字典中，回應對應答案
        if msg in words_dict:
            ans = words_dict[msg]
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ans))
        else:
            error_msg = "抱歉，我暫時無法回答你的問題。請再次輸入問題："
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
