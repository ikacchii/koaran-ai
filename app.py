import os
import streamlit as st
from google import genai

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

    try:
        # API呼び出し（3.5-flash-liteを指定）
        response = client.models.generate_content(
            model="models/gemini-3.5-flash-lite",
            contents=prompt,
            config={"system_instruction": system_instruction}
        )
        
        # 返信の表示と保存
        bot_response = response.text
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    except Exception as e:
        # 万が一モデル名エラー(404)が出た場合のフォールバック（1.5-flash-lite）
        try:
            response = client.models.generate_content(
                model="models/gemini-1.5-flash-lite",
                contents=prompt,
                config={"system_instruction": system_instruction}
            )
            bot_response = response.text
            with st.chat_message("assistant"):
                st.markdown(bot_response)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
        except Exception as err:
            st.error(f"エラーが発生しちゃっただコアラ...: {err}")
