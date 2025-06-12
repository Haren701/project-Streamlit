import streamlit as st
import pandas as pd
import gdown
import os
import plotly.express as px

# Google Drive 파일들 다운로드
file_ids = {
    "steam.csv": "1A_BG5jSFNhf767TEtNbmmoA6dWCzOruG",
    "steam_description_data.csv": "1QbdPyNpHpkPSXZUzQucHkY6MmtedJLgI",
    "steam_media_data.csv": "1PqNoE2a_9vJVwWTjDpVipD5p8kBB5-Cz",
    "steam_requirements_data.csv": "141XWiKtqJRQCUhpzhhLKvk5lcPBW7WlS",
    "steam_support_info.csv": "1IiOvUwVf0J4vwSNyYJqjKgeZ0akI14XS",
    "steamspy_tag_data.csv": "1qcSg_as9wRvqlBLLMj2NGBQ9t9DHXsBR"
}

for filename, file_id in file_ids.items():
    if not os.path.exists(filename):
        gdown.download(f"https://drive.google.com/uc?id={file_id}", filename, quiet=False)

# 데이터 로드
steam = pd.read_csv("steam.csv")

# 추가 데이터 로드
desc = pd.read_csv("steam_description_data.csv")
media = pd.read_csv("steam_media_data.csv")
require = pd.read_csv("steam_requirements_data.csv")
support = pd.read_csv("steam_support_info.csv")
tags = pd.read_csv("steamspy_tag_data.csv")

# 병합 전에 appid 컬럼 존재 여부 확인
def safe_merge(df1, df2, name):
    if 'appid' in df2.columns:
        return df1.merge(df2, on='appid', how='left')
    else:
        st.warning(f"⚠️ 병합 실패: '{name}' 데이터에 'appid' 컬럼이 없습니다.")
        return df1

steam = safe_merge(steam, desc, "desc")
steam = safe_merge(steam, media, "media")
steam = safe_merge(steam, require, "require")
steam = safe_merge(steam, support, "support")

# steamspy_tag_data는 특별 처리 필요
if 'appid' in tags.columns and 'tags' in tags.columns:
    tags = tags.rename(columns={'tags': 'steamspy_tags'})
    steam = steam.merge(tags[['appid', 'steamspy_tags']], on='appid', how='left')
else:
    st.warning("⚠️ steamspy_tag_data.csv에서 'appid' 또는 'tags' 컬럼이 없습니다.")

# Streamlit UI
st.title("🎮 Steam 게임 탐색기")

# 게임 검색
search_term = st.text_input("게임 이름 검색")
if search_term:
    results = steam[steam['name'].str.contains(search_term, case=False, na=False)]
    st.write(results[['name', 'release_date', 'price', 'positive_ratings']].head(10))

# 인기 게임 Top 10
if 'positive_ratings' in steam.columns:
    st.subheader("🔥 인기 게임 TOP 10 (긍정 리뷰 수 기준)")
    top10 = steam.sort_values(by='positive_ratings', ascending=False).head(10)
    st.write(top10[['name', 'positive_ratings']])
    fig = px.bar(top10, x='name', y='positive_ratings', title="긍정 리뷰 상위 게임")
    st.plotly_chart(fig)
else:
    st.warning("⚠️ 'positive_ratings' 컬럼이 없어 인기 순위를 표시할 수 없습니다.")

# 가격 대비 리뷰 수
if 'price' in steam.columns and 'positive_ratings' in steam.columns:
    st.subheader("💰 가격 대비 긍정 리뷰 수")
    filtered = steam[steam['price'] > 0]
    filtered['value_score'] = filtered['positive_ratings'] / filtered['price']
    top_value = filtered.sort_values(by='value_score', ascending=False).head(10)
    st.write(top_value[['name', 'price', 'positive_ratings', 'value_score']])
    fig2 = px.bar(top_value, x='name', y='value_score', title="가격 대비 긍정 리뷰 수")
    st.plotly_chart(fig2)
else:
    st.warning("⚠️ 시각화를 위한 데이터가 부족합니다.")

# 장르별 게임 수
if 'genres' in steam.columns:
    st.subheader("📚 장르별 게임 수")
    genre_series = steam['genres'].dropna().str.split(';').explode()
    genre_count = genre_series.value_counts().head(10)
    st.bar_chart(genre_count)
else:
    st.warning("⚠️ 'genres' 컬럼이 없어 장르 분석이 불가능합니다.")

# 가장 많은 태그를 가진 게임
if 'steamspy_tags' in steam.columns:
    st.subheader("🏷️ 가장 많은 태그를 가진 게임 TOP 10")
    tag_series = steam['steamspy_tags'].dropna().str.split(';').explode()
    tag_count = tag_series.value_counts().head(10)
    st.bar_chart(tag_count)
else:
    st.warning("⚠️ 'steamspy_tags' 컬럼이 없어 태그 정보를 표시할 수 없습니다.")
