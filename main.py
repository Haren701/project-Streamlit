import streamlit as st
import pandas as pd

# Load data from GitHub raw URLs
steam_df = pd.read_csv("steam.csv")
tags_df = pd.read_csv("steamspy_tag_data.csv")

# Merge data
steam_df = steam_df.merge(tags_df, on="appid", how="left")

st.set_page_config(page_title="Steam 게임 탐색기", layout="wide")
st.title("🎮 Steam 게임 탐색기")

# 장르 문자열 분리하여 단일화 후 새로운 리스트 생성
def extract_unique_genres(df):
    genre_set = set()
    for genres in df['genres'].dropna():
        for g in str(genres).split(';'):
            genre_set.add(g.strip())
    return sorted(list(genre_set))

unique_genres = extract_unique_genres(steam_df)

# Sidebar filters
st.sidebar.header("🔍 필터")
name_query = st.sidebar.text_input("게임 이름 검색")
developer_filter = st.sidebar.multiselect("개발사 선택", options=steam_df['developer'].dropna().unique())
genre_filter = st.sidebar.multiselect("장르 태그 선택 (다중 선택 가능)", options=unique_genres)

price_max = int(steam_df['price'].max())
price_range = st.sidebar.slider("가격 범위", 0, price_max, (0, price_max), step=1)

# Apply filters
filtered_df = steam_df.copy()
if name_query:
    filtered_df = filtered_df[filtered_df['name'].str.contains(name_query, case=False, na=False)]
if developer_filter:
    filtered_df = filtered_df[filtered_df['developer'].isin(developer_filter)]
if genre_filter:
    filtered_df = filtered_df[filtered_df['genres'].apply(lambda g: all(tag in str(g).split(';') for tag in genre_filter))]
filtered_df = filtered_df[(filtered_df['price'] >= price_range[0]) & (filtered_df['price'] <= price_range[1])]

st.subheader(f"🎯 총 {len(filtered_df)}개의 게임이 검색되었습니다.")
st.dataframe(filtered_df[['name', 'release_date', 'developer', 'genres', 'price', 'positive_ratings', 'negative_ratings', 'average_playtime']])

# Game detail viewer
st.subheader("🔎 게임 상세 정보 보기")
selected_game = st.selectbox("게임 선택", filtered_df['name'].unique())
detail = filtered_df[filtered_df['name'] == selected_game].iloc[0]

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**🧾 이름:** {detail['name']}")
    st.markdown(f"**🛠 개발사:** {detail['developer']}")
    st.markdown(f"**📅 출시일:** {detail['release_date']}")
    st.markdown(f"**💰 가격:** ${detail['price']}")
    st.markdown(f"**👍 추천:** {detail['positive_ratings']} / 👎 비추천: {detail['negative_ratings']}")
    st.markdown(f"**⏱ 평균 플레이타임:** {detail['average_playtime']} 분")

# Tag filtering and visualization
st.subheader("🏷 태그 기반 탐색")
tag_columns = tags_df.drop(columns=["appid"]).columns
selected_tags = st.multiselect("태그 선택 (여러 개 선택 가능)", tag_columns)

if selected_tags:
    tag_condition = steam_df[selected_tags].sum(axis=1) == len(selected_tags)
    tagged_games = steam_df[tag_condition]
    st.write(f"**'{', '.join(selected_tags)}' 태그를 모두 포함한 게임 수:** {len(tagged_games)}")
    st.dataframe(tagged_games[['name', 'developer', 'genres', 'price']])
else:
    st.info("좌측에서 하나 이상의 태그를 선택하세요.")
