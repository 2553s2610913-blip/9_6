import streamlit as st

# ---------------------------------------------------------
# 1. 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="메일 발송 전 맞춤법 검사 사전",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. 커스텀 CSS (차분하고 선명한 무채색 다크/그레이 테마)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* 전체 배경: 눈이 편안한 딥 차콜 그레이 */
    .stApp {
        background-color: #12161A;
        color: #F1F5F9;
    }

    /* 메인 타이틀 */
    .office-title {
        color: #FFFFFF;
        font-size: 2.2rem;
        font-weight: 800;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        margin-bottom: 0.2rem;
    }
    
    .office-sub {
        color: #94A3B8;
        font-size: 1.05rem;
        font-weight: 400;
        margin-bottom: 1.8rem;
    }

    /* 무채색 카드 컨테이너 */
    .office-card {
        background-color: #1E262E;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }

    /* 탭 스타일 조정 (높은 대비) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1A202C;
        padding: 6px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: transparent;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        padding: 0 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2D3748 !important;
        color: #FFFFFF !important;
        border: 1px solid #4A5568;
    }

    /* 본문 텍스트 가독성 강화 */
    p, span, label {
        color: #E2E8F0 !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 3. 데이터 세트 (직장인 자주 틀리는 맞춤법 사전)
# ---------------------------------------------------------
DICT_DATA = [
    {
        "wrong": "어의없다 / 어의가 없네",
        "right": "어처구니없다 / 어이가 없다",
        "cat": "비즈니스 표현",
        "desc": "'어의'는 조선시대 임금님의 의사를 뜻합니다. 일이 너무 뜻밖이어서 기가 막힐 때는 '어이'가 맞습니다.",
        "example": "📌 올바른 예시: '갑작스러운 일정 변경으로 어이가 없었지만 차분히 대응했습니다.'"
    },
    {
        "wrong": "오랫만에 연락드립니다",
        "right": "오랜만에 연락드립니다",
        "cat": "메일 인삿말",
        "desc": "'오랜 시간'이 지난 뒤를 뜻할 때는 '오랜만(오래간만)'이 올바른 표기입니다.",
        "example": "📌 올바른 예시: '팀장님, 오랜만에 메일로 인사드립니다.'"
    },
    {
        "wrong": "결제 바랍니다 (서류 승인 시)",
        "right": "결재 바랍니다",
        "cat": "비즈니스 표현",
        "desc": "서류 승인/허가는 '결재(裁)', 신용카드/현금으로 돈을 치르는 것은 '결제(濟)'입니다.",
        "example": "📌 올바른 예시: '첨부해 드린 기안서 결재 부탁드립니다.'"
    },
    {
        "wrong": "문안하게 처리되었습니다",
        "right": "무난하게 처리되었습니다",
        "cat": "업무 보고",
        "desc": "'문안'은 안부를 묻는 것이고, 별탈 없이 이롭다는 뜻은 '무난(無難)'입니다.",
        "example": "📌 올바른 예시: '금일 프로젝트 발표는 무난하게 마무리되었습니다.'"
    },
    {
        "wrong": "요의가 있으신 분",
        "right": "이의가 있으신 분",
        "cat": "회의/소통",
        "desc": "다른 의견은 '이의(異議)'입니다. '요의'는 소변을 보고 싶은 느낌을 뜻하므로 주의하세요!",
        "example": "📌 올바른 예시: '본 안건에 대해 이의가 있으신 분은 말씀해 주세요.'"
    },
    {
        "wrong": "금일/내일/명일/이틀",
        "right": "금일(오늘), 명일(내일), 익일(다음날)",
        "cat": "날짜/시간",
        "desc": "'금일'은 금요일이 아닌 '오늘'을 뜻하며, '익일'은 '이튿날(다음날)'을 의미합니다.",
        "example": "📌 올바른 예시: '제출 기한은 금일 오후 6시까지입니다.'"
    },
    {
        "wrong": "뵈요 / 봬요",
        "right": "봬요 (뵈어요)",
        "cat": "메일 맺음말",
        "desc": "'뵈다'에 종결어미 '-요'가 붙을 때는 '뵈어요'의 축약형인 '봬요'가 올바릅니다.",
        "example": "📌 올바른 예시: '내일 회의실에서 봬요!'"
    },
    {
        "wrong": "되라 / 돼라",
        "right": "돼라 (되어라)",
        "cat": "자주 틀리는 어휘",
        "desc": "'되' 뒤에 '-어'가 결합하면 '돼'가 됩니다. '해'를 넣어 자연스러우면 '돼', '하'를 넣어 자연스러우면 '되'입니다.",
        "example": "📌 올바른 예시: '훌륭한 전문가가 돼라!'"
    }
]


# ---------------------------------------------------------
# 4. 메인 실행 함수
# ---------------------------------------------------------
def main():
    # 사이드바
    with st.sidebar:
        st.markdown("### ✉️ 업무 도구함")
        st.write("발송 전 실수를 줄여주는 비즈니스 맞춤법 가이드라인입니다.")
        st.divider()
        
        st.markdown("#### 💡 업무 팁")
        st.info("메일 보내기 직전, 수신자 주소와 파일 권한을 반드시 재확인하세요.")
        
        st.markdown("---")
        st.caption("Business Mail Checker v1.0")

    # 헤더 섹션
    st.markdown('<div class="office-title">✉️ 이메일 맞춤법 & 체크리스트 사전</div>', unsafe_allow_html=True)
    st.markdown('<div class="office-sub">정확하고 신뢰받는 메일 작성을 위한 필수 점검 가이드라인</div>', unsafe_allow_html=True)

    # 탭 구성
    tab1, tab2, tab3 = st.tabs([
        "📋 메일 발송 전 4단계 체크리스트", 
        "📖 자주 틀리는 맞춤법 사전", 
        "📝 맞춤법 점검 퀴즈"
    ])

    # ---------------------------------------------------------
    # TAB 1: 메일 발송 전 체크리스트
    # ---------------------------------------------------------
    with tab1:
        st.markdown("### 📋 메일 발송 전 4대 필수 점검 사항")
        st.write("아래 항목을 하나씩 확인하며 메일 실수를 예방하세요.")
        st.write("")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 1️⃣ 수신자 & 참조(CC) 점검")
            c1 = st.checkbox("수신자(To) 및 참조자(CC) 이메일 주소 재확인")
            c2 = st.checkbox("대량 발송 시 숨은참조(BCC) 설정 여부")

            st.markdown("##### 2️⃣ 호칭 & 본문 오탈자 점검")
            c3 = st.checkbox("수신자의 성함, 회사명, 직급 오탈자 확인")
            c4 = st.checkbox("첫 인삿말/맺음말의 예의 및 맞춤법 점검")

        with col2:
            st.markdown("##### 3️⃣ 첨부파일 & 용량 점검")
            c5 = st.checkbox("본문 내 언급된 파일의 실제 첨부 여부")
            c6 = st.checkbox("정돈된 파일명 및 최신 버전 문서 여부")

            st.markdown("##### 4️⃣ 링크 & 권한 점검")
            c7 = st.checkbox("본문 내 URL 정상 접속 여부")
            c8 = st.checkbox("클라우드 공유 링크 접속 권한(외부인 공개) 점검")

        # 진척도 계산
        total_checks = 8
        checked_count = sum([c1, c2, c3, c4, c5, c6, c7, c8])
        progress = checked_count / total_checks

        st.write("")
        st.progress(progress)
        
        if checked_count == total_checks:
            st.success("✅ 모든 항목 점검을 마쳤습니다. 메일을 보낼 준비가 완료되었습니다.")
        else:
            st.info(f"💡 {total_checks}개 항목 중 {checked_count}개 체크되었습니다.")

    # ---------------------------------------------------------
    # TAB 2: 자주 틀리는 맞춤법 사전
    # ---------------------------------------------------------
    with tab2:
        st.markdown("### 📖 자주 틀리는 비즈니스 맞춤법")
        
        # 검색 및 카테고리 필터
        f_col1, f_col2 = st.columns([2, 1])
        with f_col1:
            search_query = st.text_input("🔍 검색어 입력 (예: 결제, 어의, 뵈요)", "")
        with f_col2:
            category_filter = st.selectbox("🏷️ 카테고리 선택", ["전체보기", "메일 인삿말", "비즈니스 표현", "업무 보고", "회의/소통", "날짜/시간", "자주 틀리는 어휘"])

        st.write("")

        # 필터링 로직
        filtered_data = DICT_DATA
        if category_filter != "전체보기":
            filtered_data = [item for item in filtered_data if item["cat"] == category_filter]
        if search_query.strip():
            filtered_data = [
                item for item in filtered_data 
                if search_query.lower() in item["wrong"].lower() or search_query.lower() in item["right"].lower()
            ]

        # 데이터 출력
        if not filtered_data:
            st.warning("검색 결과가 없습니다.")
        else:
            for item in filtered_data:
                with st.expander(f"❌ {item['wrong']}  ➡️  ✅ {item['right']} ({item['cat']})"):
                    st.write(f"**설명:** {item['desc']}")
                    st.info(item['example'])

    # ---------------------------------------------------------
    # TAB 3: 맞춤법 퀴즈
    # ---------------------------------------------------------
    with tab3:
        st.markdown("### 📝 맞춤법 미니 점검 퀴즈")
        st.write("자주 실수하는 표기법을 테스트해 보세요.")
        st.write("")

        # Q1
        q1 = st.radio(
            "Q1. 상사에게 서류 승인을 요청할 때 올바른 표현은?",
            ["팀장님, 결제 부탁드립니다.", "팀장님, 결재 부탁드립니다."],
            index=None
        )
        if q1:
            if "결재" in q1:
                st.success("⭕ 정답입니다! 서류 승인은 '결재(裁)'입니다.")
            else:
                st.error("❌ 틀렸습니다. 돈 계산은 '결제', 서류 승인은 '결재'입니다.")

        st.divider()

        # Q2
        q2 = st.radio(
            "Q2. 메일 마지막에 인사할 때 올바른 표현은?",
            ["내일 오전에 뵈요!", "내일 오전에 봬요!"],
            index=None
        )
        if q2:
            if "봬요" in q2:
                st.success("⭕ 정답입니다! '뵈어'의 축약형인 '봬요'가 맞습니다.")
            else:
                st.error("❌ 틀렸습니다. '뵈요'가 아닌 '봬요'가 올바릅니다.")


if __name__ == "__main__":
    main()
