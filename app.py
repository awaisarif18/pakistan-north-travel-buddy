"""Run with: streamlit run app.py"""

import streamlit as st
from google.genai import errors

from rag import (
    CHAT_MODEL, TRAVEL_NOTICE, generate_answer, gemini_client,
    open_collection, page_label, retrieve,
)

st.set_page_config(page_title="Pakistan North Tours AI", page_icon="🏔️", layout="centered")
st.title("Pakistan North Tours AI")
st.write("Ask about routes, treks, transport, and facilities in the 92-page Northern Pakistan travel guide.")
st.caption("Ask each question with its destination named. Chat history is displayed, but retrieval uses the latest question only.")
st.info(TRAVEL_NOTICE)


@st.cache_resource
def resources():
    return open_collection(), gemini_client()


def show_answer(message):
    st.markdown(message["text"])
    with st.expander("Retrieved source evidence"):
        for match in message["matches"]:
            cited = " • cited" if match["id"] in message["cited_ids"] else ""
            st.caption(f"{match['metadata']['source']} • {page_label(match['metadata'])}{cited}")
            st.code(match["id"], language=None)
            st.text(match["text"])


if "messages" not in st.session_state:
    st.session_state.messages = []
with st.sidebar:
    st.caption(f"Answers generated with {CHAT_MODEL}")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

try:
    collection, client = resources()
except Exception:
    st.error("Could not load the local index or Gemini configuration. Check .env and run python ingest.py --embed if the index is missing.")
    st.stop()

example = None
if not st.session_state.messages:
    st.caption("Try a question")
    for text in [
        "Where should I refuel before traveling to Khunjerab Pass?",
        "What is the best season for Rakaposhi Base Camp?",
        "What transport options are available from Islamabad to Skardu?",
    ]:
        if st.button(text, use_container_width=True):
            example = text

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            show_answer(message)
        else:
            st.markdown(message["text"])

question = st.chat_input("Ask about a destination or route…") or example
if question:
    with st.chat_message("user"):
        st.markdown(question)
    try:
        with st.chat_message("assistant"):
            with st.spinner("Reading the guide…"):
                matches = retrieve(collection, client, question)
                answer = generate_answer(client, question, matches)
            message = {"role": "assistant", **answer, "matches": matches}
            show_answer(message)
        st.session_state.messages.extend([{"role": "user", "text": question}, message])
    except errors.APIError as error:
        st.error(f"Gemini request failed with status {error.code}. Check your API quota and model access, then try again.")
    except Exception:
        st.error("The answer could not be completed. Check your connection and configuration, then try again.")
