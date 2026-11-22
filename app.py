import streamlit as st

from database.db import initialize_database

from modules.dashboard import show_dashboard
from modules.applications import show_applications
from modules.companies import show_companies
from modules.interviews import show_interviews
from modules.notes import show_notes
from modules.skills import show_skills
from modules.ai_assistant import show_ai_assistant


st.set_page_config(
    page_title="Smart Career Tracker",
    page_icon="🎯",
    layout="wide"
)

initialize_database()


st.sidebar.title("🎯 Career Tracker")

st.sidebar.caption(
    "Your personal career management workspace"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Applications",
        "Companies",
        "Interviews",
        "Notes & Preparation",
        "Skills & Learning",
        "AI Career Assistant"
    ]
)


if page == "Dashboard":
    show_dashboard()

elif page == "Applications":
    show_applications()

elif page == "Companies":
    show_companies()

elif page == "Interviews":
    show_interviews()

elif page == "Notes & Preparation":
    show_notes()

elif page == "Skills & Learning":
    show_skills()

elif page == "AI Career Assistant":
    show_ai_assistant()