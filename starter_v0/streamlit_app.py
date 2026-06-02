"""Streamlit UI for the Day 04 Research Agent.

Run from starter_v0/:
    source .venv/bin/activate
    pip install -r requirements.txt
    streamlit run streamlit_app.py
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


load_lab_env(ROOT)

PROVIDER_ENV = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash-lite",
    "openrouter": "openai/gpt-4o-mini",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-latest",
}

EXAMPLE_PROMPTS = [
    "Tweet mới nhất của Sam Altman là gì?",
    "Mọi người đang bàn gì về GPT-5 trên Twitter?",
    "Tin tức AI hôm nay có gì nổi bật?",
    "Tóm tắt bài này: https://openai.com/blog",
    "Tóm tắt 5 tweet mới nhất giúp mình",
    "Gửi tin tức AI hôm nay qua Gmail giúp mình",
]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def env_status() -> dict[str, str]:
    keys = [
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "TAVILY_API_KEY",
        "FIRECRAWL_API_KEY",
        "RAPIDAPI_KEY",
        "TELEGRAM_BOT_TOKEN",
        "RESEND_API_KEY",
        "RESEND_FROM",
    ]
    return {key: ("✅" if os.getenv(key) else "—") for key in keys}


def init_session() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model_history" not in st.session_state:
        st.session_state.model_history = []
    if "transcript" not in st.session_state:
        st.session_state.transcript = None
    if "transcript_path" not in st.session_state:
        st.session_state.transcript_path = None
    if "turn_index" not in st.session_state:
        st.session_state.turn_index = 0


def ensure_transcript(provider: str, model: str | None, version: str, system_prompt_path: Path, tools_path: Path) -> None:
    if st.session_state.transcript is not None:
        return
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider), timestamp])
    path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"
    st.session_state.transcript_path = path
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider,
        "model": model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
        "ui": "streamlit",
    }


def render_tool_rounds(rounds: list[dict[str, Any]]) -> None:
    if not rounds:
        return
    with st.expander("🔧 Tool rounds", expanded=True):
        for record in rounds:
            st.markdown(f"**Round {record.get('round')}**")
            if record.get("assistant_text"):
                st.caption(record["assistant_text"])
            calls = record.get("tool_calls") or []
            if calls:
                st.json(calls)
            for event in record.get("tool_results") or []:
                name = event.get("tool", "?")
                with st.container(border=True):
                    st.markdown(f"`{name}`")
                    st.caption("Args")
                    st.json(event.get("args", {}))
                    st.caption("Result")
                    st.json(event.get("result", {}))


def process_user_message(
    user_text: str,
    *,
    provider_name: str,
    model: str | None,
    version: str,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> dict[str, Any]:
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    openai_tools = to_openai_tools(load_tool_declarations(tools_path))
    provider = make_provider(provider_name)
    selected_model = model or getattr(provider, "default_model", None)
    ensure_transcript(provider_name, selected_model, version, system_prompt_path, tools_path)

    st.session_state.turn_index += 1
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.model_history, history_window),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
    }

    try:
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model,
            max_tool_rounds=max_tool_rounds,
        )
        turn_record.update(result)
        assistant_text = result.get("assistant_text") or ""
        st.session_state.model_history.append({"role": "user", "content": user_text})
        st.session_state.model_history.append({"role": "assistant", "content": assistant_text})
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"
        turn_record.update({"status": "provider_error", "error": err})
        result = {"status": "provider_error", "assistant_text": err, "rounds": [], "tool_events": []}

    turn_record["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
    return result


def sidebar_config() -> dict[str, Any]:
    st.sidebar.header("Cấu hình")
    provider = st.sidebar.selectbox(
        "Provider",
        ["gemini", "openrouter", "openai", "anthropic"],
        index=0,
    )
    env_key = PROVIDER_ENV[provider]
    if not os.getenv(env_key):
        st.sidebar.error(f"Thiếu `{env_key}` trong `.env`")

    model_default = DEFAULT_MODELS.get(provider, "")
    model = st.sidebar.text_input("Model (để trống = mặc định)", value=model_default).strip() or None

    version = st.sidebar.text_input("Artifact version", value="v3")
    prompt_options = {
        "Final (v3)": ARTIFACTS_DIR / "system_prompt.md",
        "v2": ARTIFACTS_DIR / "prompts" / "v2_system_prompt.md",
        "v1": ARTIFACTS_DIR / "prompts" / "v1_system_prompt.md",
        "Baseline v0": ARTIFACTS_DIR / "prompts" / "v0_baseline_system_prompt.md",
    }
    prompt_label = st.sidebar.selectbox("System prompt", list(prompt_options.keys()))
    system_prompt_path = prompt_options[prompt_label]
    tools_path = ARTIFACTS_DIR / "tools.yaml"

    history_window = st.sidebar.slider("History window (cặp user/assistant)", 1, 10, 5)
    max_tool_rounds = st.sidebar.slider("Max tool rounds", 1, 8, 4)

    st.sidebar.divider()
    st.sidebar.subheader("API keys (.env)")
    for key, status in env_status().items():
        st.sidebar.text(f"{status} {key}")

    st.sidebar.divider()
    if st.sidebar.button("🗑 Xóa hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.session_state.model_history = []
        st.session_state.transcript = None
        st.session_state.transcript_path = None
        st.session_state.turn_index = 0
        st.rerun()

    return {
        "provider": provider,
        "model": model,
        "version": version,
        "system_prompt_path": system_prompt_path,
        "tools_path": tools_path,
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
    }


def main() -> None:
    st.set_page_config(
        page_title="Research Agent",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_session()
    cfg = sidebar_config()

    st.title("🔬 Research Agent")
    st.caption(
        f"Provider: **{cfg['provider']}** · Model: **{cfg['model'] or 'default'}** · "
        f"Prompt: **{cfg['system_prompt_path'].name}** · Version: **{cfg['version']}**"
    )
    if path := st.session_state.get("transcript_path"):
        st.caption(f"Transcript: `{path}`")

    st.subheader("Gợi ý thử")
    cols = st.columns(2)
    for index, prompt in enumerate(EXAMPLE_PROMPTS):
        if cols[index % 2].button(prompt, key=f"ex_{index}", use_container_width=True):
            st.session_state.trigger_prompt = prompt

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("rounds"):
                render_tool_rounds(message["rounds"])
            if message.get("status") == "waiting_for_user":
                st.info("Agent đang chờ bạn trả lời (clarify).")
            if message.get("status") == "max_tool_rounds":
                st.warning("Đã đạt giới hạn vòng gọi tool.")
            if message.get("status") == "provider_error":
                st.error(message["content"])

    user_text = st.chat_input("Nhập yêu cầu research…")
    if not user_text:
        user_text = st.session_state.pop("trigger_prompt", None)
    if not user_text:
        return

    st.session_state.messages.append({"role": "user", "content": user_text})

    with st.chat_message("assistant"):
        with st.spinner("Agent đang xử lý…"):
            result = process_user_message(
                user_text.strip(),
                provider_name=cfg["provider"],
                model=cfg["model"],
                version=cfg["version"],
                system_prompt_path=cfg["system_prompt_path"],
                tools_path=cfg["tools_path"],
                history_window=cfg["history_window"],
                max_tool_rounds=cfg["max_tool_rounds"],
            )
        render_tool_rounds(result.get("rounds", []))
        assistant_text = result.get("assistant_text") or ""
        st.markdown(assistant_text)
        if result.get("status") == "waiting_for_user":
            st.info("Agent đang chờ bạn trả lời (clarify).")
        elif result.get("status") == "max_tool_rounds":
            st.warning("Đã đạt giới hạn vòng gọi tool.")
        err = assistant_text if result.get("status") == "provider_error" else ""
        if "429" in err or "RESOURCE_EXHAUSTED" in err:
            st.info("Gemini free tier: ~20 request/ngày. Thử lại sau hoặc bật billing.")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result.get("assistant_text") or "",
        "rounds": result.get("rounds", []),
        "status": result.get("status"),
    })


if __name__ == "__main__":
    main()
