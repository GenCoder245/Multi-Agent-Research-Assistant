import json
import os
import uuid

import requests
import streamlit as st


API_BASE = os.getenv("API_BASE", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="Technical Research Assistant",
    page_icon="🔎",
    layout="wide",
)


def reset_session() -> None:
    st.session_state.messages = []
    st.session_state.session_id = uuid.uuid4().hex


def stream_response(query: str, session_id: str):
    response = requests.post(
        f"{API_BASE}/chat",
        json={"query": query, "session_id": session_id},
        stream=True,
        timeout=300,
    )
    response.raise_for_status()
    try:
        for line in response.iter_lines(chunk_size=1, decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            try:
                event = json.loads(line[len("data:"):].strip())
            except json.JSONDecodeError:
                continue
            if event.get("type") == "error":
                raise RuntimeError(event.get("error", "The API returned an error."))
            yield event
            if event.get("done"):
                break
    finally:
        response.close()


if "messages" not in st.session_state:
    reset_session()

st.title("Technical Research Assistant")
st.caption("Ask a technical question and follow the research workflow as it happens.")

with st.sidebar:
    st.subheader("Conversation")
    if st.button("New conversation", use_container_width=True):
        reset_session()
        st.rerun()
    st.caption(f"Session: {st.session_state.session_id}")

    if st.button("Show workflow", use_container_width=True):
        try:
            image = requests.get(f"{API_BASE}/graph_image", timeout=60)
            image.raise_for_status()
            st.image(image.content, caption="LangGraph workflow", use_container_width=True)
        except requests.RequestException as exc:
            st.error(f"Unable to load workflow: {exc}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask a technical research question...")
if prompt and prompt.strip():
    query = prompt.strip()
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        stage_placeholder = st.empty()
        answer_placeholder = st.empty()
        answer_parts: list[str] = []
        try:
            for event in stream_response(query, st.session_state.session_id):
                if event.get("type") == "stage":
                    stage_placeholder.info(event.get("stage", "Working..."))
                elif event.get("type") == "chunk":
                    answer_parts.append(event.get("delta", ""))
                    answer_placeholder.markdown("".join(answer_parts))
            stage_placeholder.empty()
        except (requests.RequestException, RuntimeError) as exc:
            stage_placeholder.error(str(exc))

        answer = "".join(answer_parts) or "No response received."
        answer_placeholder.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})