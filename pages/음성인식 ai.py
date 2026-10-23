
import streamlit as st
from hanspell import spell_checker

st.set_page_config(
    page_title="맞춤법 검사기",
    page_icon="📝"
)

st.title("📝 한글 맞춤법 검사기")
st.write("맞춤법과 띄어쓰기를 검사해 보세요!")

text = st.text_area(
    "검사할 문장을 입력하세요.",
    placeholder="예: 오늘은 날씨가 너무 조아",
    height=200
)

if st.button("맞춤법 검사하기"):
    if text.strip():
        try:
            result = spell_checker.check(text)

            st.subheader("검사 결과")
            st.success(result.checked)

            if result.checked == text:
                st.info("수정할 부분이 없는 것 같아요!")
            else:
                st.write("위의 수정된 문장을 확인해 보세요.")

        except Exception:
            st.error(
                "검사에 실패했어요. 잠시 후 다시 시도해 주세요."
            )
    else:
        st.warning("먼저 검사할 문장을 입력해 주세요.")
