import streamlit as st
from google import genai
from google.genai import types
import json

# ---------------------------------------------------------
# 1. 페이지 기본 설정 (밝고 상큼한 레이아웃)
# ---------------------------------------------------------
st.set_page_config(
    page_title="바른 한글 - 맞춤법 검사기",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. 커스텀 CSS (밝고 화사한 디자이너 스타일 커스텀 테마)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* 배경 및 기본 폰트 */
    .stApp {
        background-color: #FAFAFE;
    }
    
    /* 타이틀 스타일 */
    .main-title {
        color: #4F46E5;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #6B7280;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    /* 카드 스타일 컨테이너 */
    .custom-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid #EEF2FF;
        margin-bottom: 20px;
    }

    /* 교정 완료 강조 박스 */
    .corrected-box {
        background-color: #F0FDF4;
        border: 1.5px solid #86EFAC;
        border-radius: 12px;
        padding: 18px;
        color: #166534;
        font-size: 1.1rem;
        line-height: 1.6;
        white-space: pre-wrap;
    }

    /* 통계/정보 배지 */
    .stat-badge {
        display: inline-block;
        background-color: #EEF2FF;
        color: #4F46E5;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 3. Gemini API 클라이언트 초기화 함수
# ---------------------------------------------------------
def get_gemini_client():
    """st.secrets에서 GEMINI_API_KEY를 읽어 Client를 생성합니다."""
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        return genai.Client(api_key=api_key)
    else:
        st.error("🔑 `GEMINI_API_KEY`가 설정되지 않았습니다. Streamlit Secrets 설정을 확인해주세요.")
        st.stop()


# ---------------------------------------------------------
# 4. Gemini 맞춤법 검사 로직
# ---------------------------------------------------------
def check_spelling(client, text, tone_option):
    prompt = f"""
    당신은 대한민국 최고의 한국어 감수자 및 맞춤법 전문가입니다.
    아래 [원문 입력]을 분석하여 맞춤법, 띄어쓰기, 문맥에 맞는 어휘, 표준어를 교정해주세요.

    [문체 요청]
    - 원문의 톤앤매너(문체)를 그대로 유지하면서 교정해주세요. (옵션 선택값: {tone_option})

    [원문 입력]
    {text}

    [응답 규칙]
    반드시 아래 JSON 형식으로만 정확히 응답해주세요. 마크다운(` ```json ` 등)을 포함하지 마세요.
    {{
        "corrected_text": "교정된 전체 문장",
        "has_errors": true 또는 false (오류 존재 여부),
        "corrections": [
            {{
                "original": "틀린 단어/문구",
                "corrected": "고친 단어/문구",
                "reason": "고친 이유 (간결하고 친절하게 설명)"
            }}
        ]
    }}
    """

    # 사용할 Gemini 모델 목록 (오류 발생 시 자동으로 호환 모델로 시도)
    models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash']

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            # JSON 파싱
            result = json.loads(response.text)
            return result
        except Exception as e:
            # 마지막 모델까지 실패한 경우 오류 메시지 출력
            if model_name == models_to_try[-1]:
                st.error(f"⚠️ 맞춤법 검사 중 오류가 발생했습니다: {str(e)}")
                return None


# ---------------------------------------------------------
# 5. UI 구성 및 메인 앱 실행
# ---------------------------------------------------------
def main():
    # 사이드바 구성
    with st.sidebar:
        st.title("✨ 바른 한글 도우미")
        st.write("밝고 깨끗한 한글 맞춤법 교정기입니다.")
        st.divider()
        
        tone_option = st.selectbox(
            "🎨 문체 유지 옵션",
            ["원문 톤 유지", "존댓말(~해요 / ~습니다)", "반말 / 일기체", "비즈니스 / 격식체"]
        )
        
        st.markdown("---")
        st.markdown("### 💡 사용 팁")
        st.info(
            "- 오탈자, 띄어쓰기, 문맥에 맞는 맞춤법을 한번에 정밀 교정합니다.\n"
            "- '수정 사유 카드'를 통해 왜 틀렸는지 쉽게 배울 수 있습니다.\n"
            "- 우측 상단 상자에서 교정된 글을 간편하게 복사하세요!"
        )

    # 메인 헤더
    st.markdown('<div class="main-title">✨ 스마트 한글 맞춤법 검사기</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Gemini AI가 문맥을 파악하여 바르고 고운 한글로 다듬어 드립니다.</div>', unsafe_allow_html=True)

    # 입력 레이아웃
    col_input, col_output = st.columns([1, 1], gap="medium")

    with col_input:
        st.subheader("📝 원문 입력")
        user_input = st.text_area(
            label="검사할 문장을 입력하세요",
            placeholder="예시: 대화가 끈켜서 어의가 없었지만 일단 오랫만에 만난 동창이라 서둘러 일어났다.",
            height=280,
            label_visibility="collapsed"
        )

        # 글자 수 정보 표시
        char_count = len(user_input)
        word_count = len(user_input.split()) if user_input.strip() else 0
        
        st.markdown(
            f'<span class="stat-badge">글자 수: {char_count}자</span>'
            f'<span class="stat-badge">단어 수: {word_count}개</span>',
            unsafe_allow_html=True
        )
        
        st.write("")
        submit_btn = st.button("✨ 맞춤법 검사하기", type="primary", use_container_width=True)

    with col_output:
        st.subheader("🎯 교정 결과")

        if submit_btn:
            if not user_input.strip():
                st.warning("검사할 문장을 먼저 입력해주세요!")
            else:
                with st.spinner("맞춤법과 문맥을 세심하게 다듬는 중..."):
                    client = get_gemini_client()
                    res = check_spelling(client, user_input, tone_option)

                    if res:
                        st.session_state['result'] = res
                        st.session_state['original_text'] = user_input

        # 결과 출력 (세션 상태 활용)
        if 'result' in st.session_state and st.session_state['result']:
            result = st.session_state['result']
            corrected_text = result.get("corrected_text", "")
            has_errors = result.get("has_errors", False)
            corrections = result.get("corrections", [])

            # 교정된 결과 박스
            st.markdown(f'<div class="corrected-box">{corrected_text}</div>', unsafe_allow_html=True)
            st.write("")

            if not has_errors or len(corrections) == 0:
                st.success("🎉 완벽합니다! 수정할 맞춤법이나 띄어쓰기가 없습니다.")
            else:
                st.markdown(f"**총 {len(corrections)}개의 부분이 교정되었습니다.**")
                
                # 상세 수정 이유 리스트
                for idx, item in enumerate(corrections, 1):
                    with st.expander(f"📍 [{idx}] '{item.get('original')}' ➡️ '{item.get('corrected')}'", expanded=True):
                        st.write(f"**이유:** {item.get('reason')}")

        else:
            st.info("왼쪽 상자에 내용을 입력하고 [맞춤법 검사하기] 버튼을 눌러주세요.")


if __name__ == "__main__":
    main()
