import re
import time
from datetime import datetime

import requests
import streamlit as st

st.set_page_config(page_title="메일체 변환기", page_icon="✉️", layout="wide")

DEFAULT_MODELS = {
    "Gemini": "gemini-3.8-flash",
    "ChatGPT (OpenAI)": "gpt-4o-mini",
}

SITUATIONS = ["업무 요청", "진행 상황 보고", "일정 조율", "자료 요청", "독촉/리마인드", "감사 인사", "사과/양해 요청", "기타"]
RELATIONS = ["상급자(윗사람)", "동료/동급", "하급자/후배", "외부 거래처/고객"]
TONES = ["정중하고 공손하게", "간결하고 깔끔하게", "친근하지만 예의 바르게", "매우 격식 있게"]
LENGTHS = ["짧게 (3~4문장)", "보통 (5~8문장)", "자세히 (9문장 이상)"]

GEMINI_TIMEOUT = 25  # 초. 너무 느리면 다음 모델로 넘어갑니다.


class ModelNotFound(RuntimeError):
    """모델명이 없거나 더 이상 제공되지 않을 때"""


class ModelBusy(RuntimeError):
    """서버가 혼잡하거나 응답이 느릴 때"""


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


# ---------------- Gemini ----------------
def call_gemini(api_key: str, model: str, system: str, prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.6, "maxOutputTokens": 2000},
    }
    try:
        r = requests.post(url, headers=headers, json=body, timeout=GEMINI_TIMEOUT)
    except requests.exceptions.Timeout:
        raise ModelBusy(f"모델 '{model}'의 응답이 너무 느립니다.")
    if r.status_code == 404:
        raise
