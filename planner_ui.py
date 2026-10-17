"""Small Streamlit trip form; admission precedes retrieval and generation."""

from uuid import uuid4

import streamlit as st

from planner import (API_BUDGET, BUDGETS, INTERESTS, MAX_DAYS, MONTHS, RETRIEVAL_MODE,
                     TRANSPORT, build_planner, run_trip, validate_preferences)
from rag import TRAVEL_NOTICE
from usage_limits import PROVIDER_BUSY, UsageLimitError, is_rate_limit
from workflow import chat_model, open_retriever


@st.cache_resource
def planner_resources():
    return build_planner(open_retriever(mode=RETRIEVAL_MODE), chat_model())


def show_planner(limiter, show_evidence, show_text):
    st.markdown('<div class="conversation-heading"><h1>Make room for the north.</h1>'
                '<p>A personal trip outline, grounded in the guide.</p></div>', unsafe_allow_html=True)
    st.caption("Travel days include the outward and return journeys. Plans may be partial when the guide lacks details.")
    with st.form("trip_preferences"):
        left, right = st.columns(2)
        departure = left.text_input("Departure city", value="Gilgit", max_chars=80, key="trip_departure")
        destination = right.text_input("Destination or region", value="Hunza", max_chars=80, key="trip_destination")
        left, right = st.columns(2)
        days = left.number_input("Total travel days", min_value=1, max_value=MAX_DAYS, value=5, key="trip_days")
        transport = right.selectbox("Transport preference", TRANSPORT, key="trip_transport")
        left, right = st.columns(2)
        budget = left.selectbox("Budget preference", BUDGETS, key="trip_budget")
        month = right.selectbox("Travel month, optional", MONTHS, key="trip_month")
        interests = st.multiselect("Travel interests", INTERESTS, default=["Nature", "Sightseeing"], key="trip_interests")
        submitted = st.form_submit_button("Create my trip outline", icon=":material/route:", use_container_width=True)
    if submitted:
        # One event consumed in this run; stored output, not form values, is replayed on reruns.
        try:
            preferences = validate_preferences({"departure": departure, "destination": destination, "days": days,
                                                "transport": transport, "budget": budget, "month": month, "interests": interests})
            with limiter.workflow(st.session_state.usage, "trip_plan", str(uuid4()),
                                  f"{departure} to {destination}", api_budget=API_BUDGET):
                with st.spinner("Finding routes, stays, and a little inspiration..."):
                    result = run_trip(planner_resources(), preferences, trace=False)
                st.session_state.trip_plan = result["plan"]
            st.rerun()
        except (UsageLimitError, ValueError) as error:
            st.info(str(error) if isinstance(error, UsageLimitError)
                    else "Check your trip preferences and try a simpler trip. The guide may lack enough evidence.")
        except Exception as error:
            st.error(PROVIDER_BUSY if is_rate_limit(error) else "The trip could not be completed. Please try again later.")
    st.caption(f"{limiter.remaining(st.session_state.usage, 'trip_plan')} of {limiter.policy.trip_requests} trip plans remaining in this session window.")
    if "trip_plan" in st.session_state:
        plan = st.session_state.trip_plan
        show_text(f"### {plan['preferences']['destination']} trip outline")
        if plan["status"] != "complete":
            st.info("A partial outline" if plan["status"] == "partial" else "This trip is not supported by the guide")
        if plan["overview"]:
            show_text(plan["overview"])
        for day in plan["days"]:
            with st.container(border=True):
                show_text(f"#### Day {day['day']} · {day['title']}")
                show_text(day["text"])
        for topic, text in plan["guidance"].items():
            if text:
                with st.expander(topic, expanded=topic in {"Season", "Safety"}):
                    show_text(text)
        if plan["limitations"]:
            st.markdown("#### Before you make arrangements")
            for line in plan["limitations"]:
                show_text(f"• {line}")
        show_evidence({"text": "", "cited_ids": plan["cited_ids"], "matches": plan["matches"]})
    st.caption(TRAVEL_NOTICE)
