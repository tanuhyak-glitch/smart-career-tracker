SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL COLLATE NOCASE,
    website TEXT DEFAULT '',
    career_page TEXT DEFAULT '',
    location TEXT DEFAULT '',
    industry TEXT DEFAULT '',
    description TEXT DEFAULT '',
    research_notes TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    location TEXT DEFAULT '',
    applied_date TEXT DEFAULT '',
    status TEXT DEFAULT 'Applied',
    notes TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    company_id INTEGER
);

CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER,
    company TEXT NOT NULL DEFAULT '',
    role TEXT DEFAULT '',
    round_name TEXT DEFAULT 'Technical',
    interview_date TEXT NOT NULL,
    interview_time TEXT DEFAULT '',
    mode TEXT DEFAULT 'Online',
    meeting_link TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    outcome TEXT DEFAULT 'Pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT DEFAULT 'General',
    company TEXT DEFAULT '',
    content TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    category TEXT DEFAULT 'Technical',
    level TEXT DEFAULT 'Beginner',
    progress INTEGER DEFAULT 0,
    notes TEXT DEFAULT '',
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    platform TEXT DEFAULT '',
    url TEXT DEFAULT '',
    status TEXT DEFAULT 'Not Started',
    progress INTEGER DEFAULT 0,
    certificate_url TEXT DEFAULT '',
    completed_date TEXT DEFAULT '',
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    technologies TEXT DEFAULT '',
    github_url TEXT DEFAULT '',
    live_url TEXT DEFAULT '',
    status TEXT DEFAULT 'In Progress',
    description TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""