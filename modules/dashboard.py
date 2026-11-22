import streamlit as st
import pandas as pd

from database.db import get_connection


def show_dashboard():

    st.title("📊 Career Dashboard")
    st.caption("Your job search at a glance")

    conn = get_connection()

    total = conn.execute(
        "SELECT COUNT(*) FROM applications"
    ).fetchone()[0]

    interviews = conn.execute(
        "SELECT COUNT(*) FROM applications WHERE status = 'Interview'"
    ).fetchone()[0]

    selected = conn.execute(
        "SELECT COUNT(*) FROM applications WHERE status = 'Selected'"
    ).fetchone()[0]

    rejected = conn.execute(
        "SELECT COUNT(*) FROM applications WHERE status = 'Rejected'"
    ).fetchone()[0]

    assessment = conn.execute(
        "SELECT COUNT(*) FROM applications WHERE status = 'Assessment'"
    ).fetchone()[0]

    status_data = conn.execute("""
        SELECT status, COUNT(*) AS total
        FROM applications
        GROUP BY status
        ORDER BY total DESC
    """).fetchall()

    recent = conn.execute("""
        SELECT company, role, status, applied_date
        FROM applications
        ORDER BY applied_date DESC, id DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    # Metrics
    c1, c2, c3 = st.columns(3)

    c1.metric("Total Applications", total)
    c2.metric("Interviews", interviews)
    c3.metric("Selected", selected)

    c4, c5, c6 = st.columns(3)

    c4.metric("Assessments", assessment)
    c5.metric("Rejected", rejected)
    c6.metric(
        "Interview Rate",
        f"{(interviews / total * 100):.1f}%"
        if total else "0%"
    )

    st.divider()

    # Application status chart
    st.subheader("Application Status Breakdown")

    if status_data:

        chart_df = pd.DataFrame(
            [dict(row) for row in status_data]
        )

        chart_df = chart_df.set_index("status")

        st.bar_chart(chart_df["total"])

    else:
        st.info("Add applications to see your analytics.")

    st.divider()

    # Recent applications
    st.subheader("🕒 Recent Applications")

    if recent:
        st.dataframe(
            [dict(row) for row in recent],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No applications yet.")