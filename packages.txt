import io
import os
import tempfile

import streamlit as st
import speech_recognition as sr

# ----------------------------------
# 맞춤법 검사기 (없어도 앱은 실행되도록 처리)
# ----------------------------------
try:
    from hanspell import spell_checker
    SPELL_OK = True
except Exception:
    spell_checker = None
    SPELL_OK = False

# mp3, m4a 변환용 (없어도 앱은 실행되도록 처리)
try:
    from pydub import AudioSegment
    PYDUB_OK = True
except Exception:
    AudioSegment = None
    PYDUB_OK = False

# ----------------------------------
# 페이지 설정
# ----------------------------------
st.set_page_config(page_title="수빈의 음성인식 AI", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #f5f7fb; }
h1 { text-align: center; color: #243b64; }
.subtitle { text-align: center; color: #64748b; font-size: 16px; }
.stButton > button { width: 100%; border-radius: 10px; height: 48px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ 수빈의 음성인식 AI")
st.markdown('<p class="subtitle">음성을 텍스트로 변환하고 맞춤법까지 교정하는 AI</p>',
            unsafe_allow_html=True)
st.divider()

# ----------------------------------
# 세션 초기화
# ----------------------------------
defaults = {"recognized_text": "", "corrected_text": "", "error_count": 0, "reset_id": 0}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

rid = st.session_state.reset_id  # 초기화할 때 위젯 키를 바꾸기 위한 값


# ----------------------------------
# 함수들
# ----------------------------------
def to_wav_bytes(file_bytes: bytes, filename: str) -> bytes:
    """wav/flac/aiff는 그대로, 나머지(mp3, m4a 등)는 pydub으로 wav 변환"""
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext in ("wav", "flac", "aiff", "aif"):
        return file_bytes
    if not PYDUB_OK:
        raise RuntimeError("mp3/m4a 변환에는 pydub과 ffmpeg가 필요합니다.")
    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        audio = AudioSegment.from_file(tmp_path)
        buf = io.BytesIO()
        audio.set_channels(1).export(buf, format="wav")
        return buf.getvalue()
    finally:
        os.remove(tmp_path)


def recognize(wav_bytes: bytes) -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
        audio_data = recognizer.record(source)
    return recognizer.recognize_google(audio_data, language="ko-KR")


def spell_check(text: str):
    """맞춤법 검사 (500자 제한이 있어 나눠서 검사). (교정문, 오류수) 반환"""
    chunks = [text[i:i + 480] for i in range(0, len(text), 480)]
    corrected, errors = [], 0
    for chunk in chunks:
        r = spell_checker.check(chunk)
        corrected.append(r.checked)
        errors += r.errors
    return "".join(corrected), errors


def handle_audio(file_bytes: bytes, filename: str):
    try:
        with st.spinner("음성을 분석하고 있습니다..."):
            wav = to_wav_bytes(file_bytes, filename)
            text = recognize(wav)
        st.session_state.recognized_text = text
        st.session_state.corrected_text = ""
        st.success("음성 인식 완료!")
    except sr.UnknownValueError:
        st.error("음성을 이해하지 못했습니다. 더 또렷한 음성으로 시도해 보세요.")
    except sr.RequestError as e:
        st.error("음성 인식 서버 연결에 실패했습니다. 인터넷 연결을 확인해 주세요.")
        st.exception(e)
    except Exception as e:
        st.error("음성 인식 중 오류가 발생했습니다.")
        st.exception(e)


# ----------------------------------
# 음성 인식
# ----------------------------------
st.subheader("🎤 음성 인식")

tab_file, tab_mic = st.tabs(["📁 파일 업로드", "🎙️ 마이크 녹음"])

with tab_file:
    types = ["wav", "aiff", "aif", "flac"]
    if PYDUB_OK:
        types += ["mp3", "m4a", "ogg"]
    audio_file = st.file_uploader("음성 파일을 선택하세요.", type=types, key=f"uploader_{rid}")
    if st.button("파일로 음성 인식 시작", key=f"btn_file_{rid}"):
        if audio_file is None:
            st.warning("음성 파일을 먼저 업로드해 주세요.")
        else:
            handle_audio(audio_file.getvalue(), audio_file.name)

with tab_mic:
    if hasattr(st, "audio_input"):
        mic = st.audio_input("버튼을 눌러 녹음하세요.", key=f"mic_{rid}")
        if st.button("녹음으로 음성 인식 시작", key=f"btn_mic_{rid}"):
            if mic is None:
                st.warning("먼저 녹음해 주세요.")
            else:
                handle_audio(mic.getvalue(), "recording.wav")
    else:
        st.info("마이크 녹음은 Streamlit 1.39 이상에서 지원됩니다.")

if st.session_state.recognized_text:
    st.markdown("### 📝 인식된 문장")
    st.text_area("음성 인식 결과", value=st.session_state.recognized_text,
                 height=120, disabled=True)

# ----------------------------------
# 직접 텍스트 입력
# ----------------------------------
st.divider()
st.subheader("⌨️ 텍스트 입력")

manual_text = st.text_area(
    "검사할 문장을 입력하세요. (비워 두면 음성 인식 결과를 검사합니다)",
    placeholder="예: 안녕하세요 저는 고등학교 학생 입니다.",
    height=150,
    key=f"manual_{rid}",
)
text_to_check = manual_text.strip() or st.session_state.recognized_text.strip()

# ----------------------------------
# 맞춤법 검사
# ----------------------------------
st.divider()
st.subheader("🔎 맞춤법 검사")

if not SPELL_OK:
    st.warning("맞춤법 검사 모듈(py-hanspell)을 불러오지 못했습니다. 음성 인식은 그대로 사용할 수 있습니다.")

if st.button("맞춤법 검사하기", key=f"btn_spell_{rid}", disabled=not SPELL_OK):
    if not text_to_check:
        st.warning("검사할 문장을 입력해 주세요.")
    else:
        try:
            with st.spinner("맞춤법을 검사하고 있습니다..."):
                corrected, errors = spell_check(text_to_check)
            st.session_state.corrected_text = corrected
            st.session_state.error_count = errors
            st.success("맞춤법 검사 완료!")
        except Exception as e:
            st.error("맞춤법 검사 중 오류가 발생했습니다. (네이버 서버 변경 등으로 일시적으로 안 될 수 있어요)")
            st.exception(e)

if st.session_state.corrected_text:
    st.divider()
    st.subheader("✨ 최종 교정 결과")
    st.text_area("교정된 문장", value=st.session_state.corrected_text,
                 height=150, disabled=True)
    st.metric("발견된 오류 수", st.session_state.error_count)
    st.download_button("📥 교정 결과 다운로드", data=st.session_state.corrected_text,
                       file_name="맞춤법_교정결과.txt", mime="text/plain")

# ----------------------------------
# 초기화
# ----------------------------------
st.divider()
if st.button("🔄 전체 초기화"):
    new_id = st.session_state.reset_id + 1
    st.session_state.clear()
    st.session_state.reset_id = new_id
    st.rerun()

st.divider()
st.caption("수빈의 음성인식 AI | 음성 인식 · 맞춤법 검사")
