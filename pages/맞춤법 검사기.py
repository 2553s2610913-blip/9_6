
import re
import streamlit as st

st.set_page_config(
    page_title="고운글 | 맞춤법 검사기",
    page_icon="🌷",
    layout="centered",
)

# -----------------------------
# 파스텔 디자인
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

:root {
    --mint: #DFF1E7;
    --mint-dark: #527C69;
    --lavender: #EAE3F7;
    --pink: #F8E7E4;
    --cream: #FBF8F2;
    --ink: #514D5B;
    --muted: #938D9A;
    --line: #ECE6EF;
}

.stApp {
    background: var(--cream);
    color: var(--ink);
    font-family: 'Noto Sans KR', sans-serif;
}

.block-container {
    max-width: 800px;
    padding-top: 2rem;
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
    margin-bottom: 34px;
}

.brand-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--mint);
    border-radius: 17px;
    font-size: 25px;
}

.brand-name {
    font-family: 'Gowun Dodum', sans-serif;
    font-size: 25px;
    font-weight: 700;
    color: #587C6C;
}

.brand-caption {
    color: var(--muted);
    font-size: 11px;
    letter-spacing: 1px;
}

.hero {
    background: linear-gradient(125deg, #E4F2E9, #F0E9F8 70%, #F8EAE5);
    padding: 30px 26px;
    border-radius: 25px;
    margin-bottom: 23px;
}

.hero-kicker {
    color: #7D7294;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 12px;
}

.hero-title {
    font-family: 'Gowun Dodum', sans-serif;
    color: #514D5B;
    font-size: clamp(27px, 5vw, 37px);
    line-height: 1.5;
    letter-spacing: -1px;
    font-weight: 700;
}

.hero-desc {
    color: #827B8B;
    font-size: 13px;
    line-height: 1.9;
    margin-top: 10px;
}

.panel {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 5px 20px rgba(104, 87, 115, 0.035);
}

.section-title {
    color: #5D5669;
    font-weight: 700;
    font-size: 16px;
    margin-bottom: 5px;
}

.section-desc {
    color: var(--muted);
    font-size: 12px;
    margin-bottom: 15px;
}

.stTextArea textarea {
    background: #FCFAFD !important;
    color: #514D5B !important;
    border: 1px solid #EAE3F1 !important;
    border-radius: 15px !important;
    padding: 15px !important;
    font-size: 15px !important;
    line-height: 1.9 !important;
}

.stTextArea textarea:focus {
    border-color: #B7A7D8 !important;
    box-shadow: 0 0 0 1px #B7A7D8 !important;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 13px !important;
    min-height: 44px;
    font-weight: 600;
    transition: 0.2s;
}

.stButton > button[kind="primary"] {
    background: #DFF1E7 !important;
    color: #4F7765 !important;
    border: 1px solid #D3E8DC !important;
}

.stButton > button[kind="primary"]:hover {
    background: #CFE8D9 !important;
}

.stButton > button:not([kind="primary"]),
.stDownloadButton > button {
    background: #F4F0FA !important;
    color: #796B99 !important;
    border: 1px solid #E9E0F3 !important;
}

.result {
    background: #FFFFFF;
    border: 1px solid #E7E0F0;
    border-radius: 20px;
    padding: 22px;
    margin: 14px 0;
}

.result-tag {
    font-size: 12px;
    font-weight: 700;
    color: #8171A7;
    margin-bottom: 12px;
}

.result-text {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    color: #514D5B;
    font-size: 16px;
    line-height: 2;
}

.stat {
    background: #FFFFFF;
    border: 1px solid #ECE6EF;
    border-radius: 15px;
    padding: 16px;
}

.stat-name {
    font-size: 12px;
    color: #938D9A;
}

.stat-value {
    font-size: 21px;
    font-weight: 700;
    color: #6C8E7C;
    margin-top: 7px;
}

.footer {
    text-align: center;
    color: #A49CA7;
    font-size: 11px;
    line-height: 1.9;
    margin-top: 30px;
}

div[data-testid="stAlert"] {
    border-radius: 14px;
}

@media (max-width: 600px) {
    .block-container {
        padding: 1rem 1rem 2rem;
    }

    .hero {
        padding: 24px 20px;
    }

    .panel {
        padding: 16px;
    }
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# 규칙 기반 맞춤법 교정
# 외부 API 없이 작동
# -----------------------------
REPLACEMENTS = [
    # 자주 틀리는 표현
    (r"안되요", "안 돼요"),
    (r"안돼요", "안 돼요"),
    (r"되요", "돼요"),
    (r"됬", "됐"),
    (r"할께요", "할게요"),
    (r"갈께요", "갈게요"),
    (r"볼께요", "볼게요"),
    (r"뵈요", "봬요"),
    (r"어떻해", "어떡해"),
    (r"어의없", "어이없"),
    (r"왠만하면", "웬만하면"),
    (r"웬지", "왠지"),
    (r"금새", "금세"),
    (r"몇일", "며칠"),
    (r"희안", "희한"),
    (r"설레임", "설렘"),
    (r"오랫만", "오랜만"),
    (r"역활", "역할"),
    (r"일일히", "일일이"),
    (r"깨끗히", "깨끗이"),
    (r"꼼꼼히히", "꼼꼼히"),
    (r"바램", "바람"),

    # 자주 쓰는 띄어쓰기
    (r"할수", "할 수"),
    (r"할수록", "할수록"),
    (r"될수", "될 수"),
    (r"할때", "할 때"),
    (r"갈때", "갈 때"),
    (r"볼때", "볼 때"),
    (r"하는것", "하는 것"),
    (r"있는것", "있는 것"),
    (r"좋은것", "좋은 것"),
    (r"할것", "할 것"),
    (r"할수있", "할 수 있"),
    (r"될것같", "될 것 같"),
    (r"것같아요", "것 같아요"),
    (r"수있습니다", "수 있습니다"),
    (r"수있어요", "수 있어요"),
    (r"수없습니다", "수 없습니다"),
    (r"수없어요", "수 없어요"),
    (r"한번더", "한 번 더"),
    (r"그동안", "그동안"),
    (r"이것저것", "이것저것"),
    (r"확인해주세요", "확인해 주세요"),
    (r"확인해 주세요", "확인해 주세요"),
    (r"부탁드립니다", "부탁드립니다"),
]


def correct_text(text):
    """알려진 오류 패턴을 순서대로 교정합니다."""
    result = text

    for pattern, replacement in REPLACEMENTS:
        result = re.sub(pattern, replacement, result)

    # 연속된 공백 정리: 줄바꿈은 유지
    result = re.sub(r"[ \t]{2,}", " ", result)

    return result


def count_changes(original, corrected):
    """교정 전후가 다른지 확인합니다."""
    return 0 if original == corrected else 1


# -----------------------------
# 세션 상태
# -----------------------------
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "corrected_text" not in st.session_state:
    st.session_state.corrected_text = ""

if "original_text" not in st.session_state:
    st.session_state.original_text = ""

if "has_result" not in st.session_state:
    st.session_state.has_result = False


def clear_all():
    st.session_state.input_text = ""
    st.session_state.corrected_text = ""
    st.session_state.original_text = ""
    st.session_state.has_result = False


def load_example():
    st.session_state.input_text = (
        "오늘은 날씨가 너무 좋아서 산책을 가고 싶어요. "
        "내일은 친구와 만나서 맛있는 음식을 먹을께요. "
        "제가 할수 있는 일을 찾아 볼께요."
    )
    st.session_state.has_result = False


# -----------------------------
# 브랜드 및 소개
# -----------------------------
st.markdown("""
<div class="brand">
    <div class="brand-icon">🌷</div>
    <div>
        <div class="brand-name">고운글</div>
        <div class="brand-caption">YOUR GENTLE WRITING HELPER</div>
    </div>
</div>

<div class="hero">
    <div class="hero-kicker">✿ 오늘도 다정한 글쓰기</div>
    <div class="hero-title">
        오늘의 문장을<br>조금 더 예쁘게
    </div>
    <div class="hero-desc">
        맞춤법이 헷갈릴 때 가볍게 확인해 보세요.<br>
        작은 표현부터 차근차근 다듬어 드릴게요.
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# 입력
# -----------------------------
st.markdown("""
<div class="panel">
    <div class="section-title">✏️ 나의 문장</div>
    <div class="section-desc">
        검사하고 싶은 문장을 아래에 입력해 주세요.
    </div>
</div>
""", unsafe_allow_html=True)

st.text_area(
    "문장 입력",
    key="input_text",
    height=200,
    max_chars=3000,
    placeholder="예: 오늘은 날씨가 좋아서 산책을 가고 싶어요.",
    label_visibility="collapsed",
)

st.caption(f"📝 현재 {len(st.session_state.input_text)}자")

left, right = st.columns(2)

with left:
    st.button(
        "🌿 예문 불러오기",
        use_container_width=True,
        on_click=load_example,
    )

with right:
    st.button(
        "지우기",
        use_container_width=True,
        on_click=clear_all,
    )

if st.button(
    "✧  맞춤법 다듬기",
    type="primary",
    use_container_width=True,
):
    original = st.session_state.input_text.strip()

    if not original:
        st.warning("먼저 문장을 입력해 주세요.")
    else:
        corrected = correct_text(original)
        st.session_state.original_text = original
        st.session_state.corrected_text = corrected
        st.session_state.has_result = True


# -----------------------------
# 결과
# -----------------------------
if st.session_state.has_result:
    original = st.session_state.original_text
    corrected = st.session_state.corrected_text
    changed = count_changes(original, corrected)

    st.markdown("## 🌸 다듬은 문장")

    st.markdown(
        f"""
        <div class="result">
            <div class="result-tag">✦ 교정 결과</div>
            <div class="result-text">{__import__('html').escape(corrected)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    a, b = st.columns(2)

    with a:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-name">문장 상태</div>
                <div class="stat-value">
                    {"표현 수정" if changed else "변경 없음"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with b:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-name">글자 수</div>
                <div class="stat-value">{len(corrected)}자</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if changed:
        st.success("자주 틀리는 표현을 찾아 수정했어요.")
    else:
        st.info(
            "등록된 교정 규칙에 해당하는 표현이 없습니다. "
            "모든 맞춤법이 정확하다는 의미는 아닙니다."
        )

    st.download_button(
        "📄 교정 결과 다운로드",
        data=corrected,
        file_name="고운글_교정결과.txt",
        mime="text/plain",
        use_container_width=True,
    )

    with st.expander("원문과 비교하기"):
        st.markdown("**수정 전**")
        st.text(original)
        st.markdown("**수정 후**")
        st.text(corrected)

    st.caption(
        "고운글은 자주 틀리는 표현을 교정하는 간단한 도구입니다. "
        "문맥에 따른 전체 맞춤법 검사를 보장하지 않습니다."
    )


# -----------------------------
# 안내
# -----------------------------
st.markdown("""
<div class="footer">
    🌷 고운글 · 오늘의 문장을 더 아름답게<br>
    외부 검사 API 없이 작동하는 규칙 기반 교정 도구
</div>
""", unsafe_allow_html=True)
