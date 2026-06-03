import streamlit as st
import requests
import pandas as pd
import os

# [필수 수정] TMDB에서 발급받은 실제 API Key를 여기에 넣으세요!
TMDB_API_KEY = "58f2261373af584bb80e4f48936da934" 

st.set_page_config(page_title="중국 영화 거장 숨은 명작 추천", page_icon="🎬", layout="centered")
st.title("🎬 중국 영화 거장 '숨은 명작' 추천 서비스")
st.write("크롤링한 전체 감독 리스트에서 대표작을 제외한 숨은 명작을 찾아줍니다.")
st.write("---")

# 1. 파일 읽어오기 (완벽하게 정렬된 부분)
csv_path = "directors.csv"

if not os.path.exists(csv_path):
    st.error(f"⚠️ 지정된 경로에 파일이 없습니다! 경로를 확인해 주세요: {csv_path}")
else:
    # CSV 파일 읽기 (한글 깨짐 방지를 위해 인코딩 설정)
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding='cp949')

    # 2. 감독 선택창 만들기 (크롤링한 모든 감독이 가나다순으로 등장합니다)
    df = df.dropna(subset=['한국어발음', 'TMDB_ID']) # 빈 데이터 제거
    director_list = sorted(df['한국어발음'].unique())
    selected_director = st.selectbox("분석할 감독을 선택하세요:", director_list)

    if selected_director:
        # 선택된 감독의 상세 정보 가져오기
        director_info = df[df['한국어발음'] == selected_director].iloc[0]
        
        director_id = int(director_info['TMDB_ID'])
        generation = director_info['세대']
        
        # 대표작 3편 텍스트 정제
        raw_known = str(director_info['대표작3편'])
        known_movies = [m.strip() for m in raw_known.replace('；', ';').replace(',', ';').replace('?', ';').split(';') if m.strip()]
        
        st.subheader(f"🧐 {selected_director} 감독 ({generation})")
        st.write(f"**알려진 대표작:** {', '.join(known_movies) if known_movies else '등록된 대표작 없음'}")
        
        # 3. TMDB API 호출 버튼
        if st.button(f"{selected_director} 감독의 숨은 명작 찾기 🚀"):
            with st.spinner("TMDB에서 영화 데이터를 분석하는 중..."):
                
                url = f"https://api.themoviedb.org/3/person/{director_id}/movie_credits?api_key={TMDB_API_KEY}&language=ko-KR"
                response = requests.get(url).json()
                all_movies = response.get('crew', [])
                
                hidden_gems = []
                
                for movie in all_movies:
                    if movie.get('job') == 'Director':
                        title = movie.get('title')
                        rating = movie.get('vote_average')
                        vote_count = movie.get('vote_count')
                        release_date = movie.get('release_date', '연도 미상')
                        poster_path = movie.get('poster_path')
                        overview = movie.get('overview', '등록된 줄거리가 없습니다.')
                        
                        # 내 크롤링 데이터의 대표작 목록에 없는 영화 + 투표수 3개 이상 필터링 (초기 데이터 확보용)
                        if title not in known_movies and vote_count >= 3:
                            hidden_gems.append({
                                "title": title,
                                "rating": rating,
                                "vote_count": vote_count,
                                "date": release_date[:4] if release_date else "미상",
                                "poster": f"https://image.tmdb.org/t/p/w200{poster_path}" if poster_path else None,