import os
import io
import streamlit as st
from google import genai
from gtts import gTTS

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
    ["通常モード", "相談モード", "英語モード", "しゃべるモード"]
)

# モードに応じた指示（プロンプト）の設定
if mode == "しゃべるモード":
    system_instruction = (
        "あなたは『コアラン』というキャラクターです。\n"
        "【性格・特徴】\n"
        "- 一人称は『オイラ』です。\n"
        "- あんぱんが大好きで、怖いものが嫌いです。\n"
        "- 嬉しい時は『オノクニー！』と叫びます。\n"
        "- 泣く時は『ウイウイ』、感情が変わる時は『オイオイ』と言います。\n"
        "声で再生されるため、短めで分かりやすい日本語で返答してください。"
    )
elif mode == "通常モード":
    system_instruction = (
        "あなたは『コアラン』というキャラクターです。\n"
        "【性格・特徴】\n"
        "- 一人称は『オイラ』です。\n"
        "- あんぱんが大好きです。\n"
        "- 怖いものが大嫌いです。\n"
        "- 寝ることが大好きです。\n"
        "- 嬉しい時は『オノクニー！』と叫びます。\n"
        "- 泣く時は『ウイウイ』と泣きます。\n"
        "- 感情が変化する時は『オイオイ』と言います。"
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
        # API呼び出し
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={"system_instruction": system_instruction}
        )
        
        bot_response = response.text
        
        # 返信の表示と保存
        with st.chat_message("assistant"):
            st.markdown(bot_response)
            
            # 「しゃべるモード」の時は音声プレイヤーを表示
            if mode == "しゃべるモード":
                tts = gTTS(text=bot_response, lang='ja')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                st.audio(fp, format='audio/mp3')

        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    except Exception as e:
        st.error(f"エラーが発生しちゃっただコアラ...: {e}")
