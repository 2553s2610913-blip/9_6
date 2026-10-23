
import streamlit as st
import re

st.set_page_config(
    page_title="말랑말랑 문장수선소",
    page_icon="💌",
    layout="centered",
)

# ---------- 귀여운 디자인 ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #fff7fb 0%, #fffdf7 100%);
}
.main .block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    color: #985879 !important;
}
div.stButton > button {
    background-color: #edb6d0;
    color: #61384d;
    border: 0;
    border-radius: 14px;
    font-weight: 600;
    min-height: 42px;
}
div.stButton > button:hover {
    background-color: #e79dc1;
    color: #ffffff;
    border: 0;
}
div[data-testid="stAlert"] {
    border-radius: 14px;
}
div[data-testid="stTextArea"] textarea {
    border-radius: 14px;
    border-color: #efcbdc;
}
div[data-testid="stTabs"] button {
    color: #985879;
}
.soft-card {
    background: #fff;
    border: 1px solid #f3d9e5;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 12px;
}
.small-note {
    color: #997d8b;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ---------- 문장 다듬기 ----------
def convert_to_email(text, purpose):
    """일상적인 문장을 정중한 업무용 문장으로 바꿉니다."""
    original = text.strip()
    if not original:
        return ""

    # 흔한 구어체를 정중한 표현으로 변경
    replacements = [
        (r"해줘요", "부탁드립니다"),
        (r"해주세요", "부탁드립니다"),
        (r"해 줘", "해 주시면 감사하겠습니다"),
        (r"알려줘", "알려 주시면 감사하겠습니다"),
        (r"알려주세요", "알려 주시면 감사하겠습니다"),
        (r"보내줘", "보내 주시면 감사하겠습니다"),
        (r"보내주세요", "보내 주시면 감사하겠습니다"),
        (r"확인해줘", "확인해 주시면 감사하겠습니다"),
        (r"확인해주세요", "확인해 주시면 감사하겠습니다"),
        (r"빨리 보내", "가능하신 한 빠르게 보내 주시면 감사하겠습니다"),
        (r"왜 답이 없어요\??", "이전에 드린 메일을 확인하셨는지 여쭙습니다."),
        (r"뭐예요\??", "어떤 내용인지 확인 부탁드립니다."),
        (r"몰라요", "현재 해당 내용을 정확히 파악하지 못했습니다."),
        (r"미안해요", "죄송합니다"),
        (r"미안합니다", "죄송합니다"),
        (r"고마워요", "감사합니다"),
        (r"고마워", "감사합니다"),
        (r"ㅇㅋ|ㅇㅇ", "네, 확인했습니다"),
        (r"ㄱㄱ", "진행하겠습니다"),
        (r"안됨", "진행이 어렵습니다"),
        (r"안 돼요", "진행이 어렵습니다"),
        (r"할게요", "진행하겠습니다"),
        (r"했어요", "완료했습니다"),
    ]

    result = original
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)

    # 목적에 따라 인사말과 마무리 추가
    if purpose == "부탁":
        opening = "안녕하세요.\n"
        ending = "\n\n확인해 주시면 감사하겠습니다.\n감사합니다."
    elif purpose == "사과":
        opening = "안녕하세요.\n"
        ending = "\n\n불편을 드려 죄송합니다. 같은 일이 반복되지 않도록 주의하겠습니다.\n감사합니다."
    elif purpose == "감사":
        opening = "안녕하세요.\n"
        ending = "\n\n도움 주셔서 진심으로 감사합니다.\n좋은 하루 보내세요."
    elif purpose == "재촉":
        opening = "안녕하세요.\n"
        ending = "\n\n바쁘시겠지만 확인 후 회신해 주시면 감사하겠습니다.\n감사합니다."
    else:
        opening = "안녕하세요.\n"
        ending = "\n\n확인 부탁드립니다.\n감사합니다."

    # 이미 인사말이 있다면 중복하지 않음
    if result.startswith(("안녕하세요", "안녕하십니까")):
        opening = ""

    return opening + result.strip() + ending


def get_feedback(style):
    """상대방에게 전달할 수 있는 부드러운 피드백 예시."""
    messages = {
        "맞춤법이 자주 틀릴 때": (
            "내용은 잘 이해했어요! 😊\n"
            "다만 중요한 내용은 서로 오해하지 않도록 "
            "맞춤법과 띄어쓰기를 한 번만 더 확인해 주시면 좋겠어요."
        ),
        "메일이 너무 짧거나 무뚝뚝할 때": (
            "빠르게 회신해 주셔서 감사합니다!\n"
            "메일에 간단한 인사말이나 요청 배경을 덧붙여 주시면 "
            "내용을 이해하고 답변하기가 더 수월할 것 같아요."
        ),
        "반말이나 무례한 표현을 사용할 때": (
            "업무 관련 소통에서는 서로 존중하는 표현을 사용하면 좋겠습니다. "
            "앞으로는 조금 더 정중한 말투로 이야기 나눌 수 있을까요?"
        ),
        "답장을 계속 늦게 할 때": (
            "바쁘신 점 이해합니다. 😊\n"
            "바로 답변하기 어려우시면 확인 예정 시점이라도 알려 주시면 "
            "업무 일정을 조율하는 데 도움이 될 것 같습니다."
        ),
        "같은 실수가 반복될 때": (
            "이전에 말씀드린 부분이 다시 확인되어 공유드립니다.\n"
            "다음부터는 발송 전에 체크리스트를 활용해 함께 확인해 보면 좋겠습니다."
        ),
    }
    return messages.get(style, "")


