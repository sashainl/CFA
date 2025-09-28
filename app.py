import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import io
import base64

# 페이지 설정
st.set_page_config(
    page_title="고객 피드백 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 감성 분석 함수 (간단한 키워드 기반)
def analyze_sentiment(text):
    """간단한 키워드 기반 감성 분석"""
    if pd.isna(text) or text == '':
        return '중립'
    
    text = str(text).lower()
    
    # 긍정 키워드
    positive_words = ['좋다', '좋은', '만족', '훌륭', '최고', '감사', '추천', '훌륭한', 
                     '빠르다', '빠른', '편리', '편한', '친절', '도움', '해결', '완벽']
    
    # 부정 키워드
    negative_words = ['나쁘다', '나쁜', '불만', '문제', '느리다', '느린', '불편', '어려움',
                     '실망', '화나다', '짜증', '복잡', '오류', '오래', '지연', '불친절']
    
    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)
    
    if positive_count > negative_count:
        return '긍정'
    elif negative_count > positive_count:
        return '부정'
    else:
        return '중립'

# 키워드 추출 함수
def extract_keywords(text, top_n=20):
    """텍스트에서 키워드 추출"""
    if pd.isna(text) or text == '':
        return []
    
    # 한글, 영문, 숫자만 추출
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', str(text))
    words = text.split()
    
    # 불용어 제거 (간단한 버전)
    stopwords = ['그', '이', '저', '것', '들', '의', '가', '을', '를', '에', '와', '과', '로', '으로',
                 '는', '은', '도', '만', '부터', '까지', '에서', '에게', '한테', '께', '서', '부터']
    
    words = [word for word in words if len(word) > 1 and word not in stopwords]
    
    return words

# 워드클라우드 생성 함수
def create_wordcloud(text_data):
    """워드클라우드 생성"""
    all_text = ' '.join(text_data.dropna().astype(str))
    words = extract_keywords(all_text, top_n=100)
    
    if not words:
        return None
    
    word_freq = Counter(words)
    
    # 워드클라우드 생성
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        font_path=None,  # 한글 폰트가 없으면 기본 폰트 사용
        max_words=50,
        colormap='viridis'
    ).generate_from_frequencies(word_freq)
    
    return wordcloud

