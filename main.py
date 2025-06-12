import streamlit as st
import pandas as pd
import altair as alt
from collections import Counter
import os

st.set_page_config(layout="wide")
st.title("🎮 Steam 게임 탐색기 (폴더 기반)")

# 1. 폴더 경로 설정
folder_url = "https://drive.google.com/drive/folders/11TcvW7kPMzV2dEt591jWUma3wFr9VTpl?usp=sharing"
st.markdown(f"**📁 데이터 폴더:** {folder_url}")

# 2. 파일 업로드 방식 대신 폴더에서 직접 읽기
# Streamlit Cloud에서는 git 리포지토리에 이 폴더를 복제해야 함
DATA_DIR = "data"  # 실제 파일 위치에 맞게 조정하세요

@st.cache_data
def load_local_files():
    steam_path = os.path.join(DATA_DIR, "steam.csv")
    desc_path = os.path.join(DATA_DIR, "steam_description_data.csv")
    media_path = os.path.join(DATA_DIR, "steam_media_data.csv")
    tags_path = os.path.join(DATA_DIR, "steamspy_tag_data.csv")
    support_path = os.path.join(DATA_DIR, "steam_support_info.csv")
    req_path = os.path.join(DATA_DIR, "steam_requirements_data.csv")

    dfs = {}
    for key, path in [
        ("steam", steam_path),
        ("desc", desc_path),
        ("media", media_path),
        ("tags", tags_path),
        ("support", support_path),
        ("require", req_path),
    ]:
        if os.path.exists(path):
            dfs[key] = pd.read_csv(path)
            dfs[key].columns = dfs[key].columns.str.strip().str.lower()
        else:
            dfs[key] = pd.DataFrame()
    return dfs

dfs = load_local_files()
steam, desc, media, tags, support, require = (
    dfs["steam"],
    dfs["desc"],
    dfs["media"],
    dfs["tags"],
    dfs["support"],
    dfs["require"],
)

# 3. 컬럼 확인
st.write("📋 steam.csv 컬럼 목록:", list(steam.columns))

# 4. 게임 검색
search = st.text_input("🔍 게임 이름 검색")
if search and "name" in steam.columns:
    filtered = steam[steam["name"].str.contains(search, case=False, na=False)]
    if not filtered.empty:
        game = filtered.iloc[0]
        st.subheader(game["name"])
        st.write(f"**출시일:** {game.get('release_date', 'N/A')}")
        st.write(f"**가격:** ${game.get('price', 0):.2f}")

        # 설명
        if "steam_appid" in desc.columns:
            desc_row = desc[desc["steam_appid"] == game["appid"]]
            if not desc_row.empty and "short_description" in desc.columns:
                st.markdown(f"**설명:** {desc_row.iloc[0]['short_description']}")

        # 이미지
        if "steam_appid" in media.columns and "header_image" in media.columns:
            media_row = media[media["steam_appid"] == game["appid"]]
            if not media_row.empty:
                st.image(media_row.iloc[0]["header_image"], use_column_width=True)

# 5. 인기 게임 TOP 10
st.header("🔥 인기 게임 TOP 10 (positive_ratings 기준)")
if "positive_ratings" in steam.columns:
    top10 = steam.sort_values(by="positive_ratings", ascending=False).head(10)
    st.dataframe(top10[["name", "positive_ratings"]])
else:
    st.warning("⚠️ 'positive_ratings' 컬럼이 없습니다.")

# 6. 가격 대비 긍정 리뷰
st.header("💰 가격 대비 긍정 리뷰 비율")
if all(col in steam.columns for col in ["price", "positive_ratings"]):
    steam["value_ratio"] = steam["positive_ratings"] / (steam["price"] + 1e-6)
    chart = alt.Chart(steam.sort_values(by="value_ratio", ascending=False).head(20)).mark_bar().encode(
        x="name:N", y="value_ratio:Q", tooltip=["name", "price", "positive_ratings"]
    ).properties(width=800)
    st.altair_chart(chart, use_container_width=True)
else:
    st.warning("시각화에 필요한 컬럼이 없습니다.")

# 7. 장르별 분포
st.header("📚 장르별 게임 수")
if "genres" in steam.columns:
    cnt = Counter()
    for row in steam["genres"].dropna():
        for g in row.split(";"):
            cnt[g.strip()] += 1
    genre_df = pd.DataFrame(cnt.items(), columns=["genre", "count"]).sort_values(by="count", ascending=False)
    st.bar_chart(genre_df.set_index("genre"))
else:
    st.warning("⚠️ 'genres' 컬럼이 없습니다.")

# 8. 태그 TOP 10
st.header("🏷️ 태그 많은 게임 TOP 10")
if "steamspy_tags" in steam.columns:
    steam["tag_count"] = steam["steamspy_tags"].fillna("").apply(lambda x: len(x.split(";")))
    top_tags = steam.sort_values(by="tag_count", ascending=False).head(10)
    st.dataframe(top_tags[["name", "tag_count", "steamspy_tags"]])
else:
    st.warning("⚠️ 'steamspy_tags' 컬럼이 없습니다.")
