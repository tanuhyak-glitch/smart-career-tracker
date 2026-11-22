import streamlit as st

from database.db import get_connection


STATUSES = [
    "Applied",
    "Assessment",
    "Interview",
    "Selected",
    "Rejected",
    "Withdrawn"
]


def show_applications():

    st.title("📋 Application Management")
    st.caption("Manage your job and internship applications")

    # ---------------- ADD APPLICATION ----------------

    st.subheader("➕ Add New Application")

    with st.form("add_application_form"):

        company = st.text_input("Company Name")
        role = st.text_input("Job Role")
        location = st.text_input("Location")

        applied_date = st.date_input("Application Date")

        status = st.selectbox(
            "Application Status",
            STATUSES
        )

        notes = st.text_area("Notes")

        submit = st.form_submit_button(
            "Add Application",
            use_container_width=True
        )

        if submit:

            if not company.strip() or not role.strip():
                st.error("Company and role are required.")

            else:

                conn = get_connection()

                # Prevent accidental duplicate entries
                duplicate = conn.execute("""
                    SELECT id
                    FROM applications
                    WHERE LOWER(TRIM(company)) = LOWER(TRIM(?))
                    AND LOWER(TRIM(role)) = LOWER(TRIM(?))
                """, (company, role)).fetchone()

                if duplicate:

                    st.warning(
                        "This company and role already exist "
                        "in your tracker. You can edit the "
                        "existing application instead."
                    )

                else:

                    conn.execute("""
                        INSERT INTO applications
                        (company, role, location, applied_date, status, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        company.strip(),
                        role.strip(),
                        location.strip(),
                        applied_date.isoformat(),
                        status,
                        notes.strip()
                    ))

                    conn.commit()

                    st.session_state["app_success"] = (
                        f"Application added for {company}!"
                    )

                conn.close()

                st.rerun()

    # Persistent success message
    if "app_success" in st.session_state:

        st.success(st.session_state["app_success"])

        del st.session_state["app_success"]

    st.divider()

    # ---------------- FETCH APPLICATIONS ----------------

    conn = get_connection()

    rows = conn.execute("""
        SELECT *
        FROM applications
        ORDER BY applied_date DESC, id DESC
    """).fetchall()

    conn.close()

    applications = [dict(row) for row in rows]

    st.subheader("📁 Your Applications")

    # ---------------- SEARCH & FILTER ----------------

    search = st.text_input(
        "🔍 Search company or role",
        placeholder="Search Google, Python Developer..."
    )

    filter_status = st.selectbox(
        "Filter by status",
        ["All"] + STATUSES
    )

    filtered = applications

    if search:

        search_lower = search.lower()

        filtered = [
            app for app in filtered
            if search_lower in app["company"].lower()
            or search_lower in app["role"].lower()
            or search_lower in (app["location"] or "").lower()
        ]

    if filter_status != "All":

        filtered = [
            app for app in filtered
            if app["status"] == filter_status
        ]

    st.write(f"Showing {len(filtered)} applications")

    # ---------------- TABLE VIEW ----------------

    if filtered:

        display_data = [
            {
                "ID": app["id"],
                "Company": app["company"],
                "Role": app["role"],
                "Location": app["location"],
                "Date": app["applied_date"],
                "Status": app["status"]
            }
            for app in filtered
        ]

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No applications match your search.")

    st.divider()

    # ---------------- EDIT APPLICATION ----------------

    st.subheader("✏️ Edit Application")

    if applications:

        app_ids = [app["id"] for app in applications]

        selected_id = st.selectbox(
            "Select application to edit",
            app_ids,
            format_func=lambda app_id: (
                f"ID {app_id} | "
                f"{next(a['company'] for a in applications if a['id'] == app_id)} | "
                f"{next(a['role'] for a in applications if a['id'] == app_id)}"
            ),
            key="edit_select"
        )

        selected = next(
            app for app in applications
            if app["id"] == selected_id
        )

        with st.form("edit_application_form"):

            edit_company = st.text_input(
                "Company",
                value=selected["company"],
                key=f"company_{selected_id}"
            )

            edit_role = st.text_input(
                "Role",
                value=selected["role"],
                key=f"role_{selected_id}"
            )

            edit_location = st.text_input(
                "Location",
                value=selected["location"] or "",
                key=f"location_{selected_id}"
            )

            edit_date = st.date_input(
                "Application Date",
                value=selected["applied_date"],
                key=f"date_{selected_id}"
            )

            edit_status = st.selectbox(
                "Status",
                STATUSES,
                index=STATUSES.index(selected["status"])
                if selected["status"] in STATUSES else 0,
                key=f"status_{selected_id}"
            )

            edit_notes = st.text_area(
                "Notes",
                value=selected["notes"] or "",
                key=f"notes_{selected_id}"
            )

            save_changes = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if save_changes:

                if not edit_company.strip() or not edit_role.strip():

                    st.error("Company and role cannot be empty.")

                else:

                    conn = get_connection()

                    conn.execute("""
                        UPDATE applications
                        SET company = ?,
                            role = ?,
                            location = ?,
                            applied_date = ?,
                            status = ?,
                            notes = ?
                        WHERE id = ?
                    """, (
                        edit_company.strip(),
                        edit_role.strip(),
                        edit_location.strip(),
                        edit_date.isoformat(),
                        edit_status,
                        edit_notes.strip(),
                        selected_id
                    ))

                    conn.commit()
                    conn.close()

                    st.session_state["app_success"] = (
                        "Application updated successfully!"
                    )

                    st.rerun()

    else:

        st.info("No applications available to edit.")

    st.divider()

    # ---------------- DELETE APPLICATION ----------------

    st.subheader("🗑️ Delete Application")

    if applications:

        delete_id = st.selectbox(
            "Select application to delete",
            app_ids,
            format_func=lambda app_id: (
                f"ID {app_id} | "
                f"{next(a['company'] for a in applications if a['id'] == app_id)} | "
                f"{next(a['role'] for a in applications if a['id'] == app_id)}"
            ),
            key="delete_select"
        )

        confirm_delete = st.checkbox(
            "I confirm that I want to delete this application.",
            key="confirm_delete"
        )

        if st.button("Delete Selected Application"):

            if not confirm_delete:

                st.warning("Please confirm deletion first.")

            else:

                conn = get_connection()

                conn.execute(
                    "DELETE FROM applications WHERE id = ?",
                    (delete_id,)
                )

                conn.commit()
                conn.close()

                st.session_state["app_success"] = (
                    "Application deleted successfully!"
                )

                st.rerun()

    else:

        st.info("No applications available to delete.")
        st.info("No applications available to delete.")