# 메인 앱
def main():
    st.title("📊 고객 피드백 분석 대시보드")
    st.markdown("---")
    
    # 사이드바
    st.sidebar.title("📁 데이터 업로드")
    
    # 파일 업로드
    uploaded_file = st.sidebar.file_uploader(
        "CSV 또는 Excel 파일을 업로드하세요",
        type=['csv', 'xlsx', 'xls'],
        help="피드백 데이터가 포함된 파일을 업로드하세요"
    )
    
    # 샘플 데이터 사용 옵션
    use_sample = st.sidebar.checkbox("샘플 데이터 사용", value=True)
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.sidebar.success(f"✅ 파일 업로드 완료: {uploaded_file.name}")
            st.sidebar.info(f"📊 총 {len(df)}개의 피드백 데이터")
            
        except Exception as e:
            st.sidebar.error(f"❌ 파일 읽기 오류: {str(e)}")
            df = None
    elif use_sample:
        # 샘플 데이터 생성
        sample_data = {
            'date': pd.date_range('2024-01-01', periods=100, freq='D'),
            'feedback': [
                '서비스가 정말 좋습니다. 직원분들이 친절하시고 빠르게 해결해주셨어요.',
                '배송이 너무 느려서 불만입니다. 다음에는 더 빨리 배송해주세요.',
                '제품 품질은 만족스럽지만 가격이 조금 비싸네요.',
                '고객센터 응답이 빠르고 친절해서 감사합니다.',
                '웹사이트가 복잡해서 주문하기 어려웠습니다.',
                '제품이 예상보다 훨씬 좋아서 만족합니다.',
                '배송 과정에서 제품이 손상되었습니다.',
                '할인 혜택이 많아서 좋았습니다.',
                '로그인이 자꾸 안되어서 불편했습니다.',
                '상품 설명이 자세해서 구매 결정에 도움이 되었습니다.'
            ] * 10,
            'rating': np.random.randint(1, 6, 100),
            'category': np.random.choice(['배송', '품질', '서비스', '가격', '기타'], 100)
        }
        df = pd.DataFrame(sample_data)
        st.sidebar.info("📊 샘플 데이터를 사용합니다")
    else:
        st.info("👆 사이드바에서 파일을 업로드하거나 샘플 데이터를 사용하세요.")
        return
    
    if df is not None and not df.empty:
        # 데이터 전처리
        st.header("📋 데이터 미리보기")
        
        # 컬럼 선택
        col1, col2 = st.columns(2)
        
        with col1:
            text_column = st.selectbox(
                "피드백 텍스트 컬럼 선택",
                df.columns.tolist(),
                help="감성 분석할 텍스트 컬럼을 선택하세요"
            )
        
        with col2:
            date_column = st.selectbox(
                "날짜 컬럼 선택 (선택사항)",
                ['없음'] + df.columns.tolist(),
                help="날짜 필터링을 위한 컬럼을 선택하세요"
            )
        
        if date_column != '없음':
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        
        # 데이터 미리보기
        st.dataframe(df.head(10), use_container_width=True)
        
        # 감성 분석 실행
        st.header("🎭 감성 분석 결과")
        
        # 감성 분석
        df['sentiment'] = df[text_column].apply(analyze_sentiment)
        
        # 감성 분포 시각화
        col1, col2 = st.columns(2)
        
        with col1:
            # 감성 분포 파이 차트
            sentiment_counts = df['sentiment'].value_counts()
            fig_pie = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="감성 분포",
                color_discrete_map={'긍정': '#2E8B57', '부정': '#DC143C', '중립': '#4682B4'}
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # 감성 분포 막대 차트
            fig_bar = px.bar(
                x=sentiment_counts.index,
                y=sentiment_counts.values,
                title="감성별 피드백 수",
                color=sentiment_counts.index,
                color_discrete_map={'긍정': '#2E8B57', '부정': '#DC143C', '중립': '#4682B4'}
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # 키워드 분석
        st.header("🔍 키워드 분석")
        
        # 키워드 추출
        all_keywords = []
        for text in df[text_column].dropna():
            keywords = extract_keywords(text)
            all_keywords.extend(keywords)
        
        keyword_counts = Counter(all_keywords)
        top_keywords = dict(keyword_counts.most_common(20))
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 상위 키워드 막대 차트
            if top_keywords:
                fig_keywords = px.bar(
                    x=list(top_keywords.values()),
                    y=list(top_keywords.keys()),
                    orientation='h',
                    title="상위 키워드 (빈도)",
                    color=list(top_keywords.values()),
                    color_continuous_scale='viridis'
                )
                fig_keywords.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_keywords, use_container_width=True)
        
        with col2:
            # 워드클라우드
            st.subheader("워드클라우드")
            wordcloud = create_wordcloud(df[text_column])
            if wordcloud:
                fig_wc, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig_wc)
            else:
                st.info("워드클라우드를 생성할 수 없습니다.")
        
        # 시간별 분석 (날짜 컬럼이 있는 경우)
        if date_column != '없음' and not df[date_column].isna().all():
            st.header("📅 시간별 분석")
            
            # 월별 감성 분포
            df['month'] = df[date_column].dt.to_period('M')
            monthly_sentiment = df.groupby(['month', 'sentiment']).size().unstack(fill_value=0)
            
            fig_monthly = px.line(
                monthly_sentiment,
                title="월별 감성 분포 변화",
                color_discrete_map={'긍정': '#2E8B57', '부정': '#DC143C', '중립': '#4682B4'}
            )
            fig_monthly.update_layout(xaxis_title="월", yaxis_title="피드백 수")
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        # 상세 분석
        st.header("📊 상세 분석")
        
        # 감성별 피드백 샘플
        sentiment_tabs = st.tabs(['긍정 피드백', '부정 피드백', '중립 피드백'])
        
        with sentiment_tabs[0]:
            positive_feedback = df[df['sentiment'] == '긍정'][text_column].head(10)
            for i, feedback in enumerate(positive_feedback, 1):
                st.write(f"{i}. {feedback}")
        
        with sentiment_tabs[1]:
            negative_feedback = df[df['sentiment'] == '부정'][text_column].head(10)
            for i, feedback in enumerate(negative_feedback, 1):
                st.write(f"{i}. {feedback}")
        
        with sentiment_tabs[2]:
            neutral_feedback = df[df['sentiment'] == '중립'][text_column].head(10)
            for i, feedback in enumerate(neutral_feedback, 1):
                st.write(f"{i}. {feedback}")
        
        # 요약 통계
        st.header("📈 요약 통계")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 피드백 수", len(df))
        
        with col2:
            positive_rate = (df['sentiment'] == '긍정').sum() / len(df) * 100
            st.metric("긍정 비율", f"{positive_rate:.1f}%")
        
        with col3:
            negative_rate = (df['sentiment'] == '부정').sum() / len(df) * 100
            st.metric("부정 비율", f"{negative_rate:.1f}%")
        
        with col4:
            neutral_rate = (df['sentiment'] == '중립').sum() / len(df) * 100
            st.metric("중립 비율", f"{neutral_rate:.1f}%")
        
        # 다운로드 기능
        st.header("💾 결과 다운로드")
        
        # 분석 결과를 CSV로 다운로드
        result_df = df.copy()
        result_df['감성분석결과'] = result_df['sentiment']
        
        csv = result_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 분석 결과 CSV 다운로드",
            data=csv,
            file_name=f"feedback_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
