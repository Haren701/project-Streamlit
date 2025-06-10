# app.py
import streamlit as st
import pandas as pd
import altair as alt
from collections import Counter

def gdrive_to_raw(gid):
    return f"https://drive.google.com/uc?id={gid}"

@st.cache_data
def load_data():
    steam = pd.read_csv(gdrive_to_raw("1A_BG5jSFNhf767TEtNbmmoA6dWCzOruG"))
    steam.columns = steam.columns.str.strip().str.lower()
    return steam

steam = load_data()

st.title("🎮 Steam 게임 탐색기 (단일 CSV 테스트)")

st.write("컬럼 목록:", steam.columns.tolist())

# 추가 테스트 코드, 예: positive_ratings
if 'positive_ratings' in steam.columns:
    st.write("✅ positive_ratings exists")
    st.write(steam[['name', 'positive_ratings']].head())
else:
    st.error("🔴 positive_ratings 컬럼이 없습니다.")
