
import streamlit as st
import speech_recognition as sr
from korector import NaverSpellChecker
import io

# 페이지 설정
st.set_page_config(
    page_title="수빈의 음성인식 AI",
    page_icon="🎙️",
    layout="centered"
)

# 검사기 준비
@st.cache_resource
def load_checker():
    return NaverSpellChecker()

# 제목
st.title("🎙️ 수빈의 음성인식 AI")
st.subheader("말하면 글자로 변환하고 맞춤법까지 교정해요.")
st.caption("음성 인식에는 인터넷 연결이 필요할 수 있습니다.")

# 음성 파일 업로드
st.markdown("### 1️⃣ 음성 입력")
audio_file = st.file_uploader(
    "음성 파일을 선택하세요.",
    type=["wav", "aiff", "aif", "flac"]
)

# 텍스트 직접 입력도 지원
st.markdown("### 2️⃣ 텍스트 입력")
manual_text = st.text_area(
    "직접 입력하거나 인식된 문장을 붙여 넣으세요.",
    placeholder="예: 안녕하세요 저는 고등학교 학생 입니다.",
    height=150
)

recognized_text = ""

# 음성 인식
if st.button("🎤 음성 인식하기", use_container_width=True):
    if audio_file is None:
        st.warning("먼저 WAV, AIFF 또는 FLAC 음성 파일을 올려 주세요.")
    else:
        try:
            recognizer = sr.Recognizer()

            with st.spinner("음성을 텍스트로 변환하고 있습니다..."):
                audio_bytes = audio_file.read()

                with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                    audio_data = recognizer.record(source)

                recognized_text = recognizer.recognize_google(
                    audio_data,
                    language="ko-KR"
                )

                st.session_state["recognized_text"] = recognized_text

            st.success("음성 인식이 완료되었습니다!")

        except sr.UnknownValueError:
            st.error("음성을 이해하지 못했어요. 더 선명한 음성으로 다시 시도해 주세요.")
        except sr.RequestError:
            st.error("음성 인식 서버에 연결하지 못했어요. 인터넷 연결을 확인해 주세요.")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# 인식 결과
recognized_text = st.session_state.get("recognized_text", "")

if recognized_text:
    st.markdown("### 📝 음성 인식 결과")
    st.text_area(
        "인식된 문장",
        value=recognized_text,
        height=120,
        key="recognized_display"
    )

# 검사할 문장 선택
text_to_check = manual_text.strip() or recognized_text.strip()

st.divider()
st.markdown("### 3️⃣ 맞춤법 검사")

if st.button("🔎 맞춤법 검사하기", use_container_width=True):
    if not text_to_check:
        st.warning("음성을 인식하거나 검사할 문장을 입력해 주세요.")
    else:
        try:
            with st.spinner("맞춤법을 검사하고 있습니다..."):
                checker = load_checker()
                result = checker.check(text_to_check)

            if not result.get("success"):
                st.error("맞춤법 검사에 실패했습니다.")
            else:
                corrected_text = result.get("corrected", text_to_check)
                error_count = result.get("error_count", 0)

                st.session_state["corrected_text"] = corrected_text
                st.session_state["error_count"] = error_count

        except Exception as e:
            st.error(
                "맞춤법 검사 중 오류가 발생했습니다. "
                "라이브러리 설치와 검사 서버를 확인해 주세요."
            )
            st.caption(str(e))

# 교정 결과
if "corrected_text" in st.session_state:
    corrected_text = st.session_state["corrected_text"]

    st.success("검사가 완료되었습니다!")
    st.text_area(
        "교정된 문장",
        value=corrected_text,
        height=150
    )

    st.metric(
        "발견된 오류 수",
        st.session_state.get("error_count", 0)
    )

    st.download_button(
        "📥 교정 결과 다운로드",
        data=corrected_text,
        file_name="맞춤법_검사_결과.txt",
        mime="text/plain",
        use_container_width=True
    )

st.divider()
st.caption("수빈의 음성인식 AI | 음성 변환 · 맞춤법 · 띄어쓰기")
