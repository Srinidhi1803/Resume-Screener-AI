import sqlite3
import json
import os

DB_NAME = "database.db"

def get_db_connection():
    """Establish connection to SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Jobs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            job_description TEXT NOT NULL,
            min_experience REAL DEFAULT 0,
            required_education TEXT,
            required_skills TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Candidates Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            candidate_name TEXT NOT NULL,
            filename TEXT NOT NULL,
            resume_text TEXT,
            skill_score REAL DEFAULT 0,
            experience_score REAL DEFAULT 0,
            education_score REAL DEFAULT 0,
            tfidf_score REAL DEFAULT 0,
            final_score REAL DEFAULT 0,
            rank_order INTEGER DEFAULT 0,
            matched_skills TEXT,
            missing_skills TEXT,
            extracted_experience REAL DEFAULT 0,
            extracted_education TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def save_job(job_title, job_description, min_experience, required_education, required_skills):
    """Save a job screening record into database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO jobs (job_title, job_description, min_experience, required_education, required_skills)
        VALUES (?, ?, ?, ?, ?)
    ''', (job_title, job_description, min_experience, required_education, required_skills))

    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return job_id

def save_candidate(job_id, candidate_data):
    """Save candidate analysis results into database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    matched_json = json.dumps(candidate_data.get('matched_skills', []))
    missing_json = json.dumps(candidate_data.get('missing_skills', []))

    cursor.execute('''
        INSERT INTO candidates (
            job_id, candidate_name, filename, resume_text,
            skill_score, experience_score, education_score, tfidf_score, final_score,
            rank_order, matched_skills, missing_skills, extracted_experience, extracted_education
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        job_id,
        candidate_data['candidate_name'],
        candidate_data['filename'],
        candidate_data.get('resume_text', ''),
        candidate_data['skill_score'],
        candidate_data['experience_score'],
        candidate_data['education_score'],
        candidate_data['tfidf_score'],
        candidate_data['final_score'],
        candidate_data.get('rank', 0),
        matched_json,
        missing_json,
        candidate_data.get('extracted_experience', 0),
        candidate_data.get('extracted_education', '')
    ))

    cand_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cand_id

def get_job_by_id(job_id):
    """Retrieve job details by job_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
    job = cursor.fetchone()
    conn.close()
    return dict(job) if job else None

def get_candidates_by_job_id(job_id):
    """Retrieve all candidates for a specific job, ordered by final_score descending."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM candidates 
        WHERE job_id = ? 
        ORDER BY final_score DESC
    ''', (job_id,))
    rows = cursor.fetchall()
    conn.close()

    candidates = []
    for r in rows:
        c = dict(r)
        c['matched_skills'] = json.loads(c['matched_skills']) if c['matched_skills'] else []
        c['missing_skills'] = json.loads(c['missing_skills']) if c['missing_skills'] else []
        candidates.append(c)

    return candidates

def get_candidate_by_id(candidate_id):
    """Retrieve single candidate analysis details by candidate_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM candidates WHERE id = ?', (candidate_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    c = dict(row)
    c['matched_skills'] = json.loads(c['matched_skills']) if c['matched_skills'] else []
    c['missing_skills'] = json.loads(c['missing_skills']) if c['missing_skills'] else []
    return c
