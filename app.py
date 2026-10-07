import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

from database import (
    init_db, save_job, save_candidate, 
    get_job_by_id, get_candidates_by_job_id, get_candidate_by_id
)
from utils.parser import parse_resume, extract_candidate_name
from utils.skill_extractor import extract_skills_from_text, parse_user_required_skills, match_skills
from utils.experience_extractor import extract_experience, calculate_experience_score
from utils.education_extractor import evaluate_education_score, extract_education
from utils.similarity import compute_tfidf_similarity
from utils.scoring import calculate_final_score, rank_candidates

app = Flask(__name__)
app.secret_key = "nlp_resume_screening_secret_key_2026"

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize DB tables at startup
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """PAGE 1: Home Page"""
    return render_template('index.html')

@app.route('/screening', methods=['GET', 'POST'])
def screening():
    """PAGE 2: Resume Screening Page"""
    if request.method == 'GET':
        return render_template('screening.html')

    # Handle POST submission
    try:
        job_title = request.form.get('job_title', 'Job Position').strip()
        job_description = request.form.get('job_description', '').strip()
        
        min_exp_str = request.form.get('min_experience', '0').strip()
        try:
            min_experience = float(min_exp_str)
        except ValueError:
            min_experience = 0.0

        required_education = request.form.get('required_education', '').strip()
        required_skills_raw = request.form.get('required_skills', '').strip()

        uploaded_files = request.files.getlist('resumes')

        if not job_description:
            flash("Please provide a Job Description.", "error")
            return redirect(request.url)

        if not uploaded_files or uploaded_files[0].filename == '':
            flash("Please upload at least one candidate resume.", "error")
            return redirect(request.url)

        # Determine required skills set: user input takes priority, supplemented by JD extractions
        user_skills = parse_user_required_skills(required_skills_raw)
        jd_extracted_skills = extract_skills_from_text(job_description)
        
        if user_skills:
            required_skills_set = user_skills
        else:
            required_skills_set = jd_extracted_skills

        required_skills_str = ", ".join(sorted(required_skills_set))

        # Save Job record in database
        job_id = save_job(
            job_title=job_title,
            job_description=job_description,
            min_experience=min_experience,
            required_education=required_education,
            required_skills=required_skills_str
        )

        candidate_results = []

        # Process each uploaded resume
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                safe_fn = secure_filename(file.filename)
                saved_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{safe_fn}")
                file.save(saved_path)

                # 1. Resume Text Extraction
                resume_text = parse_resume(saved_path)
                cand_name = extract_candidate_name(resume_text, safe_fn)

                # 2. Skill Extraction & Matching
                cand_skills = extract_skills_from_text(resume_text)
                skill_score, matched_skills, missing_skills = match_skills(required_skills_set, cand_skills)

                # 3. Experience Extraction & Matching
                cand_exp = extract_experience(resume_text)
                exp_score = calculate_experience_score(cand_exp, min_experience)

                # 4. Education Extraction & Matching
                edu_score, cand_edu_desc = evaluate_education_score(required_education, resume_text)

                # 5. TF-IDF + Cosine Similarity
                tfidf_score = compute_tfidf_similarity(job_description, resume_text)

                # 6. Weighted Final Score
                final_score = calculate_final_score(skill_score, tfidf_score, exp_score, edu_score)

                candidate_results.append({
                    'candidate_name': cand_name,
                    'filename': safe_fn,
                    'resume_text': resume_text,
                    'skill_score': skill_score,
                    'experience_score': exp_score,
                    'education_score': edu_score,
                    'tfidf_score': tfidf_score,
                    'final_score': final_score,
                    'matched_skills': matched_skills,
                    'missing_skills': missing_skills,
                    'extracted_experience': cand_exp,
                    'extracted_education': cand_edu_desc
                })

        if not candidate_results:
            flash("No valid resumes could be processed. Supported formats: PDF, DOCX, TXT.", "error")
            return redirect(request.url)

        # 7. Rank candidates descending by Final Score
        ranked_list = rank_candidates(candidate_results)

        # 8. Save candidates into database
        for c in ranked_list:
            save_candidate(job_id, c)

        return redirect(url_for('results', job_id=job_id))

    except Exception as e:
        print(f"Error in processing screening: {e}")
        flash(f"An unexpected error occurred during processing: {str(e)}", "error")
        return redirect(request.url)

