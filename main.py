import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Load data
steam_df = pd.read_csv("steam.csv")
tags_df = pd.read_csv("steamspy_tag_data.csv")

# Merge tag data
steam_df = steam_df.merge(tags_df, on="appid", how="left")

st.set_page_config(page_title="Steam 게임 탐색기", layout="wide")
st.title("🎮 Steam 게임 탐색기")

# Helper function: Extract unique genres
def extract_unique_genres(df):
    genre_set = set()
    for genres in df['genres'].dropna():
        for g in str(genres).split(';'):
            genre_set.add(g.strip())
    return sorted(list(genre_set))

unique_genres = extract_unique_genres(steam_df)

# Sidebar filters
with st.sidebar:
    st.header("🔍 필터")
    name_query = st.text_input("게임 이름 검색")
    developer_filter = st.multiselect("개발사 선택", options=steam_df['developer'].dropna().unique())
    genre_filter = st.multiselect("장르 태그 선택 (다중 선택 가능)", options=unique_genres)
    price_max = int(steam_df['price'].max())
    price_range = st.slider("가격 범위", 0, price_max, (0, price_max), step=1)

# Filter data
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

# Game detail viewer
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
            st.markdown("(여기에 추후 이미지나 태그 시각화 추가 가능)")

# --- Visualization Section ---
st.header("📊 데이터 시각화")

# 1. 장르별 게임 수
st.subheader("1️⃣ 장르별 게임 수")
genre_counts = pd.Series([g.strip() for sublist in steam_df['genres'].dropna().str.split(';') for g in sublist]).value_counts()
fig1 = px.bar(x=genre_counts.index[:15], y=genre_counts.values[:15], labels={'x': '장르', 'y': '게임 수'})
st.plotly_chart(fig1, use_container_width=True)

# 2. 가격대별 평균 추천 수
st.subheader("2️⃣ 가격대별 평균 추천 수")
price_bins = pd.cut(steam_df['price'], bins=[0, 5, 10, 20, 40, 60, 100], right=False)
price_grouped = steam_df.groupby(price_bins)[['positive_ratings']].mean().reset_index()
fig2 = px.bar(price_grouped, x='price', y='positive_ratings', labels={'price': '가격대', 'positive_ratings': '평균 추천 수'})
st.plotly_chart(fig2, use_container_width=True)

# 3. 평균 플레이타임 분포
st.subheader("3️⃣ 평균 플레이타임 분포")
fig3 = px.histogram(steam_df, x='average_playtime', nbins=50, title="평균 플레이타임 분포 (분)")
st.plotly_chart(fig3, use_container_width=True)

# 4. 상관관계 히트맵
st.subheader("4️⃣ 주요 수치 간 상관관계")
correlation_cols = ['price', 'positive_ratings', 'negative_ratings', 'average_playtime']
corr_matrix = steam_df[correlation_cols].corr()
fig4, ax4 = plt.subplots()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax4)
st.pyplot(fig4)
