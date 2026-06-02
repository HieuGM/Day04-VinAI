from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import assistant_tool_message, execute_tool_call, json_text, tool_results_message, trim_history
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return slug.strip("_") or "run"


@st.cache_resource(show_spinner=False)
def load_runtime(provider_name: str, system_prompt_path: str, tools_path: str) -> dict[str, Any]:
    system_prompt = Path(system_prompt_path).read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(Path(tools_path))
    return {
        "provider": make_provider(provider_name),
        "system_prompt": system_prompt,
        "tools": to_openai_tools(tool_declarations),
    }


def transcript_path(transcript_id: str) -> Path:
    return TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"


def write_transcript() -> None:
    transcript = st.session_state.transcript
    transcript["updated_at"] = now_iso()
    path = transcript_path(transcript["transcript_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    st.session_state.transcript_file = str(path)


def reset_chat(provider_name: str, model_name: str | None, version: str, system_prompt_path: Path, tools_path: Path) -> None:
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), "ui", timestamp])
    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model_name,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "surface": "streamlit",
        "turns": [],
    }
    write_transcript()


def run_tool_loop(
    *,
    provider: Any,
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]],
    model: str | None,
    max_tool_rounds: int,
) -> dict[str, Any]:
    working_messages = list(messages)
    rounds: list[dict[str, Any]] = []
    all_tool_events: list[dict[str, Any]] = []

    for round_index in range(1, max_tool_rounds + 1):
        response = provider.complete(working_messages, tools, model=model, temperature=0.0)
        calls = response.tool_calls
        round_record: dict[str, Any] = {
            "round": round_index,
            "assistant_text": response.text,
            "tool_calls": [{"name": call.name, "args": call.args} for call in calls],
            "tool_results": [],
        }

        if not calls:
            rounds.append(round_record)
            return {
                "status": "answered",
                "assistant_text": response.text or "",
                "rounds": rounds,
                "tool_events": all_tool_events,
            }

        working_messages.append(assistant_tool_message(response.text, calls))
        non_clarification_events: list[dict[str, Any]] = []

        for call in calls:
            event = execute_tool_call(call)
            round_record["tool_results"].append(event)
            all_tool_events.append(event)

            result = event.get("result", {})
            if isinstance(result, dict) and result.get("awaiting_user"):
                question = result.get("question") or call.args.get("question") or "Please add the missing information."
                rounds.append(round_record)
                return {
                    "status": "waiting_for_user",
                    "assistant_text": question,
                    "rounds": rounds,
                    "tool_events": all_tool_events,
                }

            non_clarification_events.append(event)

        rounds.append(round_record)
        working_messages.append(tool_results_message(non_clarification_events))

    return {
        "status": "max_tool_rounds",
        "assistant_text": f"Stopped after {max_tool_rounds} tool rounds. Inspect the transcript for details.",
        "rounds": rounds,
        "tool_events": all_tool_events,
    }


def submit_message(user_text: str, runtime: dict[str, Any], model: str | None, history_window: int, max_tool_rounds: int) -> None:
    if not user_text.strip():
        return

    messages = [
        {"role": "system", "content": runtime["system_prompt"]},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text.strip()},
    ]
    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": now_iso(),
        "user": user_text.strip(),
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    try:
        result = run_tool_loop(
            provider=runtime["provider"],
            messages=messages,
            tools=runtime["tools"],
            model=model,
            max_tool_rounds=max_tool_rounds,
        )
        turn_record.update(result)
        assistant_text = result["assistant_text"]
    except Exception as exc:
        assistant_text = f"ERROR: {type(exc).__name__}: {exc}"
        turn_record.update({"status": "provider_error", "error": assistant_text})

    turn_record["assistant_text"] = assistant_text
    turn_record["ended_at"] = now_iso()
    st.session_state.history.append({"role": "user", "content": user_text.strip()})
    st.session_state.history.append({"role": "assistant", "content": assistant_text})
    st.session_state.turns.append(turn_record)
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript()


def env_table() -> list[dict[str, str]]:
    keys = [
        "OPENROUTER_API_KEY",
        "TAVILY_API_KEY",
        "FIRECRAWL_API_KEY",
        "RAPIDAPI_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "DISCORD_WEBHOOK_URL",
        "RESEND_API",
        "RESEND_FROM",
        "GITHUB_TOKEN",
    ]
    return [{"Variable": key, "Status": "present" if os.getenv(key) else "missing"} for key in keys]


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        st.markdown(turn.get("assistant_text") or "")
        calls = []
        for round_record in turn.get("rounds", []):
            calls.extend(round_record.get("tool_calls", []))
        if calls:
            with st.expander("Tool calls", expanded=False):
                st.json(calls)
        events = turn.get("tool_events", [])
        if events:
            with st.expander("Tool results", expanded=False):
                st.code(json_text(events, max_chars=12000), language="json")


def main() -> None:
    st.set_page_config(page_title="Research Agent", layout="wide")
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.25rem; max-width: 1180px; }
        [data-testid="stSidebar"] .stButton button { width: 100%; }
        .stChatMessage { border-radius: 6px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"

    with st.sidebar:
        st.title("Research Agent")
        provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
        version = st.text_input("Version", value="v7")
        model_override = st.text_input("Model override", value="")
        history_window = st.slider("History window", min_value=1, max_value=10, value=5)
        max_tool_rounds = st.slider("Tool rounds", min_value=1, max_value=6, value=4)
        model = model_override.strip() or None

        if st.button("New chat"):
            reset_chat(provider_name, model, version, system_prompt_path, tools_path)
            st.rerun()

        st.divider()
        st.dataframe(env_table(), hide_index=True, use_container_width=True)
        if "transcript_file" in st.session_state:
            st.caption(st.session_state.transcript_file)

    runtime = load_runtime(provider_name, str(system_prompt_path), str(tools_path))
    selected_model = model or getattr(runtime["provider"], "default_model", None)

    if "transcript" not in st.session_state:
        reset_chat(provider_name, selected_model, version, system_prompt_path, tools_path)

    st.header("Research Agent")

    for turn in st.session_state.turns:
        render_turn(turn)

    waiting_yes_no = False
    if st.session_state.turns:
        last = st.session_state.turns[-1]
        waiting_yes_no = last.get("status") == "waiting_for_user" and any(
            event.get("result", {}).get("response_type") == "yes_no"
            for event in last.get("tool_events", [])
            if isinstance(event.get("result"), dict)
        )

    if waiting_yes_no:
        left, right = st.columns(2)
        with left:
            if st.button("Confirm"):
                with st.spinner("Running agent"):
                    submit_message("OK, I confirm.", runtime, model, history_window, max_tool_rounds)
                st.rerun()
        with right:
            if st.button("Cancel"):
                with st.spinner("Running agent"):
                    submit_message("No, do not send.", runtime, model, history_window, max_tool_rounds)
                st.rerun()

    prompt = st.chat_input("Ask a research question")
    if prompt:
        with st.spinner("Running agent"):
            submit_message(prompt, runtime, model, history_window, max_tool_rounds)
        st.rerun()


if __name__ == "__main__":
    main()
