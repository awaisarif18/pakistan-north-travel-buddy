"""Run with: streamlit run app.py. Presentation only; RAG runs in workflow.py."""

from html import escape
from pathlib import Path
import os
import re
from uuid import uuid4

import streamlit as st
from langgraph.checkpoint.memory import InMemorySaver

from rag import TRAVEL_NOTICE, page_label
from workflow import build_workflow, chat_model, needs_rewrite, open_retriever, run_question
from usage_limits import Policy, ProcessLimiter, UsageLimitError, is_rate_limit, new_usage, PROVIDER_BUSY

st.set_page_config(page_title="Pakistan North Tours AI", page_icon="🏔️", layout="wide")
st.html(f"<style>{Path(__file__).with_name('ui.css').read_text(encoding='utf-8')}</style>")

MOUNTAIN = '<span class="mountain-icon" aria-hidden="true"><i></i><b></b></span>'
FEEDBACK_URL = os.getenv("FEEDBACK_FORM_URL", "").strip() or "https://forms.gle/5McdABdSnigwwdNz5"
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
    # Only stateless clients are shared; each session owns its graph/checkpointer.
    return open_retriever(mode=os.getenv("RETRIEVAL_MODE", "dense")), chat_model(), chat_model(rewrite=True)


@st.cache_resource
def shared_limiter():
    return ProcessLimiter(Policy.from_env())


def queue_question():
    st.session_state.pending_submission = {"id": str(uuid4()), "text": st.session_state.chat_question}


try:
    limiter = shared_limiter()
except (ValueError, TypeError):
    st.error("The travel assistant is temporarily unavailable. Please try again later.")
    st.stop()
if "usage" not in st.session_state:
    st.session_state.usage = new_usage()


def show_text(text):
    # Travel prices are literal currency, not LaTeX. Keep stored answers unchanged.
    st.markdown(re.sub(r"(?<!\\)\$", r"\\$", text))


def show_answer(message):
    # Only presentation changes: retain the backend's exact page values and text.
    show_text(re.sub(CITATION, r"`\1`", message["text"]))
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
                show_text(match["text"])
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
                show_text(message["text"])


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


with st.sidebar:
    st.html(f'<div class="sidebar-brand"><div class="brand-mark">{MOUNTAIN}</div>'
            '<div><strong>North Tours</strong><span>Your Pakistan travel companion</span></div></div>')
    view = st.radio("Explore", ["Chat", "Plan a Trip"], key="app_view", label_visibility="collapsed")
    if st.button("New conversation", icon=":material/edit_square:", key="clear_chat", use_container_width=True):
        st.session_state.pop("conversation", None)
        st.session_state.pop("pending_submission", None)
        st.rerun()
    st.caption(f"{limiter.remaining(st.session_state.usage)} of {limiter.policy.chat_requests} chat questions remaining in this session window.")
    st.html('<div class="sidebar-section"><p class="eyebrow">The guide</p>'
            '<h2>A little closer to the north.</h2><p>From Hunza’s trails to the valleys of Kalash. '
            'Explore at your own pace, with the guide beside you.</p></div>'
            '<div class="sidebar-facts"><span>92 pages</span><span>8 regions</span><span>PDF sources</span></div>')
    with st.expander("About this companion", icon=":material/info:"):
        st.write("Answers come from your Pakistan North Tours guide. Open the source evidence beneath an answer to read the passages behind it.")
        st.caption("Ask follow-up questions about your current destination. Context uses the last four exchanges and resets with a new conversation.")
        st.link_button("Help Test Future Releases", FEEDBACK_URL, icon=":material/science:", use_container_width=True)
        st.caption("Volunteer through the form. Only opt in and provide an email if you want future testing invitations.")
    st.link_button("Send Feedback", FEEDBACK_URL, icon=":material/rate_review:", use_container_width=True)
    st.caption("Opens Google Forms. Your chat and trip details are not sent automatically.")
    st.html('<p class="sidebar-note">For thoughtful planning.<br>Always check local conditions before you go.</p>')

st.html('<header class="workspace-header"><span>Pakistan North Tours AI</span>'
        '<span class="workspace-tag"><i></i> Your guide to the north</span></header>')
if view == "Plan a Trip":
    from planner_ui import show_planner
    show_planner(limiter, show_answer, show_text)
    st.stop()
try:
    if "conversation" not in st.session_state:
        st.session_state.conversation = (str(uuid4()), build_workflow(*resources(), checkpointer=InMemorySaver()))
    thread_id, workflow = st.session_state.conversation
    turns = workflow.get_state({"configurable": {"thread_id": thread_id}}).values.get("turns", [])
except Exception:
    st.error("The guide could not be opened. Check the local index and Gemini configuration, then reload the app.")
    st.stop()

example = empty_state() if not turns else None
if turns:
    st.html('<div class="conversation-heading"><h1>A little guidance, wherever you go.</h1>'
            '<p>Answers from the guide. Sources within reach.</p></div>')
with st.container(key="conversation"):
    for index, turn in enumerate(turns):
        show_message({"role": "user", "text": turn["question"]}, f"{index}_user")
        show_message({"role": "assistant", **turn["answer"], "matches": turn["matches"]}, f"{index}_assistant")

with st.container(key="travel_note"):
    st.caption(TRAVEL_NOTICE)
st.chat_input("Ask about your next trip…", key="chat_question", on_submit=queue_question,
              max_chars=limiter.policy.question_chars)
if example:
    st.session_state.pending_submission = {"id": str(uuid4()), "text": example}
submission = st.session_state.pop("pending_submission", None)
if submission:
    try:
        budget = {"generation": 1, "embedding": 0 if os.getenv("RETRIEVAL_MODE", "dense") == "bm25" else 1}
        if needs_rewrite({"question": submission["text"], "turns": turns}):
            budget["generation"] += 1
        with limiter.workflow(st.session_state.usage, "chat", submission["id"], submission["text"], api_budget=budget):
            show_message({"role": "user", "text": submission["text"]}, "pending")
            with st.container(key="chat_assistant_pending"):
                with st.chat_message("assistant", avatar=":material/landscape:"):
                    with st.spinner("Searching the guide…"):
                        run_question(workflow, submission["text"], thread_id=thread_id, trace=False)
        st.rerun()
    except UsageLimitError as error:
        st.info(str(error))
    except Exception as error:
        st.error(PROVIDER_BUSY if is_rate_limit(error) else "The answer could not be completed. Please try again later.")
