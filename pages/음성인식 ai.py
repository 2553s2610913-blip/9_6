
import streamlit as st
import speech_recognition as sr
from korector import NaverSpellChecker
import io

# ==================================
# 1. 페이지 설정
# ==================================

st.set_page_config(
    page_title="수빈의 음성인식 AI",
    page_icon="🎙️",
    layout="centered"
)

# ==================================
# 2. 스타일 설정
# ==================================

st.markdown("""
<style>
.stApp {
    background-color: #f5f7fb;
}

h1 {
    text-align: center;
    color: #243b64;
}

.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 16px;
}

.stButton > button {
    width: 100%;
    border-radius: 10px;
    height: 48px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ==================================
# 3. 검사기 불러오기
# ==================================

@st.cache_resource
def load_checker():
    return NaverSpellChecker()

# ==================================
# 4. 제목
# ==================================

st.title("🎙️ 수빈의 음성인식 AI")

st.markdown(
    '<p class="subtitle">음성을 텍스트로 변환하고 맞춤법까지 교정하는 AI</p>',
    unsafe_allow_html=True
)

st.divider()

# ==================================
# 5. 세션 초기화
# ==================================

if "recognized_text" not in st.session_state:
    st.session_state.recognized_text = ""

if "corrected_text" not in st.session_state:
    st.session_state.corrected_text = ""

if "error_count" not in st.session_state:
    st.session_state.error_count = 0

# ==================================
# 6. 음성 파일 업로드
# ==================================

st.subheader("🎤 음성 인식")

audio_file = st.file_uploader(
    "음성 파일을 선택하세요.",
    type=["wav", "aiff", "aif", "flac"]
)

if st.button("음성 인식 시작"):

    if audio_file is None:
        st.warning("음성 파일을 먼저 업로드해 주세요.")

    else:
        try:
            recognizer = sr.Recognizer()

            with st.spinner("음성을 분석하고 있습니다..."):

                audio_bytes = audio_file.getvalue()

                with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                    audio_data = recognizer.record(source)

                recognized = recognizer.recognize_google(
                    audio_data,
                    language="ko-KR"
                )

                st.session_state.recognized_text = recognized
                st.session_state.corrected_text = ""

            st.success("음성 인식 완료!")

        except sr.UnknownValueError:
            st.error("음성을 이해하지 못했습니다.")

        except sr.RequestError as e:
            st.error("음성 인식 서버 연결에 실패했습니다.")
            st.exception(e)

        except Exception as e:
            st.error("음성 인식 중 오류가 발생했습니다.")
            st.exception(e)

# ==================================
# 7. 음성 인식 결과
# ==================================

if st.session_state.recognized_text:

    st.markdown("### 📝 인식된 문장")

    st.text_area(
        "음성 인식 결과",
        value=st.session_state.recognized_text,
        height=120,
        key="recognized_display"
    )

# ==================================
# 8. 직접 텍스트 입력
# ==================================

st.divider()

st.subheader("⌨️ 텍스트 입력")

manual_text = st.text_area(
    "검사할 문장을 입력하세요.",
    placeholder="예: 안녕하세요 저는 고등학교 학생 입니다.",
    height=150,
    key="manual_input"
)

# 입력 문장 우선, 없으면 음성 인식 결과 사용
text_to_check = (
    manual_text.strip()
    or st.session_state.recognized_text.strip()
)

# ==================================
# 9. 맞춤법 검사
# ==================================

st.divider()

st.subheader("🔎 맞춤법 검사")

if st.button("맞춤법 검사하기"):

    if not text_to_check:
        st.warning("검사할 문장을 입력해 주세요.")

    else:
        try:
            with st.spinner("맞춤법을 검사하고 있습니다..."):

                checker = load_checker()
                result = checker.check(text_to_check)

            if isinstance(result, dict) and result.get("success"):

                corrected = result.get(
                    "corrected",
                    text_to_check
                )

                errors = result.get("error_count", 0)

                st.session_state.corrected_text = corrected
                st.session_state.error_count = errors

                st.success("맞춤법 검사 완료!")

            else:
                st.error("맞춤법 검사 결과를 가져오지 못했습니다.")
                st.write("서버 응답:", result)

        except Exception as e:
            st.error("맞춤법 검사 중 오류가 발생했습니다.")
            st.exception(e)

# ==================================
# 10. 교정 결과
# ==================================

if st.session_state.corrected_text:

    st.divider()

    st.subheader("✨ 최종 교정 결과")

    st.text_area(
        "교정된 문장",
        value=st.session_state.corrected_text,
        height=150,
        key="corrected_display"
    )

    st.metric(
        label="발견된 오류 수",
        value=st.session_state.error_count
    )

    st.download_button(
        label="📥 교정 결과 다운로드",
        data=st.session_state.corrected_text,
        file_name="맞춤법_교정결과.txt",
        mime="text/plain"
    )

# ==================================
# 11. 초기화
# ==================================

st.divider()

if st.button("🔄 전체 초기화"):

    st.session_state.clear()
    st.rerun()

# ==================================
# 12. 하단 안내
# ==================================

st.divider()

st.caption(
    "수빈의 음성인식 AI | 음성 인식 · 맞춤법 검사 · 띄어쓰기 교정"
)
