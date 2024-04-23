import base64
import os
import streamlit as st
from openai import OpenAI
import settings


# 環境変数からAPIキーを読み込む
api_key = settings.OPEN_AI_KEY
# api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=api_key)

st.title("音声からデータを要約するwebアプリ")

audio_file = st.file_uploader(
    "音声ファイルをアップロードしてください", type=["m4a", "mp3", "webm", "mp4", "mpga", "wav"]
)

if audio_file is not None:
    st.audio(audio_file, format="audio/wav")

    if st.button("音声を予約する"):
        with st.spinner("音声を文字起こししています..."):
            transcript= client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                language="ja",
                response_format="text"
            )

        with st.spinner("音声ファイルの要約を生成中です..."):
            # OpenAIのGPTモデルを使用して、文字起こし結果から求人票を生成
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"以下の情報をもとに文章を要約してください。\n{transcript}\n"}
            ]
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            job_description = response.choices[0].message.content

        st.success("文章が要約されました！")
        st.write(job_description)

        # 求人票をバイトに変換し、それをbase64でエンコードする
        job_description_encoded = base64.b64encode(job_description.encode()).decode()
        # ダウンロードリンクを作成する
        st.markdown(
            f'<a href="data:file/txt;base64,{job_description_encoded}" download="job_description.txt">Download Job Description</a>',
            unsafe_allow_html=True,
        )
