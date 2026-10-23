import re
from datetime import datetime

import requests
import streamlit as st

st.set_page_config(page_title="메일체 변환기", page_icon="✉️", layout="wide")

DEFAULT_MODELS = {
    "Gemini": "gemini-2.5-flash",
    "ChatGPT (OpenAI)": "gpt-4o-mini",
}

SITUATIONS = ["업무 요청", "진행 상황 보고", "일정 조율", "자료 요청", "독촉/리마인드", "감사 인사", "사과/양해 요청", "기타"]
RELATIONS = ["상급자(윗사람)", "동료/동급", "하급자/후배", "외부 거래처/고객"]
TONES = ["정중하고 공손하게", "간결하고 깔끔하게", "친근하지만 예의 바르게", "매우 격식 있게"]
LENGTHS = ["짧게 (3~4문장)", "보통 (5~8문장)", "자세히 (9문장 이상)"]


def get_secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


def build_prompt(d: dict) -> tuple:
    system = (
        "당신은 한국 직장 문화에 능통한 비즈니스 이메일 작성 전문가입니다. "
        "사용자가 준 핵심 내용만으로 자연스러운 한국어 이메일을 작성합니다. "
        "입력에 없는 사실(날짜, 금액, 숫자, 고유명사)은 절대 지어내지 않습니다. "
        "수신자 직급과 관계에 맞는 호칭과 존댓말을 사용합니다."
    )
    prompt = f"""다음 정보를 바탕으로 이메일을 작성해 주세요.

[수신자] {d['to_name']} {d['to_rank']}
[수신자와의 관계] {d['relation']}
[발신자] {d['my_org']} {d['my_rank']} {d['my_name']}
[메일 목적] {d['situation']}
[업무 내용] {d['work']}
[요청 사항] {d['request']}
[기한] {d['deadline'] or '별도 없음'}
[말투] {d['tone']}
[분량] {d['length']}
[추가 지시] {d['extra'] or '없음'}

출력 형식(반드시 지킬 것):
제목: (메일 제목 한 줄)
---
(본문: 인사 → 소개 → 업무 내용 → 요청 사항 → 마무리 인사 → 서명)

설명이나 따옴표, 마크다운 기호는 넣지 말고 위 형식대로만 출력하세요."""
    return system, prompt


def call_gemini(api_key: str, model: str, system: str, prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.6},
    }
    r = requests.post(url, headers=headers, json=body, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"Gemini 오류 ({r.status_code}): {r.text[:300]}")
    data = r.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts).strip()
    except Exception:
        raise RuntimeError("Gemini 응답을 해석하지 못했습니다. 입력 내용이나 모델명을 확인해 주세요.")


def call_openai(api_key: str, model: str, system: str, prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.6,
    }
    r = requests.post(url, headers=headers, json=body, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"OpenAI 오류 ({r.status_code}): {r.text[:300]}")
    try:
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        raise RuntimeError("OpenAI 응답을 해석하지 못했습니다. 모델명을 확인해 주세요.")


def split_subject_body(text: str) -> tuple:
    text = text.strip().strip("`").strip()
    m = re.match(r"^\s*제목\s*[:：]\s*(.+?)\s*\n+(?:-{3,}\s*\n+)?(.*)$", text, re.S)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return "(제목 없음)", text


def fallback_mail(d: dict) -> tuple:
    """AI 없이 만드는 기본 템플릿"""
    to = f"{d['to_name']} {d['to_rank']}님".strip()
    me = " ".join(x for x in [d["my_org"], d["my_rank"], d["my_name"]] if x)
    subject = f"[{d['situation']}] {d['work'][:25]}{'...' if len(d['work']) > 25 else ''}"
    lines = [f"안녕하세요, {to}.", f"{me}입니다.", ""]
    if d["work"]:
        lines += [f"{d['work']}", ""]
    if d["request"]:
        lines += [f"다름이 아니라, {d['request']}", ""]
    if d["deadline"]:
        lines += [f"가능하시다면 {d['deadline']}까지 회신 부탁드립니다.", ""]
    lines += ["바쁘신 와중에 시간 내어 확인해 주셔서 감사합니다.", "", "감사합니다.", me]
    return subject, "\n".join(lines)


def generate(d: dict, provider: str, api_key: str, model: str) -> tuple:
    if not api_key:
        s, b = fallback_mail(d)
        return s, b, "API 키가 없어 AI 대신 기본 템플릿으로 변환했습니다."
    system, prompt = build_prompt(d)
    try:
        if provider == "Gemini":
            raw = call_gemini(api_key, model, system, prompt)
        else:
            raw = call_openai(api_key, model, system, prompt)
        if not raw:
            raise RuntimeError("AI가 빈 응답을 보냈습니다.")
        s, b = split_subject_body(raw)
        return s, b, ""
    except requests.exceptions.Timeout:
        msg = "응답 시간이 초과되었습니다."
    except requests.exceptions.RequestException as e:
        msg = f"네트워크 오류: {e}"
    except Exception as e:
        msg = str(e)
    s, b = fallback_mail(d)
    return s, b, f"⚠️ {msg}\n대신 기본 템플릿으로 변환했습니다."