@app.route('/results/<int:job_id>')
def results(job_id):
    """PAGE 3: Results Dashboard"""
    job = get_job_by_id(job_id)
    if not job:
        flash("Job screening record not found.", "error")
        return redirect(url_for('index'))

    candidates = get_candidates_by_job_id(job_id)
    
    # Calculate summary metrics
    total_candidates = len(candidates)
    top_candidate = candidates[0]['candidate_name'] if candidates else "N/A"
    avg_score = round(sum(c['final_score'] for c in candidates) / total_candidates, 2) if total_candidates > 0 else 0.0

    return render_template(
        'results.html',
        job=job,
        candidates=candidates,
        total_candidates=total_candidates,
        top_candidate=top_candidate,
        avg_score=avg_score
    )

@app.route('/candidate/<int:candidate_id>')
def candidate(candidate_id):
    """PAGE 4: Candidate Detailed Analysis Page"""
    cand = get_candidate_by_id(candidate_id)
    if not cand:
        flash("Candidate analysis record not found.", "error")
        return redirect(url_for('index'))

    job = get_job_by_id(cand['job_id'])

    return render_template('candidate.html', candidate=cand, job=job)

@app.route('/resume/<int:candidate_id>')
def view_resume(candidate_id):
    """View extracted resume raw text."""
    cand = get_candidate_by_id(candidate_id)
    if not cand:
        return "Resume not found", 404
    return f"<pre style='font-family: monospace; padding: 20px; white-space: pre-wrap;'>{cand.get('resume_text', 'No text content available.')}</pre>"

@app.route('/demo')
def run_demo():
    """Quick single-click Demo route: loads sample JD & 10 sample resumes, runs screening."""
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_data')
    jd_path = os.path.join(sample_dir, 'sample_job_description.txt')
    resumes_dir = os.path.join(sample_dir, 'sample_resumes')

    if not os.path.exists(jd_path) or not os.path.exists(resumes_dir):
        flash("Sample dataset files not found.", "error")
        return redirect(url_for('screening'))

    with open(jd_path, 'r', encoding='utf-8') as f:
        job_description = f.read()

    job_title = "Senior NLP & Full Stack Python Engineer"
    min_experience = 3.0
    required_education = "B.Tech / B.E. / M.Tech"
    required_skills_raw = "Python, NLP, spaCy, Flask, SQL, Machine Learning, Scikit-learn, AWS, Docker, Git, REST API"

    required_skills_set = parse_user_required_skills(required_skills_raw)
    required_skills_str = ", ".join(sorted(required_skills_set))

    job_id = save_job(
        job_title=job_title,
        job_description=job_description,
        min_experience=min_experience,
        required_education=required_education,
        required_skills=required_skills_str
    )

    candidate_results = []
    resume_files = os.listdir(resumes_dir)

    for fn in resume_files:
        file_path = os.path.join(resumes_dir, fn)
        if os.path.isfile(file_path):
            resume_text = parse_resume(file_path)
            cand_name = extract_candidate_name(resume_text, fn)

            cand_skills = extract_skills_from_text(resume_text)
            skill_score, matched_skills, missing_skills = match_skills(required_skills_set, cand_skills)

            cand_exp = extract_experience(resume_text)
            exp_score = calculate_experience_score(cand_exp, min_experience)

            edu_score, cand_edu_desc = evaluate_education_score(required_education, resume_text)

            tfidf_score = compute_tfidf_similarity(job_description, resume_text)

            final_score = calculate_final_score(skill_score, tfidf_score, exp_score, edu_score)

            candidate_results.append({
                'candidate_name': cand_name,
                'filename': fn,
                'resume_text': resume_text,
                'skill_score': skill_score,
                'experience_score': exp_score,
                'education_score': edu_score,
                'tfidf_score': tfidf_score,
                'final_score': final_score,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'extracted_experience': cand_exp,
                'extracted_education': cand_edu_desc
            })

    ranked_list = rank_candidates(candidate_results)
    for c in ranked_list:
        save_candidate(job_id, c)

    flash("Sample demo dataset loaded and processed successfully!", "success")
    return redirect(url_for('results', job_id=job_id))

if __name__ == '__main__':
    print("Starting NLP Resume Screening Web Application...")
    app.run(debug=True, port=5000)
