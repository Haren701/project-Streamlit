import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🎮 Steam 게임 데이터 분석")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])
if uploaded_file is not None:
    steam_df = pd.read_csv(uploaded_file)

    # 기본 전처리
    steam_df = steam_df.dropna(subset=['positive_ratings', 'price', 'average_playtime'])

    st.markdown("## 🔍 데이터 미리보기")
    st.dataframe(steam_df.head(), use_container_width=True)

    # 시각화
    st.markdown("## 📊 시각화 자료")

    # 가격 구간별 평균 추천 수
    st.markdown("### 💰 가격 구간별 평균 추천 수")
    binned_df = steam_df.copy()
    binned_df['price_bin'] = pd.cut(
        binned_df['price'],
        bins=[-1, 0, 5, 10, 20, 30, 60],
        labels=["무료", "$0~5", "$5~10", "$10~20", "$20~30", "$30~60"]
    )
    price_group = binned_df.groupby('price_bin')['positive_ratings'].mean().reset_index()

    fig_bar = px.bar(
        price_group,
        x='price_bin',
        y='positive_ratings',
        title='💰 가격 구간별 평균 추천 수',
        labels={'price_bin': '가격 구간', 'positive_ratings': '평균 추천 수'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # 장르별 평균 추천 수
    st.markdown("### 🔥 장르별 평균 추천 수 (상위 15개)")
    genre_df = steam_df[['genres', 'positive_ratings', 'average_playtime']].dropna()
    genre_rows = []

    for _, row in genre_df.iterrows():
        genres = str(row['genres']).split(';')
        for g in genres:
            genre_rows.append({
                'genre': g.strip(),
                'positive_ratings': row['positive_ratings'],
                'average_playtime': row['average_playtime']
            })

    genre_expanded = pd.DataFrame(genre_rows)
    genre_summary = genre_expanded.groupby('genre').agg({
        'positive_ratings': 'mean',
        'average_playtime': 'mean'
    }).reset_index().sort_values(by='positive_ratings', ascending=False)

    fig_genre = px.bar(
        genre_summary.head(15),
        x='genre',
        y='positive_ratings',
        title='🔥 장르별 평균 추천 수 (상위 15개)',
        labels={'genre': '장르', 'positive_ratings': '평균 추천 수'}
    )
    st.plotly_chart(fig_genre, use_container_width=True)

    # 평균 플레이타임 vs 추천 수
    st.markdown("### ⏱ 평균 플레이타임 vs 추천 수 (로그 스케일)")
    trimmed_df = steam_df.copy()
    trimmed_df = trimmed_df[trimmed_df['positive_ratings'] < trimmed_df['positive_ratings'].quantile(0.99)]

    fig_scatter = px.scatter(
        trimmed_df,
        x='average_playtime',
        y='positive_ratings',
        title='⏱ 평균 플레이타임 vs 추천 수 (상위 99% 컷오프)',
        labels={'average_playtime': '평균 플레이타임(분)', 'positive_ratings': '추천 수'},
        log_y=True
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # 상관 분석
    st.markdown("### 📈 변수 간 상관 분석")
    corr_df = steam_df[['price', 'positive_ratings', 'negative_ratings', 'average_playtime']].dropna()
    corr_matrix = corr_df.corr(numeric_only=True)

    st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm'), use_container_width=True)

else:
    st.info("좌측 사이드바에서 Steam 데이터 CSV 파일을 업로드해주세요.")
