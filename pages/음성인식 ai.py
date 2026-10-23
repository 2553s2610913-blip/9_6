
import streamlit as st
from korector import NaverSpellChecker

# 페이지 설정
st.set_page_config(
    page_title="수빈의 맞춤법 검사기",
    page_icon="✍️",
    layout="centered"
)

# 검사기 준비
@st.cache_resource
def load_checker():
    return NaverSpellChecker()

# 디자인
st.title("✍️ 맞춤법 검사기")
st.subheader("맞춤법과 띄어쓰기를 간편하게 검사하세요.")
st.caption("글을 입력하고 검사 버튼을 누르면 교정 결과를 보여줍니다.")

# 입력창
original_text = st.text_area(
    "검사할 문장을 입력하세요",
    height=220,
    placeholder="예: 안녕하세요 저는 고등학교 학생 입니다."
)

# 글자 수 표시
st.caption(f"입력 글자 수: {len(original_text)}자")

# 검사 버튼
if st.button("🔎 맞춤법 검사하기", use_container_width=True):

    if not original_text.strip():
        st.warning("검사할 문장을 먼저 입력해 주세요.")

    else:
        try:
            with st.spinner("맞춤법을 검사하고 있습니다..."):
                checker = load_checker()
                result = checker.check(original_text)

            if not result.get("success"):
                st.error("검사에 실패했습니다. 잠시 후 다시 시도해 주세요.")

            else:
                corrected_text = result.get(
                    "corrected", original_text
                )
                error_count = result.get("error_count", 0)

                st.success("검사가 완료되었습니다!")

                st.markdown("### 📝 검사 결과")

                if corrected_text == original_text:
                    st.info("입력한 문장에서 수정된 부분이 없습니다.")
                else:
                    st.markdown("**교정된 문장**")
                    st.text_area(
                        "수정 결과",
                        value=corrected_text,
                        height=180,
                        key="corrected_result"
                    )

                st.metric("발견된 오류 수", error_count)

                st.download_button(
                    label="📥 수정된 문장 다운로드",
                    data=corrected_text,
                    file_name="맞춤법_검사_결과.txt",
                    mime="text/plain",
                    use_container_width=True
                )

        except Exception:
            st.error(
                "검사 서버에 연결하지 못했습니다. "
                "인터넷 연결과 라이브러리 설치를 확인해 주세요."
            )

st.divider()
st.caption("수빈의 맞춤법 검사기 | 한국어 맞춤법·띄어쓰기 검사")
