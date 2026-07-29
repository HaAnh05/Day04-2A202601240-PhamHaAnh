from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import run_model_tool_loop, write_transcript, safe_slug, now_iso, trim_history

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

st.set_page_config(
    page_title="Research Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean white theme and typography
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #1f2937;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .main .block-container {
        padding-top: 2rem;
        max-width: 1000px;
    }
    h1, h2, h3, h4 {
        color: #111827;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #e5e7eb;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px;
        color: #4b5563;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f3f4f6;
        color: #111827;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.title("Research Agent")

# Sidebar Configuration
st.sidebar.header("Agent Configuration")

provider_choice = st.sidebar.selectbox(
    "Provider",
    options=["gemini", "openrouter", "openai", "anthropic"],
    index=0
)

version_choice = st.sidebar.text_input("Version Label", value="v0")
model_override = st.sidebar.text_input("Model Override (Optional)", value="gemini-3.1-flash-lite")

history_window = st.sidebar.number_input("History Window", min_value=1, max_value=10, value=5)
max_tool_rounds = st.sidebar.number_input("Max Tool Rounds", min_value=1, max_value=10, value=4)

# Load artifacts
system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_yaml_path = ARTIFACTS_DIR / "tools.yaml"

system_prompt = system_prompt_path.read_text(encoding="utf-8") if system_prompt_path.exists() else ""
tool_declarations = load_tool_declarations(tools_yaml_path) if tools_yaml_path.exists() else []
openai_tools = to_openai_tools(tool_declarations)

artifact_version = build_artifact_version(version_choice, system_prompt_path, tools_yaml_path)

st.sidebar.divider()
st.sidebar.text(f"Version: {artifact_version.artifact_version}")
st.sidebar.text(f"Prompt Hash: {artifact_version.prompt_hash[:8]}")
st.sidebar.text(f"Tools Hash: {artifact_version.tools_hash[:8]}")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "tool_events_history" not in st.session_state:
    st.session_state.tool_events_history = []

if "transcript_id" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    st.session_state.transcript_id = "_".join([
        safe_slug(version_choice),
        safe_slug(provider_choice),
        timestamp,
    ])

transcript_path = TRANSCRIPTS_DIR / f"{st.session_state.transcript_id}.transcript.json"

tab_chat, tab_traces, tab_artifacts = st.tabs(["Chat", "Tool Traces", "System Info"])

with tab_chat:
    # Render past messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "tool_events" in msg and msg["tool_events"]:
                with st.expander("Tool Calls"):
                    for idx, event in enumerate(msg["tool_events"], 1):
                        st.text(f"{idx}. {event['tool']}")
                        st.json({"args": event["args"], "result": event["result"]})

    # Chat Input
    if prompt := st.chat_input("Nhập câu hỏi..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        messages_payload = [
            {"role": "system", "content": system_prompt},
            *trim_history(history[:-1], history_window),
            {"role": "user", "content": prompt},
        ]

        with st.chat_message("assistant"):
            with st.spinner("Đang xử lý..."):
                try:
                    provider = make_provider(provider_choice)
                    selected_model = model_override.strip() if model_override.strip() else None

                    result = run_model_tool_loop(
                        provider=provider,
                        messages=messages_payload,
                        tools=openai_tools,
                        model=selected_model,
                        max_tool_rounds=max_tool_rounds,
                    )

                    assistant_text = result.get("assistant_text", "")
                    st.write(assistant_text)

                    tool_events = result.get("tool_events", [])
                    if tool_events:
                        with st.expander("Tool Calls", expanded=False):
                            for idx, event in enumerate(tool_events, 1):
                                st.text(f"{idx}. {event['tool']}")
                                st.json({"args": event["args"], "result": event["result"]})

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_text,
                        "tool_events": tool_events,
                    })

                    st.session_state.tool_events_history.extend(tool_events)

                    transcript_data = {
                        "transcript_id": st.session_state.transcript_id,
                        **artifact_version_dict(artifact_version),
                        "provider": provider_choice,
                        "model": selected_model or getattr(provider, "default_model", None),
                        "turns": st.session_state.messages,
                    }
                    write_transcript(transcript_path, transcript_data)

                except Exception as exc:
                    err_msg = f"Lỗi: {type(exc).__name__}: {str(exc)}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})

with tab_traces:
    st.subheader("Tool Execution History")
    if not st.session_state.tool_events_history:
        st.write("Chưa có tool call nào.")
    else:
        for i, ev in enumerate(reversed(st.session_state.tool_events_history), 1):
            st.text(f"Event #{len(st.session_state.tool_events_history) - i + 1}: {ev['tool']}")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Arguments:")
                st.json(ev["args"])
            with col2:
                st.caption("Result:")
                st.json(ev["result"])
            st.divider()

with tab_artifacts:
    st.subheader("System Prompt")
    st.code(system_prompt, language="markdown")

    st.subheader("Tools Declarations")
    st.code(tools_yaml_path.read_text(encoding="utf-8") if tools_yaml_path.exists() else "", language="yaml")
