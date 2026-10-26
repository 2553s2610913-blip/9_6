
import streamlit as st
from hanspell import spell_checker
import html
import time

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="바른글 | 맞춤법 검사기",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------
# 디자인
# --------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

    :root {
        --green: #176B52;
        --green-dark: #10513E;
        --green-light: #EAF4EF;
        --text: #202923;
        --muted: #78837D;
        --border: #E4EAE6;
    }

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .stApp {
        background: #F8FAF8;
    }

    .block-container {
        max-width: 880px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 28px;
    }

    .brand-icon {
        width: 46px;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--green);
        color: white;
        border-radius: 15px;
        font-size: 23px;
    }

    .brand-name {
        font-size: 23px;
        font-weight: 800;
        letter-spacing: -1px;
        color: var(--green-dark);
    }

    .brand-sub {
        font-size: 12px;
        color: var(--muted);
        margin-top: 1px;
    }

    .hero {
        margin-bottom: 26px;
    }

    .hero-tag {
        display: inline-block;
        background: var(--green-light);
        color: var(--green);
        padding: 6px 11px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: clamp(27px, 5vw, 36px);
        line-height: 1.4;
        letter-spacing: -1.7px;
        font-weight: 800;
        color: var(--text);
        margin: 0 0 10px 0;
    }

    .hero-desc {
        font-size: 14px;
        line-height: 1.8;
        color: var(--muted);
        margin: 0;
    }

    .panel {
        background: white;
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 5px 22px rgba(30, 60, 45, 0.025);
    }

    .section-label {
        font-size: 15px;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 5px;
    }

    .section-help {
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 14px;
    }

    .stTextArea textarea {
        background: #FBFCFB !important;
        border: 1px solid #E1E8E3 !important;
        border-radius: 12px !important;
        color: var(--text) !important;
        font-size: 15px !important;
        line-height: 1.9 !important;
        padding: 15px !important;
    }

    .stTextArea textarea:focus {
        border-color: var(--green) !important;
        box-shadow: 0 0 0 1px var(--green) !important;
    }

    .stButton > button {
        border-radius: 12px;
        min-height: 46px;
        font-weight: 700;
        transition: all .2s ease;
    }

    .stButton > button[kind="primary"] {
        background: var(--green);
        border: 1px solid var(--green);
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--green-dark);
        border-color: var(--green-dark);
    }

    .result-box {
        background: white;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 20px;
        margin: 10px 0 16px;
    }

    .result-label {
        color: var(--green);
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .result-text {
        color: var(--text);
        font-size: 16px;
        line-height: 2;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
    }

    .stat-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 15px;
        min-height: 88px;
    }

    .stat-label {
        font-size: 12px;
        color: var(--muted);
        margin-bottom: 8px;
    }

    .stat-value {
        font-size: 23px;
        font-weight: 800;
        color: var(--green-dark);
    }

    .footer-note {
        color: #929C96;
        text-align: center;
        font-size: 11px;
        line-height: 1.8;
        margin-top: 30px;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    @media (max-width: 600px) {
        .block-container {
            padding: 1.2rem 1rem 2rem;
        }

        .panel {
            padding: 16px;
            border-radius: 15px;
        }

        .hero-title {
            letter-spacing: -1px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 상단 브랜드
# --------------------------------------------------
st.markdown(
    """
    <div class="brand">
        <div class="brand-icon">✍</div>
        <div>
            <div class="brand-name">바른글</div>
            <div class="brand-sub">KOREAN SPELL CHECKER</div>
        </div>
    </div>

    <div class="hero">
        <div class="hero-tag">✦ 더 정확한 글쓰기</div>
        <div class="hero-title">
            당신의 문장을<br>더 바르게 다듬어 드려요.
        </div>
        <p class="hero-desc">
            맞춤법과 띄어쓰기를 확인하고<br>
            더 자연스러운 문장으로 교정해 보세요.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# 세션 상태 초기화
# --------------------------------------------------
if "corrected_text" not in st.session_state:
    st.session_state.corrected_text = ""

if "original_text" not in st.session_state:
    st.session_state.original_text = ""

if "error_count" not in st.session_state:
    st.session_state.error_count = 0

if "check_time" not in st.session_state:
    st.session_state.check_time = 0.0

if "has_result" not in st.session_state:
    st.session_state.has_result = False

# --------------------------------------------------
# 입력 영역
# --------------------------------------------------
st.markdown('<div class="panel">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="section-label">검사할 문장</div>
    <div class="section-help">
        교정하고 싶은 문장이나 글을 입력해 주세요.
    </div>
    """,
    unsafe_allow_html=True,
)

examples = {
    "예문 선택": "",
    "일상 문장": "오늘은 날씨가 너무 좋아서 산책을 가고 싶습니다.",
    "맞춤법 예시": "제가 할수 있는 일을 찾아 볼께요.",
    "업무용 문장": "회의 내용을 확인 하신 후 답변 부탁 드립니다.",
}

selected_example = st.selectbox(
    "예문 선택",
    options=list(examples.keys()),
    label_visibility="collapsed",
    help="예문을 선택하면 입력창에 문장이 채워집니다.",
)

if selected_example != st.session_state.get("last_example", "예문 선택"):
    if selected_example != "예문 선택":
        st.session_state.input_text = examples[selected_example]
    st.session_state.last_example = selected_example

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

input_text = st.text_area(
    "검사할 문장 입력",
    key="input_text",
    height=220,
    max_chars=500,
    placeholder=(
        "예: 오늘은 날씨가 너무 좋아서 산책을 가고 싶습니다.\n"
        "이곳에 문장을 입력해 주세요."
    ),
    label_visibility="collapsed",
)

character_count = len(input_text)

left, right = st.columns([1, 1])

with left:
    st.caption(f"📝 {character_count} / 500자")

with right:
    if st.button("내용 지우기", use_container_width=True):
        st.session_state.input_text = ""
        st.session_state.corrected_text = ""
        st.session_state.original_text = ""
        st.session_state.error_count = 0
        st.session_state.has_result = False
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# 검사 실행
# --------------------------------------------------
if st.button(
    "✓  맞춤법 검사하기",
    type="primary",
    use_container_width=True,
):
    text_to_check = st.session_state.input_text.strip()

    if not text_to_check:
        st.warning("검사할 문장을 먼저 입력해 주세요.")
    elif len(text_to_check) > 500:
        st.warning("한 번에 최대 500자까지 검사할 수 있습니다.")
    else:
        try:
            with st.spinner("문장을 꼼꼼하게 확인하고 있어요..."):
                start_time = time.time()
                result = spell_checker.check(text_to_check)
                elapsed = time.time() - start_time

            corrected = getattr(result, "checked", None)
            error_count = getattr(result, "errors", None)

            if not isinstance(corrected, str) or not corrected.strip():
                st.error(
                    "검사 결과를 받아오지 못했습니다. "
                    "잠시 후 다시 시도해 주세요."
                )
                st.session_state.has_result = False
            else:
                st.session_state.original_text = text_to_check
                st.session_state.corrected_text = corrected
                st.session_state.error_count = (
                    error_count
                    if isinstance(error_count, int)
                    else 0
                )
                st.session_state.check_time = elapsed
                st.session_state.has_result = True

        
        except Exception as e:
            st.session_state.has_result = False
            st.error("맞춤법 검사 중 오류가 발생했습니다.")

            with st.expander("오류 상세 정보 확인"):
                st.code(f"{type(e).__name__}: {e}")
                st.caption(
                    "이 내용을 확인하면 설치 문제인지, "
                    "외부 서비스 응답 문제인지 구분하는 데 도움이 됩니다."
                )

            )
            st.caption(
                "외부 검사 서비스의 점검, 요청 제한 또는 "
                "응답 형식 변경으로 검사가 실패할 수 있습니다."
            )

# --------------------------------------------------
# 검사 결과
# --------------------------------------------------
if st.session_state.has_result:
    original = st.session_state.original_text
    corrected = st.session_state.corrected_text
    errors = st.session_state.error_count

    st.markdown("### 검사 결과")

    stat1, stat2 = st.columns(2)

    with stat1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">검사 상태</div>
                <div class="stat-value" style="font-size:19px;">
                    ✓ 검사 완료
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with stat2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">감지된 오류 수</div>
                <div class="stat-value">{errors}개</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="result-box">
            <div class="result-label">✦ 교정된 문장</div>
            <div class="result-text">{html.escape(corrected)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if original == corrected:
        st.success("입력한 문장과 교정 결과가 같습니다.")
    else:
        st.info(
            "교정 결과를 확인한 후 실제 의도와 문맥에 맞는지 "
            "검토해 주세요."
        )

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="교정 결과 다운로드",
            data=corrected,
            file_name="바른글_교정결과.txt",
            mime="text/plain; charset=utf-8",
            use_container_width=True,
        )

    with col2:
        st.button(
            "새 문장 검사하기",
            use_container_width=True,
            on_click=lambda: st.session_state.update(
                has_result=False,
                corrected_text="",
                original_text="",
            ),
        )

    with st.expander("원문과 교정 결과 비교하기"):
        st.markdown("**검사 전 원문**")
        st.text(original)
        st.markdown("**검사 후 결과**")
        st.text(corrected)

    st.caption(
        f"검사 시간: {st.session_state.check_time:.2f}초 · "
        "자동 교정 결과는 문맥에 따라 직접 확인해 주세요."
    )

# --------------------------------------------------
# 하단 안내
# --------------------------------------------------
st.markdown(
    """
    <div class="footer-note">
        바른글 · 한국어 맞춤법 및 띄어쓰기 도우미<br>
        외부 검사 서비스를 이용하며, 결과는 문맥에 따라 달라질 수 있습니다.
    </div>
    """,
    unsafe_allow_html=True,
)
