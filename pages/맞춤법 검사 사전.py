import json
import streamlit as st
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. 페이지 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="바른 한글 - 맞춤법 검사기",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. 화사한 밝은 테마 커스텀 CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #FAFAFE;
    }
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
# 3. Gemini API 클라이언트 로드
# ---------------------------------------------------------
def get_gemini_client():
    if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"].strip():
        return genai.Client(api_key=st.secrets["GEMINI_API_KEY"].strip())
    else:
        st.error("🔑 Streamlit Secrets에 `GEMINI_API_KEY`가 설정되어 있지 않습니다. App Settings > Secrets에서 키를 입력해주세요.")
        st.stop()


# ---------------------------------------------------------
# 4. 맞춤법 검사 핵심 함수 (안정적인 구조)
# ---------------------------------------------------------
def check_spelling(client, text, tone_option):
    prompt = f"""
    당신은 대한민국 최고의 한국어 감수자 및 맞춤법 전문가입니다.
    아래 [원문 입력]을 분석하여 맞춤법, 띄어쓰기, 문맥에 맞는 어휘, 표준어를 교정해주세요.

    [문체 요청]
    - 원문의 톤앤매너(문체)를 그대로 유지하면서 교정해주세요. (옵션: {tone_option})

    [원문 입력]
    {text}

    [응답 규칙]
    반드시 아래 JSON 형식으로만 응답해주세요.
    {{
        "corrected_text": "교정된 전체 문장",
        "has_errors": true 또는 false,
        "corrections": [
            {{
                "original": "틀린 단어/문구",
                "corrected": "고친 단어/문구",
                "reason": "고친 이유 설명"
            }}
        ]
    }}
    """

    try:
        # 최신 안정화 모델 사용
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        
        # 텍스트 정제 후 JSON 파싱
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "", 1).rstrip("`").strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "", 1).rstrip("`").strip()
            
        return json.loads(raw_text)

    except Exception as e:
        st.error(f"⚠️ 맞춤법 검사 호출 중 오류가 발생했습니다: {str(e)}")
        return None


# ---------------------------------------------------------
# 5. UI 및 실행 메인 함수
# ---------------------------------------------------------
def main():
    # 사이드바
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
            "- 오탈자, 띄어쓰기, 문맥 맞춤법을 세심하게 다듬어 줍니다.\n"
            "- 수정된 이유를 카드로 확인해 보세요!"
        )

    # 헤더
    st.markdown('<div class="main-title">✨ 스마트 한글 맞춤법 검사기</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Gemini AI가 문맥을 파악하여 바르고 고운 한글로 다듬어 드립니다.</div>', unsafe_allow_html=True)

    # 본문 2열 레이아웃
    col_input, col_output = st.columns([1, 1], gap="medium")

    with col_input:
        st.subheader("📝 원문 입력")
        user_input = st.text_area(
            label="검사할 문장을 입력하세요",
            placeholder="예시: 대화가 끈켜서 어의가 없었지만 일단 오랫만에 만난 동창이라 서둘러 일어났다.",
            height=280,
            label_visibility="collapsed"
        )

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
                st.warning("검사할 문장을 입력해 주세요!")
            else:
                with st.spinner("맞춤법과 문맥을 세심하게 다듬는 중..."):
                    client = get_gemini_client()
                    res = check_spelling(client, user_input, tone_option)

                    if res:
                        st.session_state['result'] = res

        # 결과 표시
        if 'result' in st.session_state and st.session_state['result']:
            result = st.session_state['result']
            corrected_text = result.get("corrected_text", "")
            has_errors = result.get("has_errors", False)
            corrections = result.get("corrections", [])

            st.markdown(f'<div class="corrected-box">{corrected_text}</div>', unsafe_allow_html=True)
            st.write("")

            if not has_errors or len(corrections) == 0:
                st.success("🎉 완벽합니다! 수정할 맞춤법이나 띄어쓰기가 없습니다.")
            else:
                st.markdown(f"**총 {len(corrections)}개의 부분이 교정되었습니다.**")
                for idx, item in enumerate(corrections, 1):
                    with st.expander(f"📍 [{idx}] '{item.get('original', '')}' ➡️ '{item.get('corrected', '')}'", expanded=True):
                        st.write(f"**이유:** {item.get('reason', '')}")
        else:
            st.info("왼쪽 상자에 내용을 입력하고 [맞춤법 검사하기] 버튼을 눌러주세요.")


if __name__ == "__main__":
    main()