# ---------- 머리말 ----------
st.markdown(
    "<div style='text-align:center; font-size:3rem;'>💌 🧸 🌷</div>",
    unsafe_allow_html=True,
)
st.title("말랑말랑 문장수선소")
st.markdown(
    "<div style='text-align:center; color:#986681;'>"
    "틀려도 괜찮아, 함께 다듬으면 되니까! ✨<br>"
    "맞춤법부터 메일 예절까지, 한 문장씩 말랑하게."
    "</div>",
    unsafe_allow_html=True,
)
st.write("")

with st.expander("🌼 이곳은 어떤 곳인가요?"):
    st.write(
        "맞춤법이나 메일 예절이 익숙하지 않은 사람을 "
        "무조건 지적하기보다는, 더 편하고 정확하게 소통할 방법을 "
        "함께 찾아보는 공간이에요."
    )
    st.caption("사람을 고치려 하기보다, 함께 사용하는 문장을 개선해 봐요.")

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 맞춤법 검사",
    "💌 메일 변신",
    "🗣️ 부드러운 피드백",
    "📚 메일 예절 도감",
])


# ---------- 탭 1: 맞춤법 검사 ----------
with tab1:
    st.subheader("📝 맞춤법 톡톡")
    st.write("보내기 전에 문장을 한 번 점검해 봐요.")

    spell_text = st.text_area(
        "검사할 문장을 입력해 주세요.",
        placeholder="예: 내일까지 자료를 보내주시면 감사하겠습니다",
        height=150,
        key="spell_text",
    )

    if st.button("🔎 맞춤법 검사하기", key="spell_button"):
        if not spell_text.strip():
            st.warning("검사할 문장을 먼저 입력해 주세요.")
        elif len(spell_text) > 5000:
            st.warning("한 번에 5,000자 이하로 입력해 주세요.")
        else:
            with st.spinner("문장을 꼼꼼히 살펴보고 있어요..."):
                try:
                    from hanspell import spell_checker

                    checked = spell_checker.check(spell_text)
                    corrected = checked.checked

                    st.success("검사가 완료되었어요! 🌷")
                    st.markdown("#### ✨ 다듬은 문장")
                    st.text_area(
                        "교정 결과",
                        value=corrected,
                        height=150,
                        key="spell_result",
                    )

                    if corrected.strip() == spell_text.strip():
                        st.info("검사 결과, 입력한 문장과 교정 결과가 같아요.")
                    else:
                        st.markdown("#### 🔍 수정 전")
                        st.code(spell_text)
                        st.markdown("#### 💗 수정 후")
                        st.code(corrected)

                    st.caption(
                        "자동 교정은 문맥에 따라 부정확할 수 있어요. "
                        "이름, 전문 용어, 의도한 표현은 직접 확인해 주세요."
                    )

                except ImportError:
                    st.error(
                        "맞춤법 검사 라이브러리를 불러오지 못했어요. "
                        "requirements.txt에 py-hanspell이 있는지 확인해 주세요."
                    )
                except Exception:
                    st.error(
                        "현재 맞춤법 검사 서비스에 연결하지 못했어요. 😢\n\n"
                        "인터넷 연결이나 외부 서비스 상태를 확인한 뒤 "
                        "잠시 후 다시 시도해 주세요. 다른 기능은 정상적으로 사용할 수 있어요."
                    )


# ---------- 탭 2: 메일 변신 ----------
with tab2:
    st.subheader("💌 메일 변신소")
    st.write("조금 딱딱해도 괜찮아요. 상황에 맞게 정중한 표현으로 바꿔 봐요.")

    purpose = st.selectbox(
        "어떤 상황인가요?",
        ["일반 업무", "부탁", "사과", "감사", "재촉"],
    )

    purpose_map = {
        "일반 업무": "일반",
        "부탁": "부탁",
        "사과": "사과",
        "감사": "감사",
        "재촉": "재촉",
    }

    mail_text = st.text_area(
        "바꾸고 싶은 문장",
        placeholder="예: 자료 빨리 보내줘요. 아직 안 왔어요.",
        height=140,
        key="mail_text",
    )

    if st.button("🎀 정중한 문장으로 바꾸기", key="mail_button"):
        if not mail_text.strip():
            st.warning("먼저 바꾸고 싶은 문장을 입력해 주세요.")
        elif len(mail_text) > 5000:
            st.warning("한 번에 5,000자 이하로 입력해 주세요.")
        else:
            result = convert_to_email(
                mail_text,
                purpose_map[purpose],
            )
            st.markdown("#### 🌸 말랑하게 바뀐 문장")
            st.text_area(
                "완성된 문장",
                value=result,
                height=220,
                key="mail_result",
            )
            st.caption(
                "정해진 표현을 바탕으로 변환한 결과예요. "
                "문장 사이에 같은 표현이 반복되거나 문맥에 맞지 않을 수 있으니 "
                "보내기 전에 한 번 읽어 주세요."
            )


