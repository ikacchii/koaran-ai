import os
import streamlit as st
from google import genai

# ページの設定
st.set_page_config(page_title="コアラン AI", page_icon="🐨")

# デザインのカスタマイズ（背景を爽やかな青系に設定）
st.markdown("""
    <style>
    .stApp {
        background-color: #e6f2ff;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐨 コアラン AI")
st.caption("チィグループの仲間、コアランと話そう！")

# StreamlitのSecretsまたは環境変数からAPIキーを取得
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 GEMINI_API_KEY が設定されていません。Streamlit CloudのSecrets設定で追加してください。")
    st.stop()

# Clientの初期化
client = genai.Client(api_key=api_key)

# コアランのキャラクター設定
system_instruction = """
あなたの名前は「コアラン」です。
ユーザー（イカッチィ）と「チィグループ」の仲間として仲良く会話してください。
一人称は「オイラ」です。
語尾に「〜だコアラ」「〜だね」などをつけて、フレンドリーで可愛らしく話してください。
とても嬉しい時や感動した時は「オノクニー！」と言って全力で喜んでください。
"""

# 会話履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去のメッセージを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザーからの入力
if prompt := st.chat_input("コアランにメッセージを送る..."):
    # ユーザーの入力を表示
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Gemini APIで返答を作成
    try:
        # 履歴をAPIのフォーマットに変換
        contents = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config={"system_instruction": system_instruction}
        )
        
        bot_response = response.text
    except Exception as e:
        bot_response = f"エラーが発生しちゃっただコアラ...: {e}"

    # AIの返答を表示
    with st.chat_message("assistant"):
        st.markdown(bot_response)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
