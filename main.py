import streamlit as st
import pandas as pd

# CSV 파일 불러오기 (GitHub 등에서 불러올 수 있음 - 여기선 로컬로 가정)
steam_df = pd.read_csv("steam.csv")              # 게임 기본 정보 데이터
tags_df = pd.read_csv("steamspy_tag_data.csv")   # 게임 태그 데이터

# 게임 ID(appid)를 기준으로 태그 데이터 병합
steam_df = steam_df.merge(tags_df, on="appid", how="left")

# Streamlit 페이지 설정
st.set_page_config(page_title="Steam 게임 탐색기", layout="wide")
st.title("🎮 Steam 게임 탐색기")

# 각 게임의 장르 문자열을 분해하여 유니크한 장르 리스트 추출하는 함수
def extract_unique_genres(df):
    genre_set = set()  # 중복 제거를 위한 set 사용
    for genres in df['genres'].dropna():
        for g in str(genres).split(';'):  # 세미콜론으로 구분된 장르 분리
            genre_set.add(g.strip())      # 양쪽 공백 제거 후 추가
    return sorted(list(genre_set))        # 알파벳 순 정렬 후 리스트 반환

unique_genres = extract_unique_genres(steam_df)  # 전체 장르 추출

# 사이드바 필터 영역
with st.sidebar:
    st.header("🔍 필터")
    
    # 게임 이름으로 검색
    name_query = st.text_input("게임 이름 검색")
    
    # 개발사 필터 (중복 제거 및 NaN 제거)
    developer_filter = st.multiselect(
        "개발사 선택",
        options=steam_df['developer'].dropna().unique()
    )
    
    # 장르 필터 (유저가 여러 장르를 선택할 수 있음)
    genre_filter = st.multiselect(
        "장르 태그 선택 (다중 선택 가능)",
        options=unique_genres
    )
    
    # 가격 범위 슬라이더 설정 (최대값은 데이터 내 최대 가격 기준)
    price_max = int(steam_df['price'].max())
    price_range = st.slider(
        "가격 범위", 0, price_max, (0, price_max), step=1
    )

# 필터를 적용하여 데이터프레임 필터링
filtered_df = steam_df.copy()

# 이름 필터 적용 (대소문자 무시, NaN 방지)
if name_query:
    filtered_df = filtered_df[filtered_df['name'].str.contains(name_query, case=False, na=False)]

# 개발사 필터 적용
if developer_filter:
    filtered_df = filtered_df[filtered_df['developer'].isin(developer_filter)]

# 장르 필터 적용
if genre_filter:
    filtered_df = filtered_df[
        filtered_df['genres'].apply(
            lambda g: all(tag in str(g).split(';') for tag in genre_filter)
        )
    ]

# 가격 범위 필터 적용
filtered_df = filtered_df[
    (filtered_df['price'] >= price_range[0]) & 
    (filtered_df['price'] <= price_range[1])
]

# 필터링된 결과 개수 표시 및 주요 정보 테이블 출력
st.subheader(f"🎯 총 {len(filtered_df)}개의 게임이 검색되었습니다.")
st.dataframe(
    filtered_df[
        ['name', 'release_date', 'developer', 'genres', 'price', 'positive_ratings', 'negative_ratings', 'average_playtime']
    ],
    use_container_width=True,   # 전체 너비 사용
    height=400                  # 테이블 높이 지정
)

# 상세 정보 보기 섹션
st.subheader("🔎 게임 상세 정보 보기")

# 필터된 게임 중 하나를 선택할 수 있는 드롭다운
selected_game = st.selectbox("게임 선택", filtered_df['name'].unique())

# 선택된 게임의 정보 추출 (첫 번째 행 선택)
detail = filtered_df[filtered_df['name'] == selected_game].iloc[0]

# 상세 정보 출력 (2열 레이아웃)
with st.container():
    col1, col2 = st.columns([1, 1])
    with col1:
        # 왼쪽 열: 텍스트 정보
        st.markdown(f"**🧾 이름:** {detail['name']}")
        st.markdown(f"**🛠 개발사:** {detail['developer']}")
        st.markdown(f"**📅 출시일:** {detail['release_date']}")
        st.markdown(f"**💰 가격:** ${detail['price']}")
        st.markdown(f"**👍 추천:** {detail['positive_ratings']} / 👎 비추천: {detail['negative_ratings']}")
        st.markdown(f"**⏱ 평균 플레이타임:** {detail['average_playtime']} 분")
    with col2:
        # 오른쪽 열: 현재는 빈 공간 (향후 이미지, 태그 시각화 등 추가 가능)
        st.empty()
