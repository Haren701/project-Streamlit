import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 불러오기
steam_df = pd.read_csv("steam.csv")
tags_df = pd.read_csv("steamspy_tag_data.csv")
steam_df = steam_df.merge(tags_df, on="appid", how="left")

st.set_page_config(page_title="Steam 게임 탐색기", layout="wide")
st.title("🎮 Steam 게임 탐색기")

# 고유 장르 추출 함수
def extract_unique_genres(df):
    genre_set = set()
    for genres in df['genres'].dropna():
        for g in str(genres).split(';'):
            genre_set.add(g.strip())
    return sorted(list(genre_set))

unique_genres = extract_unique_genres(steam_df)

# 🔍 사이드바 필터
with st.sidebar:
    st.header("🔍 필터")
    name_query = st.text_input("게임 이름 검색")
    developer_filter = st.multiselect("개발사 선택", options=steam_df['developer'].dropna().unique())
    genre_filter = st.multiselect("장르 태그 선택 (다중 선택 가능)", options=unique_genres)
    price_max = int(steam_df['price'].max())
    price_range = st.slider("가격 범위", 0, price_max, (0, price_max), step=1)

# 🔎 필터 적용
filtered_df = steam_df.copy()
if name_query:
    filtered_df = filtered_df[filtered_df['name'].str.contains(name_query, case=False, na=False)]
if developer_filter:
    filtered_df = filtered_df[filtered_df['developer'].isin(developer_filter)]
if genre_filter:
    filtered_df = filtered_df[filtered_df['genres'].apply(lambda g: all(tag in str(g).split(';') for tag in genre_filter))]
filtered_df = filtered_df[(filtered_df['price'] >= price_range[0]) & (filtered_df['price'] <= price_range[1])]

st.subheader(f"🎯 총 {len(filtered_df)}개의 게임이 검색되었습니다.")
st.dataframe(
    filtered_df[['name', 'release_date', 'developer', 'genres', 'price', 'positive_ratings', 'negative_ratings', 'average_playtime']],
    use_container_width=True,
    height=400
)

# 📊 시각화 자료
st.subheader("📊 시각화 자료")

# 1. 가격 vs 추천 수 (상위 99% + 로그스케일)
price_rating_df = steam_df[['price', 'positive_ratings']].dropna()
price_rating_df = price_rating_df[
    (price_rating_df['price'] <= price_rating_df['price'].quantile(0.99)) &
    (price_rating_df['positive_ratings'] <= price_rating_df['positive_ratings'].quantile(0.99))
]

fig1 = px.scatter(
    price_rating_df,
    x='price',
    y='positive_ratings',
    title='💰 가격 vs 👍 추천 수 (상위 99% 컷오프)',
    labels={'price': '가격($)', 'positive_ratings': '추천 수'},
    log_y=True
)
st.plotly_chart(fig1, use_container_width=True)

# 2. 평균 플레이타임 vs 추천 수 (상위 99% + 로그스케일)
playtime_df = steam_df[['average_playtime', 'positive_ratings']].dropna()
playtime_df = playtime_df[
    (playtime_df['average_playtime'] <= playtime_df['average_playtime'].quantile(0.99)) &
    (playtime_df['positive_ratings'] <= playtime_df['positive_ratings'].quantile(0.99))
]

fig2 = px.scatter(
    playtime_df,
    x='average_playtime',
    y='positive_ratings',
    title='⏱ 평균 플레이타임 vs 👍 추천 수 (상위 99% 컷오프)',
    labels={'average_playtime': '평균 플레이타임(분)', 'positive_ratings': '추천 수'},
    log_y=True
)
st.plotly_chart(fig2, use_container_width=True)

# 🔍 게임 상세 정보
st.subheader("🔎 게임 상세 정보 보기")
if not filtered_df.empty:
    selected_game = st.selectbox("게임 선택", filtered_df['name'].unique())
    detail = filtered_df[filtered_df['name'] == selected_game].iloc[0]

    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"**🧾 이름:** {detail['name']}")
            st.markdown(f"**🛠 개발사:** {detail['developer']}")
            st.markdown(f"**📅 출시일:** {detail['release_date']}")
            st.markdown(f"**💰 가격:** ${detail['price']}")
            st.markdown(f"**👍 추천:** {detail['positive_ratings']} / 👎 비추천: {detail['negative_ratings']}")
            st.markdown(f"**⏱ 평균 플레이타임:** {detail['average_playtime']} 분")
        with col2:
            st.empty()
else:
    st.warning("조건에 맞는 게임이 없습니다. 필터를 조정해주세요.")
