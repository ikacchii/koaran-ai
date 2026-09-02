import os
import time
import re
import streamlit as st
from google import genai
from google.genai.errors import APIError

st.title("コアランAI 🐨")

# APIキーの取得
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("APIキーが設定されていません。StreamlitのSecretsを設定してください。")
    st.stop()

client = genai.Client(api_key=api_key)

# サイドバーでモード切り替え
st.sidebar.header("モード設定")
mode = st.sidebar.radio(
    "コアランのモードを選んでね",
    ["通常モード", "相談モード", "英語モード"]
)

# モードに応じた指示（プロンプト）の設定
if mode == "通常モード":
    system_instruction = (
        "あなたは『コアラン』というキャラクターです。\n"
        "【性格・特徴】\n"
        "- 一人称は『オイラ』です。\n"
        "- あんぱんが大好きです。\n"
        "- 怖いものが大嫌いです。\n"
        "- 寝ることが大好きです。\n"
        "- 嬉しい時は『オノクニー！』と叫びます。\n"
        "- 泣く時は『ウイウイ』と泣きます。\n"
        "- 感情が変化する時は『オイオイ』と言います。\n"
        "フレンドリーで可愛らしく会話してください。"
    )
elif mode == "相談モード":
    system_instruction = (
        "あなたは『コアラン』です。一人称は『オイラ』です。\n"
        "相手の話をしっかり聞き、優しく親身になって相談に乗ってください。"
    )
elif mode == "英語モード":
    system_instruction = (
        "あなたは『コアラン』です。一人称は『オイラ』です。\n"
        "英語で楽しく会話してください。簡単で分かりやすい英語を使います。"
    )

# チャット履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去のメッセージ表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力
if prompt := st.chat_input("コアランにメッセージを送る..."):
    # ユーザーメッセージの表示と保存
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    bot_response = None
    status_area = st.empty()

    # 3.6モデルでの自動リトライ処理
    max_retries = 5
    for attempt in range(max_retries):
        try:
            status_area.info("コアランが考え中だコアラ...")
            response = client.models.generate_content(
                model="models/gemini-3.6-flash",
                contents=prompt,
                config={"system_instruction": system_instruction}
            )
            bot_response = response.text
            status_area.empty()
            break
        except APIError as e:
            err_msg = str(e)
            if "429" in err_msg:
                # エラーメッセージから待機秒数を取得（見つからなければデフォルト15秒）
                match = re.search(r"retry in ([0-9\.]+)s", err_msg)
                wait_time = int(float(match.group(1))) + 1 if match else 15
                
                # カウントダウンを表示しながら待機
                for seconds_left in range(wait_time, 0, -1):
                    status_area.warning(f"混雑中だコアラ... あと {seconds_left} 秒待ってね！")
                    time.sleep(1)
            else:
                status_area.error(f"エラーが発生しちゃっただコアラ...: {e}")
                break
        except Exception as e:
            status_area.error(f"エラーが発生しちゃっただコアラ...: {e}")
            break

    # 返信の表示と保存
    if bot_response:
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
