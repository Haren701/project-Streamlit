import streamlit as st
import pandas as pd
import altair as alt
from collections import Counter

@st.cache_data
def load_data():
    steam = pd.read_csv('https://drive.google.com/uc?id=1A_BG5jSFNhf767TEtNbmmoA6dWCzOruG')
    desc = pd.read_csv('https://drive.google.com/uc?id=1QbdPyNpHpkPSXZUzQucHkY6MmtedJLgI')
    media = pd.read_csv('https://drive.google.com/uc?id=1PqNoE2a_9vJVwWTjDpVipD5p8kBB5-Cz')
    requirements = pd.read_csv('https://drive.google.com/uc?id=141XWiKtqJRQCUhpzhhLKvk5lcPBW7WlS')
    support = pd.read_csv('https://drive.google.com/uc?id=1IiOvUwVf0J4vwSNyYJqjKgeZ0akI14XS')
    tags = pd.read_csv('https://drive.google.com/uc?id=1qcSg_as9wRvqlBLLMj2NGBQ9t9DHXsBR')
    return steam, desc, media, requirements, support, tags

steam, desc, media, requirements, support, tags = load_data()

st.title("🎮 Steam 게임 탐색기")

# 게임 이름 검색
search = st.text_input("게임 이름 검색")
if search:
    filtered = steam[steam['name'].str.contains(search, case=False, na=False)]
    if not filtered.empty:
        game = filtered.iloc[0]
        st.subheader(game['name'])
        st.write(f"**출시일:** {game['release_date']}")
        st.write(f"**개발사:** {game['developer']}")
        st.write(f"**장르:** {game['genres']}")
        st.write(f"**가격:** ${game['price']:.2f}")

        # 설명
        desc_row = desc[desc['steam_appid'] == game['appid']]
        if not desc_row.empty:
            st.markdown(f"**설명:** {desc_row.iloc[0]['short_description']}")

        # 이미지
        media_row = media[media['steam_appid'] == game['appid']]
        if not media_row.empty:
            st.image(media_row.iloc[0]['header_image'], use_column_width=True)

        # 지원
        support_row = support[support['steam_appid'] == game['appid']]
        if not support_row.empty:
            st.write(f"**지원 이메일:** {support_row.iloc[0]['support_email']}")
            st.write(f"**지원 URL:** {support_row.iloc[0]['support_url']}")

        # 요구 사항
        req_row = requirements[requirements['steam_appid'] == game['appid']]
        if not req_row.empty:
            st.write("**최소 요구 사항:**")
            st.markdown(req_row.iloc[0]['minimum'], unsafe_allow_html=True)

# 인기 게임 TOP 10
st.header("🔥 인기 게임 TOP 10 (긍정 리뷰)")
top10 = steam.sort_values(by="positive_ratings", ascending=False).head(10)
st.dataframe(top10[['name', 'positive_ratings', 'price']])

# 가격 대비 평점 시각화
st.header("💰 가격 대비 리뷰 수")
chart_data = steam[steam['price'] > 0]
chart = alt.Chart(chart_data).mark_circle(size=60).encode(
    x='price',
    y='positive_ratings',
    tooltip=['name', 'price', 'positive_ratings']
).interactive()
st.altair_chart(chart, use_container_width=True)

# 장르별 분석
st.header("📚 장르별 게임 수")
def count_genres(genres_series):
    genre_list = []
    for genres in genres_series.dropna():
        genre_list.extend([g.strip() for g in genres.split(',')])
    return pd.DataFrame(Counter(genre_list).items(), columns=['Genre', 'Count']).sort_values(by='Count', ascending=False)

genre_df = count_genres(steam['genres'])
st.bar_chart(genre_df.set_index('Genre'))

# 태그 많은 게임 TOP 10
st.header("🏷️ 태그 많은 게임 TOP 10")
tags['tag_count'] = tags.drop('appid', axis=1).notnull().sum(axis=1)
top_tags = tags.sort_values(by='tag_count', ascending=False).head(10)
top_tags = top_tags.merge(steam[['appid', 'name']], on='appid', how='left')
st.dataframe(top_tags[['name', 'tag_count']])
