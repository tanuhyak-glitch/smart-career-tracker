import streamlit as st
import pandas as pd

from database.db import query, execute


def show_companies():

    st.title("🏢 Company Management")

    # ADD COMPANY

    with st.expander("➕ Add Company"):

        with st.form("add_company_form"):

            name = st.text_input("Company Name *")
            website = st.text_input("Company Website")
            career_page = st.text_input("Career Page")
            location = st.text_input("Location")
            industry = st.text_input("Industry")

            description = st.text_area(
                "Company Description"
            )

            research_notes = st.text_area(
                "Research Notes"
            )

            submit = st.form_submit_button(
                "Save Company"
            )

        if submit:

            if not name.strip():

                st.error("Company name is required.")

            elif query(
                "SELECT id FROM companies WHERE name=? COLLATE NOCASE",
                (name.strip(),)
            ):

                st.warning("This company already exists.")

            else:

                execute("""
                    INSERT INTO companies
                    (
                        name,
                        website,
                        career_page,
                        location,
                        industry,
                        description,
                        research_notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    name.strip(),
                    website,
                    career_page,
                    location,
                    industry,
                    description,
                    research_notes
                ))

                st.success("Company saved!")
                st.rerun()

    # DISPLAY COMPANIES

    companies = query("""
        SELECT *
        FROM companies
        ORDER BY name
    """)

    st.subheader("Your Companies")

    if not companies:

        st.info("No companies added yet.")

        return

    df = pd.DataFrame([
        dict(company)
        for company in companies
    ])

    search = st.text_input("Search companies")

    if search:

        df = df[
            df.astype(str).apply(
                lambda column: column.str.contains(
                    search,
                    case=False,
                    na=False
                )
            ).any(axis=1)
        ]

    st.dataframe(
        df[
            [
                "name",
                "industry",
                "location",
                "website",
                "career_page"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # EDIT COMPANY

    with st.expander("✏️ Edit Company"):

        company_ids = [
            company["id"]
            for company in companies
        ]

        selected_id = st.selectbox(
            "Choose company",
            company_ids,
            format_func=lambda company_id: next(
                company["name"]
                for company in companies
                if company["id"] == company_id
            )
        )

        current = next(
            company
            for company in companies
            if company["id"] == selected_id
        )

        with st.form("edit_company_form"):

            new_name = st.text_input(
                "Company Name",
                value=current["name"]
            )

            new_website = st.text_input(
                "Website",
                value=current["website"] or ""
            )

            new_career = st.text_input(
                "Career Page",
                value=current["career_page"] or ""
            )

            new_location = st.text_input(
                "Location",
                value=current["location"] or ""
            )

            new_industry = st.text_input(
                "Industry",
                value=current["industry"] or ""
            )

            new_description = st.text_area(
                "Description",
                value=current["description"] or ""
            )

            new_research = st.text_area(
                "Research Notes",
                value=current["research_notes"] or ""
            )

            update = st.form_submit_button(
                "Update Company"
            )

        if update:

            if not new_name.strip():

                st.error("Company name cannot be empty.")

            else:

                try:

                    execute("""
                        UPDATE companies
                        SET
                            name=?,
                            website=?,
                            career_page=?,
                            location=?,
                            industry=?,
                            description=?,
                            research_notes=?
                        WHERE id=?
                    """, (
                        new_name.strip(),
                        new_website,
                        new_career,
                        new_location,
                        new_industry,
                        new_description,
                        new_research,
                        selected_id
                    ))

                    # Keep application company names synchronized

                    execute("""
                        UPDATE applications
                        SET company=?
                        WHERE company_id=?
                    """, (
                        new_name.strip(),
                        selected_id
                    ))

                    st.success("Company updated!")

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Could not update company: {error}"
                    )

    # DELETE COMPANY

    with st.expander("🗑️ Delete Company"):

        delete_id = st.selectbox(
            "Select company to delete",
            [company["id"] for company in companies],
            format_func=lambda company_id: next(
                company["name"]
                for company in companies
                if company["id"] == company_id
            ),
            key="delete_company"
        )

        selected_company = next(
            company
            for company in companies
            if company["id"] == delete_id
        )

        linked_applications = query("""
            SELECT COUNT(*) AS total
            FROM applications
            WHERE company_id = ?
               OR company = ? COLLATE NOCASE
        """, (
            delete_id,
            selected_company["name"]
        ))

        linked_count = linked_applications[0]["total"]

        if linked_count > 0:

            st.warning(
                f"This company has {linked_count} linked application(s). "
                "Delete or update those applications first."
            )

        confirm = st.checkbox(
            "I confirm deleting this company",
            key="confirm_company_delete"
        )

        if st.button(
            "Delete Company",
            disabled=(not confirm or linked_count > 0)
        ):

            execute(
                "DELETE FROM companies WHERE id=?",
                (delete_id,)
            )

            st.success("Company deleted.")

            st.rerun()