if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None

# ---------------- 사이드바 ----------------
with st.sidebar:
    st.header("⚙️ AI 설정")
    provider = st.radio("사용할 AI", list(DEFAULT_MODELS.keys()))
    secret_name = "GEMINI_API_KEY" if provider == "Gemini" else "OPENAI_API_KEY"
    saved_key = get_secret(secret_name)

    if saved_key:
        st.success("저장된 API 키를 사용합니다.")
        api_key = saved_key
    else:
        api_key = st.text_input(f"{provider} API 키", type="password",
                                help="키는 저장되지 않고 현재 세션에서만 사용됩니다.").strip()
        if not api_key:
            st.info("키가 없으면 AI 없이 기본 템플릿으로 변환됩니다.")

    model = st.text_input("모델명", value=DEFAULT_MODELS[provider]).strip() or DEFAULT_MODELS[provider]
    st.caption("모델명이 바뀌어 오류가 나면 최신 모델명으로 수정하세요.")

    st.divider()
    st.subheader("🕘 최근 변환 기록")
    if st.session_state.history:
        for i, h in enumerate(reversed(st.session_state.history[-5:])):
            if st.button(f"{h['time']} · {h['subject'][:18]}", key=f"hist_{i}"):
                st.session_state.result = h
    else:
        st.caption("아직 기록이 없습니다.")

# ---------------- 메인 화면 ----------------
st.title("✉️ 메일체 변환기")
st.caption("핵심 내용만 적으면 상황과 직급에 맞는 정중한 이메일로 바꿔드립니다.")

left, right = st.columns(2, gap="large")

with left:
    st.subheader("1. 정보 입력")
    c1, c2 = st.columns(2)
    to_name = c1.text_input("수신자 이름", placeholder="김민수")
    to_rank = c2.text_input("수신자 직급", placeholder="팀장")
    c3, c4, c5 = st.columns(3)
    my_org = c3.text_input("내 소속", placeholder="마케팅팀")
    my_rank = c4.text_input("내 직급", placeholder="대리")
    my_name = c5.text_input("내 이름 (선택)", placeholder="홍길동")

    work = st.text_area("업무 내용", height=110, placeholder="예) 3분기 광고 성과 보고서 초안 작성 완료")
    request = st.text_area("요청 사항", height=90, placeholder="예) 검토 후 수정사항 알려주세요")

    c6, c7 = st.columns(2)
    situation = c6.selectbox("메일 목적", SITUATIONS)
    relation = c7.selectbox("수신자와의 관계", RELATIONS)
    c8, c9 = st.columns(2)
    tone = c8.selectbox("말투", TONES)
    length = c9.selectbox("분량", LENGTHS, index=1)
    deadline = st.text_input("회신 기한 (선택)", placeholder="예) 이번 주 금요일 오후 5시")
    extra = st.text_input("추가 지시 (선택)", placeholder="예) 첨부파일이 있다고 언급해줘")

    run = st.button("✨ 메일체로 변환", type="primary", use_container_width=True)

if run:
    if not work.strip() and not request.strip():
        st.warning("업무 내용 또는 요청 사항을 입력해 주세요.")
    else:
        data = {
            "to_name": to_name.strip(), "to_rank": to_rank.strip(),
            "my_org": my_org.strip(), "my_rank": my_rank.strip(), "my_name": my_name.strip(),
            "work": work.strip(), "request": request.strip(),
            "situation": situation, "relation": relation, "tone": tone, "length": length,
            "deadline": deadline.strip(), "extra": extra.strip(),
        }
        with st.spinner("메일을 작성하는 중입니다..."):
            subject, body, notice = generate(data, provider, api_key, model)
        item = {"time": datetime.now().strftime("%H:%M"), "subject": subject, "body": body, "notice": notice}
        st.session_state.result = item
        st.session_state.history.append(item)

with right:
    st.subheader("2. 변환 결과")
    res = st.session_state.result
    if not res:
        st.info("왼쪽에 내용을 입력하고 '메일체로 변환'을 눌러주세요.")
    else:
        if res.get("notice"):
            st.warning(res["notice"])
        subject_edit = st.text_input("제목", value=res["subject"], key=f"subj_{res['time']}_{len(res['body'])}")
        body_edit = st.text_area("본문 (직접 수정 가능)", value=res["body"], height=380,
                                 key=f"body_{res['time']}_{len(res['body'])}")

        full = f"제목: {subject_edit}\n\n{body_edit}"
        st.caption("아래 박스 오른쪽 위의 복사 아이콘을 누르면 전체가 복사됩니다.")
        st.code(full, language=None)
        st.download_button("💾 텍스트 파일로 저장", data=full.encode("utf-8"),
                           file_name="mail.txt", mime="text/plain", use_container_width=True)
