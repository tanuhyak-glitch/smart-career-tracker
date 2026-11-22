import streamlit as st
import pandas as pd

from database.db import query, execute


SKILL_CATEGORIES = [
    "Programming",
    "Web Development",
    "Database",
    "AI/ML",
    "Tools",
    "Soft Skills",
    "Other"
]

LEVELS = [
    "Beginner",
    "Learning",
    "Intermediate",
    "Advanced"
]


def show_skills():

    st.title("💻 Skills & Learning Tracker")

    tabs = st.tabs([
        "Skills",
        "Courses & Certificates",
        "Projects"
    ])

    # ================= SKILLS =================

    with tabs[0]:

        st.subheader("My Skills")

        with st.expander("➕ Add Skill"):

            with st.form("add_skill_form"):

                name = st.text_input("Skill Name")

                category = st.selectbox(
                    "Category",
                    SKILL_CATEGORIES
                )

                level = st.selectbox(
                    "Skill Level",
                    LEVELS
                )

                progress = st.slider(
                    "Progress",
                    0,
                    100,
                    0
                )

                notes = st.text_area("Notes")

                submit = st.form_submit_button(
                    "Save Skill"
                )

            if submit:

                if not name.strip():

                    st.error("Skill name is required.")

                elif query(
                    "SELECT id FROM skills WHERE name=? COLLATE NOCASE",
                    (name.strip(),)
                ):

                    st.warning("Skill already exists.")

                else:

                    execute("""
                        INSERT INTO skills
                        (name, category, level, progress, notes)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        name.strip(),
                        category,
                        level,
                        progress,
                        notes
                    ))

                    st.success("Skill added!")

                    st.rerun()

        skills = query("""
            SELECT *
            FROM skills
            ORDER BY category, name
        """)

        if skills:

            skill_df = pd.DataFrame([
                dict(skill)
                for skill in skills
            ])

            st.dataframe(
                skill_df,
                use_container_width=True,
                hide_index=True
            )

            with st.expander("✏️ Update Skill"):

                skill_id = st.selectbox(
                    "Select Skill",
                    [skill["id"] for skill in skills],
                    format_func=lambda selected_id: next(
                        skill["name"]
                        for skill in skills
                        if skill["id"] == selected_id
                    )
                )

                current = next(
                    skill
                    for skill in skills
                    if skill["id"] == skill_id
                )

                with st.form("update_skill_form"):

                    new_level = st.selectbox(
                        "Level",
                        LEVELS,
                        index=(
                            LEVELS.index(current["level"])
                            if current["level"] in LEVELS
                            else 0
                        )
                    )

                    new_progress = st.slider(
                        "Progress",
                        0,
                        100,
                        int(current["progress"])
                    )

                    new_notes = st.text_area(
                        "Notes",
                        value=current["notes"] or ""
                    )

                    update = st.form_submit_button(
                        "Update"
                    )

                if update:

                    execute("""
                        UPDATE skills
                        SET level=?,
                            progress=?,
                            notes=?,
                            updated_at=CURRENT_TIMESTAMP
                        WHERE id=?
                    """, (
                        new_level,
                        new_progress,
                        new_notes,
                        skill_id
                    ))

                    st.success("Skill updated!")

                    st.rerun()

            with st.expander("🗑️ Delete Skill"):

                delete_skill_id = st.selectbox(
                    "Skill",
                    [skill["id"] for skill in skills],
                    format_func=lambda selected_id: next(
                        skill["name"]
                        for skill in skills
                        if skill["id"] == selected_id
                    ),
                    key="delete_skill"
                )

                confirm = st.checkbox(
                    "Confirm skill deletion",
                    key="confirm_skill_delete"
                )

                if st.button(
                    "Delete Skill",
                    disabled=not confirm
                ):

                    execute(
                        "DELETE FROM skills WHERE id=?",
                        (delete_skill_id,)
                    )

                    st.rerun()

        else:

            st.info("Add your skills to track progress.")

    # ================= COURSES =================

    with tabs[1]:

        st.subheader("Courses & Certificates")

        with st.expander("➕ Add Course"):

            with st.form("add_course_form"):

                name = st.text_input("Course Name")

                platform = st.text_input(
                    "Platform (Coursera, Udemy, Oracle...)"
                )

                url = st.text_input("Course URL")

                status = st.selectbox(
                    "Status",
                    [
                        "Not Started",
                        "In Progress",
                        "Completed"
                    ]
                )

                progress = st.slider(
                    "Progress (%)",
                    0,
                    100,
                    0
                )

                certificate_url = st.text_input(
                    "Certificate URL"
                )

                completed_date = st.text_input(
                    "Completion Date"
                )

                notes = st.text_area("Notes")

                submit = st.form_submit_button(
                    "Save Course"
                )

            if submit:

                if not name.strip():

                    st.error("Course name is required.")

                else:

                    execute("""
                        INSERT INTO courses
                        (
                            name,
                            platform,
                            url,
                            status,
                            progress,
                            certificate_url,
                            completed_date,
                            notes
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        name,
                        platform,
                        url,
                        status,
                        progress,
                        certificate_url,
                        completed_date,
                        notes
                    ))

                    st.success("Course saved!")

                    st.rerun()

        courses = query("""
            SELECT *
            FROM courses
            ORDER BY id DESC
        """)

        if courses:

            st.dataframe(
                pd.DataFrame([
                    dict(course)
                    for course in courses
                ]),
                use_container_width=True,
                hide_index=True
            )

            with st.expander("🗑️ Delete Course"):

                course_id = st.selectbox(
                    "Select Course",
                    [course["id"] for course in courses],
                    format_func=lambda selected_id: next(
                        course["name"]
                        for course in courses
                        if course["id"] == selected_id
                    )
                )

                confirm = st.checkbox(
                    "Confirm deletion",
                    key="confirm_course_delete"
                )

                if st.button(
                    "Delete Course",
                    disabled=not confirm
                ):

                    execute(
                        "DELETE FROM courses WHERE id=?",
                        (course_id,)
                    )

                    st.rerun()

        else:

            st.info("No courses added yet.")

    # ================= PROJECTS =================

    with tabs[2]:

        st.subheader("My Projects")

        with st.expander("➕ Add Project"):

            with st.form("add_project_form"):

                name = st.text_input("Project Name")

                technologies = st.text_input(
                    "Technologies (comma separated)"
                )

                github_url = st.text_input(
                    "GitHub Repository"
                )

                live_url = st.text_input(
                    "Live Deployment"
                )

                status = st.selectbox(
                    "Project Status",
                    [
                        "Planning",
                        "In Progress",
                        "Completed"
                    ]
                )

                description = st.text_area(
                    "Project Description"
                )

                submit = st.form_submit_button(
                    "Save Project"
                )

            if submit:

                if not name.strip():

                    st.error("Project name is required.")

                else:

                    execute("""
                        INSERT INTO projects
                        (
                            name,
                            technologies,
                            github_url,
                            live_url,
                            status,
                            description
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        name,
                        technologies,
                        github_url,
                        live_url,
                        status,
                        description
                    ))

                    st.success("Project saved!")

                    st.rerun()

        projects = query("""
            SELECT *
            FROM projects
            ORDER BY id DESC
        """)

        if projects:

            st.dataframe(
                pd.DataFrame([
                    dict(project)
                    for project in projects
                ]),
                use_container_width=True,
                hide_index=True
            )

            with st.expander("🗑️ Delete Project"):

                project_id = st.selectbox(
                    "Select Project",
                    [project["id"] for project in projects],
                    format_func=lambda selected_id: next(
                        project["name"]
                        for project in projects
                        if project["id"] == selected_id
                    )
                )

                confirm = st.checkbox(
                    "Confirm deletion",
                    key="confirm_project_delete"
                )

                if st.button(
                    "Delete Project",
                    disabled=not confirm
                ):

                    execute(
                        "DELETE FROM projects WHERE id=?",
                        (project_id,)
                    )

                    st.rerun()

        else:

            st.info("No projects added yet.")