import streamlit as st
import pandas as pd
import altair as alt
import gdown
from collections import Counter
import os

# Google Drive 파일 ID 매핑
file_ids = {
    "steam": "1A_BG5jSFNhf767TEtNbmmoA6dWCzOruG",
    "desc": "1QbdPyNpHpkPSXZUzQucHkY6MmtedJLgI",
    "media": "1PqNoE2a_9vJVwWTjDpVipD5p8kBB5-Cz",
    "require": "141XWiKtqJRQCUhpzhhLKvk5lcPBW7WlS",
    "support": "1IiOvUwVf0J4vwSNyYJqjKgeZ0akI14XS",
    "tags": "1qcSg_as9wRvqlBLLMj2NGBQ9t9DHXsBR"
}

@st.cache_data
def download_csvs():
    datasets = {}
    for name, fid in file_ids.items():
        output = f"{name}.csv"
        if not os.path.exists(output):
            gdown.download(f"https://drive.google.com/uc?id={fid}", output, quiet=False)
        datasets[name] = pd.read_csv(output)
        datasets[name].columns = datasets[name].columns.str.strip().str.lower()
    return datasets

data = download_csvs()
steam = data['steam']
desc = data['desc']
media = data['media']
require = data['require']
support = data['support']
tags = data['tags']

st.title("🎮 Steam 게임 탐색기")

# 🔍 게임 검색
search = st.text_input("게임 이름 검색")
if search:
    filtered = steam[steam['name'].str.contains(search, case=False, na=False)]
    if not filtered.empty:
        game = filtered.iloc[0]
        st.subheader(game['name'])
        st.write(f"**출시일:** {game.get('release_date', 'N/A')}")
        st.write(f"**개발사:** {game.get('developer', 'N/A')}")
        st.write(f"**장르:** {game.get('genres', 'N/A')}")
        st.write(f"**가격:** ${game.get('price', 0):.2f}")

        # 설명 출력
        desc_row = desc[desc['steam_appid'] == game['appid']]
        if not desc_row.empty:
            st.markdown(f"**설명:** {desc_row.iloc[0].get('short_description', 'N/A')}")

        # 이미지 출력
        media_row = media[media['steam_appid'] == game['appid']]
        if not media_row.empty:
            st.image(media_row.iloc[0].get('header_image'), use_column_width=True)

        # 지원 정보
        support_row = support[support['steam_appid'] == game['appid']]
        if not support_row.empty:
            st.markdown(f"**지원 이메일:** {support_row.iloc[0].get('support_email', '없음')}")
            st.markdown(f"**지원 URL:** {support_row.iloc[0].get('support_url', '없음')}")

        # 요구 사양
        req_row = require[require['steam_appid'] == game['appid']]
        if not req_row.empty:
            st.markdown("**최소 요구 사양:**")
            st.markdown(req_row.iloc[0].get('minimum_requirements', 'N/A'), unsafe_allow_html=True)

# 🔥 인기 게임 TOP 10 (positive_ratings 기준)
st.header("🔥 인기 게임 TOP 10 (긍정 리뷰 수 기준)")
if 'positive_ratings' in steam.columns:
    top10 = steam.sort_values(by="positive_ratings", ascending=False).head(10)
    st.dataframe(top10[['name', 'positive_ratings', 'price']])
else:
    st.warning("⚠️ 'positive_ratings' 컬럼이 없어 인기 순위를 표시할 수 없습니다.")

# 💰 가격 대비 긍정 리뷰 수 시각화
st.header("💰 가격 대비 긍정 리뷰 수")
if 'positive_ratings' in steam.columns and 'price' in steam.columns:
    chart_data = steam[(steam['price'] > 0) & (steam['positive_ratings'] > 0)]
    chart = alt.Chart(chart_data).mark_circle(size=60).encode(
        x='price',
        y='positive_ratings',
        tooltip=['name', 'price', 'positive_ratings']
    ).interactive()
    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("⚠️ 시각화를 위한 데이터가 부족합니다.")

# 📚 장르별 게임 수
st.header("📚 장르별 게임 수")
if 'genres' in steam.columns:
    def count_genres(genres_series):
        genre_list = []
        for genres in genres_series.dropna():
            genre_list.extend([g.strip() for g in genres.split(',')])
        return pd.DataFrame(Counter(genre_list).items(), columns=['Genre', 'Count']).sort_values(by='Count', ascending=False)

    genre_df = count_genres(steam['genres'])
    st.bar_chart(genre_df.set_index('Genre'))
else:
    st.warning("⚠️ 'genres' 컬럼이 없어 장르 분석이 불가능합니다.")

# 🏷️ 태그 수 많은 게임 TOP 10
st.header("🏷️ 가장 많은 태그를 가진 게임 TOP 10")
if 'steamspy_tags' in tags.columns:
    tag_data = steam.merge(tags, how='left', on='appid')
    tag_data['tag_count'] = tag_data['steamspy_tags'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0)
    top_tags = tag_data.sort_values(by='tag_count', ascending=False).head(10)
    st.dataframe(top_tags[['name', 'tag_count', 'steamspy_tags']])
else:
    st.warning("⚠️ 'steamspy_tags' 컬럼이 없어 태그 정보를 표시할 수 없습니다.")
