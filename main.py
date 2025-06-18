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

st.subheader("📊 시각화 자료")

# 1. 가격 vs 추천 수 (가격 버킷 처리)
binned_df = steam_df.copy()
binned_df['가격 구간'] = pd.cut(
    binned_df['price'],
    bins=[-1, 0, 5, 10, 20, 30, 60],
    labels=["무료", "0~5달러", "5~10달러", "10~20달러", "20~30달러", "30~60달러"]
)
price_group = binned_df.groupby('가격 구간')['positive_ratings'].mean().reset_index()

fig_bar = px.bar(
    price_group,
    x='가격 구간',
    y='positive_ratings',
    title='💰 가격 구간별 평균 추천 수',
    labels={'가격 구간': '가격 구간', 'positive_ratings': '평균 추천 수'}
)
st.plotly_chart(fig_bar, use_container_width=True)

# 2. 장르별 추천 수 및 플레이타임
genre_df = steam_df[['genres', 'positive_ratings', 'average_playtime']].dropna()
genre_rows = []

for _, row in genre_df.iterrows():
    genres = str(row['genres']).split(';')
    for g in genres:
        genre_rows.append({'장르': g.strip(), '추천 수': row['positive_ratings'], '평균 플레이타임': row['average_playtime']})

genre_expanded = pd.DataFrame(genre_rows)
genre_summary = genre_expanded.groupby('장르').agg({
    '추천 수': 'mean',
    '평균 플레이타임': 'mean'
}).reset_index().sort_values(by='추천 수', ascending=False)

fig_genre = px.bar(
    genre_summary.head(15),
    x='장르',
    y='추천 수',
    title='🔥 장르별 평균 추천 수 (상위 15개)',
    labels={'장르': '장르', '추천 수': '평균 추천 수'}
)
st.plotly_chart(fig_genre, use_container_width=True)

# 3. 상관 분석
st.subheader("📈 변수 간 상관 분석")

# 컬럼명 한글로 변경
corr_df = steam_df[['price', 'positive_ratings', 'negative_ratings', 'average_playtime']].dropna()
corr_df_renamed = corr_df.rename(columns={
    'price': '가격',
    'positive_ratings': '추천 수',
    'negative_ratings': '비추천 수',
    'average_playtime': '평균 플레이타임'
})
corr_matrix = corr_df_renamed.corr(numeric_only=True)

st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm'), use_container_width=True)
