import streamlit as st
import pandas as pd

from database.db import query, execute


CATEGORIES = [
    "General",
    "Company Research",
    "Interview Preparation",
    "Technical",
    "HR",
    "DSA",
    "Project",
    "Other"
]


def show_notes():

    st.title("📝 Notes & Preparation")

    # ADD NOTE

    with st.expander("➕ Add Note"):

        with st.form("add_note_form"):

            title = st.text_input("Note Title *")

            category = st.selectbox(
                "Category",
                CATEGORIES
            )

            company = st.text_input(
                "Related Company (Optional)"
            )

            content = st.text_area(
                "Note Content",
                height=200
            )

            submit = st.form_submit_button(
                "Save Note"
            )

        if submit:

            if not title.strip() or not content.strip():

                st.error(
                    "Title and content are required."
                )

            else:

                execute("""
                    INSERT INTO notes
                    (title, category, company, content)
                    VALUES (?, ?, ?, ?)
                """, (
                    title.strip(),
                    category,
                    company,
                    content
                ))

                st.success("Note saved!")

                st.rerun()

    # DISPLAY

    notes = query("""
        SELECT *
        FROM notes
        ORDER BY updated_at DESC, id DESC
    """)

    st.subheader("Your Notes")

    if not notes:

        st.info("No notes created yet.")

        return

    df = pd.DataFrame([
        dict(note)
        for note in notes
    ])

    search = st.text_input("Search Notes")

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
                "title",
                "category",
                "company",
                "updated_at"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # VIEW NOTE

    with st.expander("📖 View Note"):

        note_id = st.selectbox(
            "Select Note",
            [note["id"] for note in notes],
            format_func=lambda selected_id: next(
                note["title"]
                for note in notes
                if note["id"] == selected_id
            )
        )

        selected_note = next(
            note
            for note in notes
            if note["id"] == note_id
        )

        st.markdown(
            f"### {selected_note['title']}"
        )

        st.caption(
            f"Category: {selected_note['category']} "
            f"| Company: {selected_note['company'] or 'None'}"
        )

        st.markdown(selected_note["content"])

    # EDIT

    with st.expander("✏️ Edit Note"):

        edit_id = st.selectbox(
            "Choose Note",
            [note["id"] for note in notes],
            key="edit_note_selection",
            format_func=lambda selected_id: next(
                note["title"]
                for note in notes
                if note["id"] == selected_id
            )
        )

        current = next(
            note
            for note in notes
            if note["id"] == edit_id
        )

        with st.form("edit_note_form"):

            new_title = st.text_input(
                "Title",
                value=current["title"]
            )

            new_category = st.selectbox(
                "Category",
                CATEGORIES,
                index=(
                    CATEGORIES.index(current["category"])
                    if current["category"] in CATEGORIES
                    else 0
                )
            )

            new_company = st.text_input(
                "Company",
                value=current["company"] or ""
            )

            new_content = st.text_area(
                "Content",
                value=current["content"] or "",
                height=200
            )

            update = st.form_submit_button(
                "Update Note"
            )

        if update:

            execute("""
                UPDATE notes
                SET
                    title=?,
                    category=?,
                    company=?,
                    content=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (
                new_title,
                new_category,
                new_company,
                new_content,
                edit_id
            ))

            st.success("Note updated!")

            st.rerun()

    # DELETE

    with st.expander("🗑️ Delete Note"):

        delete_id = st.selectbox(
            "Select note to delete",
            [note["id"] for note in notes],
            key="delete_note_selection",
            format_func=lambda selected_id: next(
                note["title"]
                for note in notes
                if note["id"] == selected_id
            )
        )

        confirm = st.checkbox(
            "Confirm deletion",
            key="confirm_note_delete"
        )

        if st.button(
            "Delete Note",
            disabled=not confirm
        ):

            execute(
                "DELETE FROM notes WHERE id=?",
                (delete_id,)
            )

            st.success("Note deleted.")

            st.rerun()