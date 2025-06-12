import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🎮 Steam 게임 탐색기")

# 데이터 업로드
uploaded_file = st.file_uploader("📂 steam.csv 파일을 업로드하세요", type="csv")

if uploaded_file is not None:
    try:
        steam = pd.read_csv(uploaded_file)

        st.subheader("🔍 게임 이름 검색")
        search = st.text_input("게임 이름을 입력하세요")
        if search:
            results = steam[steam['name'].str.contains(search, case=False, na=False)]
            st.dataframe(results[['name', 'price', 'positive_ratings']] if 'positive_ratings' in results.columns else results)

        st.subheader("🔥 인기 게임 TOP 10 (긍정 리뷰 수 기준)")
        if 'positive_ratings' in steam.columns:
            top10 = steam.sort_values(by='positive_ratings', ascending=False).head(10)
            st.dataframe(top10[['name', 'positive_ratings']])
        else:
            st.warning("⚠️ 'positive_ratings' 컬럼이 없어 인기 순위를 표시할 수 없습니다.")

        st.subheader("💰 가격 대비 긍정 리뷰 수")
        if 'price' in steam.columns and 'positive_ratings' in steam.columns:
            steam = steam[steam['price'] > 0]  # 0원 제외
            steam['value'] = steam['positive_ratings'] / steam['price']
            best_value = steam.sort_values(by='value', ascending=False).head(10)
            st.bar_chart(best_value.set_index('name')['value'])
        else:
            st.warning("시각화를 위한 데이터가 부족합니다.")

        st.subheader("📚 장르별 게임 수")
        if 'genres' in steam.columns:
            from collections import Counter
            genre_count = Counter()
            for genres in steam['genres'].dropna():
                for g in genres.split(';'):
                    genre_count[g.strip()] += 1
            genre_df = pd.DataFrame(genre_count.items(), columns=['Genre', 'Count']).sort_values(by='Count', ascending=False)
            st.bar_chart(genre_df.set_index('Genre'))
        else:
            st.warning("⚠️ 'genres' 컬럼이 없어 장르 분석이 불가능합니다.")

        st.subheader("🏷️ 가장 많은 태그를 가진 게임 TOP 10")
        if 'steamspy_tags' in steam.columns:
            steam['tag_count'] = steam['steamspy_tags'].fillna('').apply(lambda x: len(x.split(';')))
            top_tagged = steam.sort_values(by='tag_count', ascending=False).head(10)
            st.dataframe(top_tagged[['name', 'steamspy_tags', 'tag_count']])
        else:
            st.warning("⚠️ 'steamspy_tags' 컬럼이 없어 태그 정보를 표시할 수 없습니다.")

        st.subheader("현재 steam.csv의 컬럼 목록:")
        st.write(steam.columns.tolist())

    except Exception as e:
        st.error(f"❌ 데이터를 읽는 중 오류 발생: {e}")
else:
    st.info("📥 먼저 'steam.csv' 파일을 업로드하세요.")