# ---------- 탭 3: 부드러운 피드백 ----------
with tab3:
    st.subheader("🗣️ 어떻게 말해야 할까요?")
    st.write(
        "상대방을 창피하게 만들지 않으면서도 필요한 점을 전달해 봐요."
    )

    feedback_type = st.selectbox(
        "어떤 상황인가요?",
        [
            "맞춤법이 자주 틀릴 때",
            "메일이 너무 짧거나 무뚝뚝할 때",
            "반말이나 무례한 표현을 사용할 때",
            "답장을 계속 늦게 할 때",
            "같은 실수가 반복될 때",
        ],
        key="feedback_type",
    )

    if st.button("💗 표현 추천받기", key="feedback_button"):
        st.markdown("#### 이렇게 말해 보세요")
        st.info(get_feedback(feedback_type))

    st.markdown("---")
    st.markdown("#### 🧸 기억하면 좋은 세 가지")
    st.markdown(
        """
        - **사람 대신 행동을 이야기하기:** "넌 왜 그래?"보다
          "이 부분을 확인해 주시면 좋겠어요."
        - **기준을 구체적으로 알려 주기:** 무엇을 어떻게 바꾸면 되는지 설명하기.
        - **공개적으로 망신 주지 않기:** 민감한 피드백은 가능하면 개인적으로 전달하기.
        """
    )


# ---------- 탭 4: 메일 예절 도감 ----------
with tab4:
    st.subheader("📚 초보자를 위한 메일 예절 도감")

    with st.expander("1. 메일 제목은 어떻게 쓰나요?", expanded=True):
        st.write("목적과 핵심 내용을 짧게 적으면 좋아요.")
        st.markdown("**좋은 예시**")
        st.code("[자료 요청] 10월 행사 안내 자료 전달 부탁드립니다")
        st.markdown("**피하면 좋은 예시**")
        st.code("안녕하세요 / 질문 있어요 / 급해요")

    with st.expander("2. 기본적인 업무 메일 구조"):
        st.code(
            "제목: [업무명] 확인 요청\n\n"
            "안녕하세요, 담당자님.\n\n"
            "다름이 아니라, 아래 내용에 대한 확인을 부탁드리고자 메일드립니다.\n"
            "가능하실 때 검토 후 회신해 주시면 감사하겠습니다.\n\n"
            "감사합니다.\n"
            "홍길동 드림"
        )

    with st.expander("3. 자주 쓰는 표현 바꾸기"):
        examples = [
            ("이거 해주세요", "이 부분을 진행해 주시면 감사하겠습니다."),
            ("빨리 답 주세요", "가능하실 때 회신 부탁드립니다."),
            ("왜 안 했어요?", "해당 작업의 진행 상황을 확인 부탁드립니다."),
            ("몰라요", "현재 정확한 내용을 확인 중입니다."),
            ("확인했어요?", "확인 여부를 알려 주시면 감사하겠습니다."),
        ]

        for before, after in examples:
            st.markdown(f"**❌ {before}**")
            st.markdown(f"**💗 {after}**")
            st.write("")

    with st.expander("4. 보내기 전 10초 체크리스트"):
        checks = [
            "제목만 보고도 내용을 알 수 있나요?",
            "받는 사람과 첨부 파일을 확인했나요?",
            "맞춤법과 띄어쓰기를 점검했나요?",
            "요청 내용과 기한을 분명하게 적었나요?",
            "상대방이 불쾌하게 받아들일 표현은 없나요?",
        ]

        for i, item in enumerate(checks):
            st.checkbox(item, key=f"mail_check_{i}")

    st.success(
        "🌷 메일 예절은 사람마다 익숙한 정도가 달라요. "
        "처음부터 완벽하기보다 하나씩 익히는 것이 중요해요."
    )


# ---------- 하단 안내 ----------
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#ad879a;'>"
    "made with 💗 말랑말랑 문장수선소<br>"
    "<span style='font-size:0.85rem;'>"
    "좋은 소통은 완벽한 맞춤법보다 서로를 존중하는 마음에서 시작돼요."
    "</span></div>",
    unsafe_allow_html=True,
)
