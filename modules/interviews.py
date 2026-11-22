import streamlit as st
import pandas as pd

from datetime import date, time

from database.db import query, execute


def show_interviews():

    st.title("🎤 Interview Tracker")

    applications = query("""
        SELECT id, company, role
        FROM applications
        ORDER BY id DESC
    """)

    # ADD INTERVIEW

    with st.expander("➕ Schedule Interview"):

        with st.form("add_interview_form"):

            application_id = st.selectbox(
                "Link Application (Optional)",
                [None] + [
                    application["id"]
                    for application in applications
                ],
                format_func=lambda selected_id:
                    "None" if selected_id is None
                    else next(
                        f"{application['company']} - "
                        f"{application['role']}"
                        for application in applications
                        if application["id"] == selected_id
                    )
            )

            company = st.text_input("Company")
            role = st.text_input("Role")

            round_name = st.selectbox(
                "Interview Round",
                [
                    "HR",
                    "Technical",
                    "Coding",
                    "Managerial",
                    "Final",
                    "Other"
                ]
            )

            interview_date = st.date_input(
                "Interview Date",
                value=date.today()
            )

            interview_time = st.time_input(
                "Interview Time",
                value=time(10, 0)
            )

            mode = st.selectbox(
                "Interview Mode",
                [
                    "Online",
                    "In-person",
                    "Phone"
                ]
            )

            meeting_link = st.text_input(
                "Meeting Link / Location"
            )

            notes = st.text_area(
                "Preparation Notes"
            )

            submit = st.form_submit_button(
                "Schedule Interview"
            )

        if submit:

            if application_id is not None:

                selected_application = next(
                    application
                    for application in applications
                    if application["id"] == application_id
                )

                company = selected_application["company"]
                role = selected_application["role"]

            if not company.strip():

                st.error("Company name is required.")

            else:

                execute("""
                    INSERT INTO interviews
                    (
                        application_id,
                        company,
                        role,
                        round_name,
                        interview_date,
                        interview_time,
                        mode,
                        meeting_link,
                        notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    application_id,
                    company,
                    role,
                    round_name,
                    interview_date.isoformat(),
                    interview_time.strftime("%H:%M"),
                    mode,
                    meeting_link,
                    notes
                ))

                st.success("Interview scheduled!")

                st.rerun()

    # VIEW INTERVIEWS

    interviews = query("""
        SELECT *
        FROM interviews
        ORDER BY interview_date, interview_time
    """)

    st.subheader("Scheduled Interviews")

    if not interviews:

        st.info("No interviews scheduled yet.")

        return

    df = pd.DataFrame([
        dict(interview)
        for interview in interviews
    ])

    st.dataframe(
        df[
            [
                "company",
                "role",
                "round_name",
                "interview_date",
                "interview_time",
                "mode",
                "outcome"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # UPDATE OUTCOME

    with st.expander("✏️ Update Interview"):

        interview_id = st.selectbox(
            "Select Interview",
            [interview["id"] for interview in interviews],
            format_func=lambda selected_id: next(
                f"{interview['company']} | "
                f"{interview['round_name']} | "
                f"{interview['interview_date']}"
                for interview in interviews
                if interview["id"] == selected_id
            )
        )

        current = next(
            interview
            for interview in interviews
            if interview["id"] == interview_id
        )

        outcomes = [
            "Pending",
            "Passed",
            "Failed",
            "Rescheduled"
        ]

        with st.form("update_interview_form"):

            outcome = st.selectbox(
                "Outcome",
                outcomes,
                index=(
                    outcomes.index(current["outcome"])
                    if current["outcome"] in outcomes
                    else 0
                )
            )

            updated_notes = st.text_area(
                "Notes",
                value=current["notes"] or ""
            )

            update = st.form_submit_button(
                "Update Interview"
            )

        if update:

            execute("""
                UPDATE interviews
                SET outcome=?, notes=?
                WHERE id=?
            """, (
                outcome,
                updated_notes,
                interview_id
            ))

            st.success("Interview updated!")

            st.rerun()

    # DELETE

    with st.expander("🗑️ Delete Interview"):

        delete_id = st.selectbox(
            "Select interview",
            [interview["id"] for interview in interviews],
            key="delete_interview",
            format_func=lambda selected_id: next(
                f"{interview['company']} - "
                f"{interview['interview_date']}"
                for interview in interviews
                if interview["id"] == selected_id
            )
        )

        confirm = st.checkbox(
            "Confirm deletion",
            key="confirm_interview_delete"
        )

        if st.button(
            "Delete Interview",
            disabled=not confirm
        ):

            execute(
                "DELETE FROM interviews WHERE id=?",
                (delete_id,)
            )

            st.success("Interview deleted.")

            st.rerun()