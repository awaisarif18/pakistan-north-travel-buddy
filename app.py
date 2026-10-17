"""Run with: streamlit run app.py. Presentation only; RAG lives in rag.py."""

from html import escape
from pathlib import Path
import re

import streamlit as st
from google.genai import errors

from rag import TRAVEL_NOTICE, generate_answer, gemini_client, open_collection, page_label, retrieve

st.set_page_config(page_title="Pakistan North Tours AI", page_icon="🏔️", layout="wide")
st.html(f"<style>{Path(__file__).with_name('ui.css').read_text(encoding='utf-8')}</style>")

MOUNTAIN = '<span class="mountain-icon" aria-hidden="true"><i></i><b></b></span>'
EXAMPLES = [
    ("Khunjerab fuel stops", "local_gas_station", "Where should I refuel before traveling to Khunjerab Pass?"),
    ("Rakaposhi trekking season", "hiking", "What is the best season for Rakaposhi Base Camp?"),
    ("Islamabad to Skardu", "directions_bus", "What transport options are available from Islamabad to Skardu?"),
    ("Treks around Hunza", "landscape", "What are the trekking options near Hunza?"),
    ("The Kalash valleys", "explore", "Which three valleys make up the Kalash Valleys group in this guide?"),
    ("Babusar fuel precautions", "route", "What fuel precautions are necessary when crossing Babusar Pass?"),
]
CITATION = r"\[(PDF pages? \d+(?:-\d+)?(?:; PDF pages? \d+(?:-\d+)?)*)\]"


@st.cache_resource
def resources():
    return open_collection(), gemini_client()


def show_answer(message):
    # Only presentation changes: retain the backend's exact page values and text.
    st.markdown(re.sub(CITATION, r"`\1`", message["text"]))
    matches = message["matches"]
    if not matches:
        return
    cited_count = len(message["cited_ids"])
    label = f"Source evidence · {cited_count} cited · {len(matches)} passages"
    with st.expander(label, icon=":material/library_books:"):
        # Show cited evidence first; keep the retriever's original rank visible.
        ordered = sorted(enumerate(matches, 1), key=lambda item: item[1]["id"] not in message["cited_ids"])
        for rank, match in ordered:
            cited = match["id"] in message["cited_ids"]
            preview = " ".join(match["text"].split())
            preview = preview[:220].rsplit(" ", 1)[0] + "…" if len(preview) > 220 else preview
            st.html(f'<div class="source-card"><div class="source-meta">'
                    f'<span class="page-badge">{escape(page_label(match["metadata"]))}</span>'
                    f'<span class="source-kind">{"Cited in answer" if cited else "Retrieved passage"} · {rank:02d}</span>'
                    f'</div><p>{escape(preview)}</p></div>')
            with st.expander(f"Read full passage · {page_label(match['metadata'])}"):
                st.caption(match["metadata"]["source"])
                st.markdown(match["text"])
                st.caption(f"Passage reference: {match['id']}")


def show_message(message, key):
    role = message["role"]
    with st.container(key=f"chat_{role}_{key}"):
        avatar = ":material/landscape:" if role == "assistant" else ":material/person:"
        with st.chat_message(role, avatar=avatar):
            st.caption("North Tours AI" if role == "assistant" else "You")
            if role == "assistant":
                show_answer(message)
            else:
                st.markdown(message["text"])


def empty_state():
    st.html(f'<section class="welcome"><div class="welcome-mark">{MOUNTAIN}</div>'
            '<p class="eyebrow">A little guidance for the road ahead</p>'
            '<h1>Pakistan North Tours <span>AI</span></h1>'
            '<p class="welcome-description">Routes, treks, and local know-how for Northern Pakistan.</p>'
            '<div class="guide-pill">92-page travel guide <span>·</span> Answers with PDF sources</div></section>')
    with st.container(key="suggestions"):
        st.caption("A place to start")
        columns = st.columns(2, gap="small")
        for index, (label, icon, question) in enumerate(EXAMPLES):
            with columns[index % 2]:
                if st.button(label, icon=f":material/{icon}:", key=f"example_{index}", use_container_width=True):
                    return question
    st.html('<section class="ask-about"><h2>A few things you can ask</h2><div class="ask-grid">'
            '<div><h3>The way there</h3><p>Roads, transport &amp; fuel stops</p></div>'
            '<div><h3>A place to explore</h3><p>Lakes, trails &amp; mountain valleys</p></div>'
            '<div><h3>Plan the details</h3><p>Seasons, stays &amp; guide prices</p></div></div></section>')
    return None


if "messages" not in st.session_state:
    st.session_state.messages = []
with st.sidebar:
    st.html(f'<div class="sidebar-brand"><div class="brand-mark">{MOUNTAIN}</div>'
            '<div><strong>North Tours</strong><span>Your Pakistan travel companion</span></div></div>')
    if st.button("New conversation", icon=":material/edit_square:", key="clear_chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.html('<div class="sidebar-section"><p class="eyebrow">The guide</p>'
            '<h2>A little closer to the north.</h2><p>From Hunza’s trails to the valleys of Kalash. '
            'Explore at your own pace, with the guide beside you.</p></div>'
            '<div class="sidebar-facts"><span>92 pages</span><span>8 regions</span><span>PDF sources</span></div>')
    with st.expander("About this companion", icon=":material/info:"):
        st.write("Answers come from your Pakistan North Tours guide. Open the source evidence beneath an answer to read the passages behind it.")
        st.caption("Name the destination in each question. Earlier messages are shown for reference; follow-up questions are not automatically linked.")
    st.html('<p class="sidebar-note">For thoughtful planning.<br>Always check local conditions before you go.</p>')

st.html('<header class="workspace-header"><span>Pakistan North Tours AI</span>'
        '<span class="workspace-tag"><i></i> Your guide to the north</span></header>')
try:
    collection, client = resources()
except Exception:
    st.error("The guide could not be opened. Check the local index and Gemini configuration, then reload the app.")
    st.stop()

example = empty_state() if not st.session_state.messages else None
if st.session_state.messages:
    st.html('<div class="conversation-heading"><h1>A little guidance, wherever you go.</h1>'
            '<p>Answers from the guide. Sources within reach.</p></div>')
with st.container(key="conversation"):
    for index, message in enumerate(st.session_state.messages):
        show_message(message, index)

with st.container(key="travel_note"):
    st.caption(TRAVEL_NOTICE)
question = st.chat_input("Ask about your next trip…") or example
if question:
    show_message({"role": "user", "text": question}, "pending")
    try:
        with st.container(key="chat_assistant_pending"):
            with st.chat_message("assistant", avatar=":material/landscape:"):
                with st.spinner("Searching the guide…"):
                    matches = retrieve(collection, client, question)
                    answer = generate_answer(client, question, matches)
        message = {"role": "assistant", **answer, "matches": matches}
        st.session_state.messages.extend([{"role": "user", "text": question}, message])
        st.rerun()
    except errors.APIError as error:
        st.error(f"The guide couldn't answer just now. Gemini returned status {error.code}; check quota or model access and try again.")
    except Exception:
        st.error("The answer could not be completed. Check your connection and configuration, then try again.")
