import streamlit as st
import pandas as pd
import altair as alt

# Load data
@st.cache_data
def load_data():
    steam = pd.read_csv("steam.csv")
    desc = pd.read_csv("steam_description_data.csv")
    media = pd.read_csv("steam_media_data.csv")
    tags = pd.read_csv("steamspy_tag_data.csv")
    return steam, desc, media, tags

steam, desc, media, tags = load_data()

st.title("🎮 Steam 게임 탐색기")

# 게임 선택
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
from collections import Counter

def count_genres(genres_series):
    genre_list = []
    for genres in genres_series.dropna():
        genre_list.extend([g.strip() for g in genres.split(',')])
    return pd.DataFrame(Counter(genre_list).items(), columns=['Genre', 'Count']).sort_values(by='Count', ascending=False)

genre_df = count_genres(steam['genres'])
st.bar_chart(genre_df.set_index('Genre'))
