import streamlit as st
import pandas as pd
import altair as alt
from collections import Counter

# 구글 드라이브 파일 링크를 직접 다운로드 가능한 링크로 변환
def gdrive_to_raw(gid):
    return f"https://drive.google.com/uc?id={gid}"

# 데이터 로드 함수
@st.cache_data
def load_data():
    steam = pd.read_csv(gdrive_to_raw("1A_BG5jSFNhf767TEtNbmmoA6dWCzOruG"))      # steam.csv
    desc = pd.read_csv(gdrive_to_raw("1QbdPyNpHpkPSXZUzQucHkY6MmtedJLgI"))       # description
    media = pd.read_csv(gdrive_to_raw("1PqNoE2a_9vJVwWTjDpVipD5p8kBB5-Cz"))      # media
    tags = pd.read_csv(gdrive_to_raw("141XWiKtqJRQCUhpzhhLKvk5lcPBW7WlS"))       # tags
    support = pd.read_csv(gdrive_to_raw("1IiOvUwVf0J4vwSNyYJqjKgeZ0akI14XS"))    # support
    require = pd.read_csv(gdrive_to_raw("1qcSg_as9wRvqlBLLMj2NGBQ9t9DHXsBR"))    # requirements

    # 컬럼명 소문자 및 공백 제거
    for df in [steam, desc, media, tags, support, require]:
        df.columns = df.columns.str.strip().str.lower()

    # 'tags' 파일 병합 (컬럼 존재할 경우만)
    if 'steam_appid' in tags.columns and 'tag' in tags.columns:
        tag_summary = tags.groupby('steam_appid')['tag'].apply(lambda x: ', '.join(x)).reset_index()
        tag_summary.columns = ['steam_appid', 'tags']
        steam = steam.merge(tag_summary, how='left', left_on='appid', right_on='steam_appid')
    else:
        steam['tags'] = None

    return steam, desc, media, support, require

steam, desc, media, support, require = load_data()

st.title("🎮 Steam 게임 탐색기")

# 게임 검색
search = st.text_input("🔍 게임 이름 검색")
if search:
    filtered = steam[steam['name'].str.contains(search, case=False, na=False)]
    if not filtered.empty:
        game = filtered.iloc[0]
        st.subheader(game['name'])
        st.write(f"**출시일:** {game.get('release_date', '정보 없음')}")
        st.write(f"**개발사:** {game.get('developer', '정보 없음')}")
        st.write(f"**장르:** {game.get('genres', '정보 없음')}")
        st.write(f"**가격:** ${game.get('price', 0):.2f}")

        # 설명
        desc_row = desc[desc['steam_appid'] == game['appid']]
        if not desc_row.empty:
            st.markdown(f"**설명:** {desc_row.iloc[0]['short_description']}")

        # 미디어 이미지
        media_row = media[media['steam_appid'] == game['appid']]
        if not media_row.empty:
            st.image(media_row.iloc[0]['header_image'], use_column_width=True)

        # 지원 정보
        support_row = support[support['steam_appid'] == game['appid']]
        if not support_row.empty:
            st.markdown(f"**지원 이메일:** {support_row.iloc[0]['support_email']}")
            st.markdown(f"**지원 URL:** {support_row.iloc[0]['support_url']}")

        # 요구 사양
        req_row = require[require['steam_appid'] == game['appid']]
        if not req_row.empty:
            st.markdown("**최소 요구 사양:**")
            st.markdown(req_row.iloc[0]['minimum_requirements'], unsafe_allow_html=True)

# 인기 게임 TOP 10 (긍정 리뷰 기준)
st.header("🔥 인기 게임 TOP 10 (긍정 리뷰 수 기준)")
if "positive_ratings" in steam.columns:
    top10 = steam.sort_values(by="positive_ratings", ascending=False).head(10)
    st.dataframe(top10[['name', 'positive_ratings', 'price']])
else:
    st.warning("⚠️ 'positive_ratings' 컬럼이 없어 인기 순위를 표시할 수 없습니다.")

# 가격 대비 리뷰 시각화
st.header("💰 가격 대비 긍정 리뷰 수")
if all(col in steam.columns for col in ["positive_ratings", "price"]):
    chart_data = steam[steam['price'] > 0]
    chart = alt.Chart(chart_data).mark_circle(size=60).encode(
        x='price',
        y='positive_ratings',
        tooltip=['name', 'price', 'positive_ratings']
    ).interactive()
    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("시각화를 위한 데이터가 부족합니다.")

# 장르별 게임 수
st.header("📚 장르별 게임 수")
def count_genres(genres_series):
    genre_list = []
    for genres in genres_series.dropna():
        genre_list.extend([g.strip() for g in genres.split(',')])
    return pd.DataFrame(Counter(genre_list).items(), columns=['Genre', 'Count']).sort_values(by='Count', ascending=False)

genre_df = count_genres(steam['genres'])
st.bar_chart(genre_df.set_index('Genre'))

# 태그 수 많은 게임 TOP 10
st.header("🏷️ 가장 많은 태그를 가진 게임 TOP 10")
if "tags" in steam.columns:
    tag_counts = steam.copy()
    tag_counts['tag_count'] = tag_counts['tags'].apply(lambda x: len(str(x).split(',')) if pd.notna(x) else 0)
    top_tags = tag_counts.sort_values(by='tag_count', ascending=False).head(10)
    st.dataframe(top_tags[['name', 'tag_count', 'tags']])
else:
    st.warning("태그 데이터가 없어 표시할 수 없습니다.")
