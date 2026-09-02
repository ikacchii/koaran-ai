import os
import time
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

    # 応答生成（失敗しても自動で再試行する処理）
    bot_response = None
    with st.spinner("コアランが考えてるよ..."):
        for attempt in range(3):  # 最大3回までやり直す
            try:
                response = client.models.generate_content(
                    model="models/gemini-3.6-flash",
                    contents=prompt,
                    config={"system_instruction": system_instruction}
                )
                bot_response = response.text
                break  # 成功したらループを抜ける
            except APIError as e:
                # 混雑・制限エラー（429）の時は自動で数秒待って再試行
                if "429" in str(e) and attempt < 2:
                    time.sleep(5)  # 5秒待つ
                else:
                    st.error("混雑しているみたいだコアラ... 少し時間を置いてから話しかけてね！")
                    break
            except Exception as e:
                st.error(f"エラーが発生しちゃっただコアラ...: {e}")
                break

    # 返信の表示と保存
    if bot_response:
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
