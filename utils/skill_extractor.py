import re

# Comprehensive skill taxonomy with aliases/canonical names
SKILL_DICTIONARY = {
    # Programming Languages
    'python': 'Python',
    'java': 'Java',
    'c': 'C',
    'c++': 'C++',
    'cpp': 'C++',
    'c#': 'C#',
    'csharp': 'C#',
    'javascript': 'JavaScript',
    'js': 'JavaScript',
    'typescript': 'TypeScript',
    'ts': 'TypeScript',
    'go': 'Go',
    'golang': 'Go',
    'rust': 'Rust',
    'ruby': 'Ruby',
    'php': 'PHP',
    'swift': 'Swift',
    'kotlin': 'Kotlin',
    'r': 'R',
    'scala': 'Scala',
    'sql': 'SQL',
    'html': 'HTML',
    'html5': 'HTML',
    'css': 'CSS',
    'css3': 'CSS',
    'bash': 'Bash',
    'shell': 'Shell',
    'powershell': 'PowerShell',

    # Frameworks & Web Development
    'react': 'React',
    'react.js': 'React',
    'reactjs': 'React',
    'angular': 'Angular',
    'angularjs': 'Angular',
    'vue': 'Vue',
    'vue.js': 'Vue',
    'vuejs': 'Vue',
    'node.js': 'Node.js',
    'nodejs': 'Node.js',
    'node': 'Node.js',
    'express': 'Express.js',
    'express.js': 'Express.js',
    'expressjs': 'Express.js',
    'flask': 'Flask',
    'django': 'Django',
    'fastapi': 'FastAPI',
    'spring boot': 'Spring Boot',
    'springboot': 'Spring Boot',
    'spring': 'Spring Boot',
    'asp.net': '.NET',
    '.net': '.NET',
    'dotnet': '.NET',
    'bootstrap': 'Bootstrap',
    'tailwind': 'Tailwind CSS',
    'tailwindcss': 'Tailwind CSS',
    'jquery': 'jQuery',

    # Data Science & AI/ML
    'pandas': 'Pandas',
    'numpy': 'NumPy',
    'scikit-learn': 'Scikit-learn',
    'sklearn': 'Scikit-learn',
    'tensorflow': 'TensorFlow',
    'pytorch': 'PyTorch',
    'keras': 'Keras',
    'opencv': 'OpenCV',
    'nltk': 'NLTK',
    'spacy': 'spaCy',
    'hugging face': 'Hugging Face',
    'huggingface': 'Hugging Face',
    'pyspark': 'PySpark',
    'spark': 'Apache Spark',
    'machine learning': 'Machine Learning',
    'ml': 'Machine Learning',
    'deep learning': 'Deep Learning',
    'dl': 'Deep Learning',
    'artificial intelligence': 'Artificial Intelligence',
    'ai': 'Artificial Intelligence',
    'nlp': 'NLP',
    'natural language processing': 'NLP',
    'computer vision': 'Computer Vision',
    'cv': 'Computer Vision',
    'data science': 'Data Science',
    'data engineering': 'Data Engineering',
    'data analysis': 'Data Analysis',

    # Databases & Storage
    'sql': 'SQL',
    'mysql': 'MySQL',
    'postgresql': 'PostgreSQL',
    'postgres': 'PostgreSQL',
    'sqlite': 'SQLite',
    'mongodb': 'MongoDB',
    'mongo': 'MongoDB',
    'redis': 'Redis',
    'cassandra': 'Cassandra',
    'oracle': 'Oracle',
    'dynamodb': 'DynamoDB',
    'firebase': 'Firebase',

    # Cloud & DevOps
    'aws': 'AWS',
    'amazon web services': 'AWS',
    'azure': 'Azure',
    'microsoft azure': 'Azure',
    'gcp': 'GCP',
    'google cloud': 'GCP',
    'google cloud platform': 'GCP',
    'docker': 'Docker',
    'kubernetes': 'Kubernetes',
    'k8s': 'Kubernetes',
    'git': 'Git',
    'github': 'GitHub',
    'gitlab': 'GitLab',
    'jenkins': 'Jenkins',
    'terraform': 'Terraform',
    'ansible': 'Ansible',
    'linux': 'Linux',
    'unix': 'Unix',
    'ci/cd': 'CI/CD',
    'cicd': 'CI/CD',
    'nginx': 'Nginx',
    'rest api': 'REST API',
    'rest apis': 'REST API',
    'restful api': 'REST API',
    'graphql': 'GraphQL',
    'microservices': 'Microservices',
    'agile': 'Agile',
    'scrum': 'Scrum',
    'jira': 'Jira'
}

def extract_skills_from_text(text):
    """
    Extract skills present in raw text using regex pattern matching against dictionary.
    Returns a set of canonical skill names (e.g. {'Python', 'Flask', 'SQL'}).
    """
    if not text:
        return set()

    found_skills = set()
    text_lower = text.lower()

    # Sort dictionary keys by length descending to match longer skills first (e.g., 'spring boot' before 'spring')
    sorted_keys = sorted(SKILL_DICTIONARY.keys(), key=lambda x: len(x), reverse=True)

    for skill_key in sorted_keys:
        canonical = SKILL_DICTIONARY[skill_key]

        # Use regex boundary matching
        # Special symbols like +, #, . require escaping or special regex
        escaped_key = re.escape(skill_key)
        
        # Word boundary pattern: check surrounded by spaces, punctuation, or string start/end
        pattern = r'(?:^|[\s,.\(\)\[\]/:\-])' + escaped_key + r'(?:$|[\s,.\(\)\[\]/:\-])'

        if re.search(pattern, text_lower):
            found_skills.add(canonical)

    return found_skills

def parse_user_required_skills(skills_input_string):
    """
    Parse comma-separated or space-separated skills entered manually by user in form.
    Returns a set of canonical or cleaned skill names.
    """
    if not skills_input_string:
        return set()

    skills = set()
    raw_tokens = [s.strip() for s in re.split(r'[,;\n]', skills_input_string) if s.strip()]

    for token in raw_tokens:
        tok_lower = token.lower()
        if tok_lower in SKILL_DICTIONARY:
            skills.add(SKILL_DICTIONARY[tok_lower])
        else:
            # Also attempt extracting skills from the token string
            extracted = extract_skills_from_text(token)
            if extracted:
                skills.update(extracted)
            else:
                # Custom skill typed by user
                skills.add(token.strip().title())

    return skills

def match_skills(required_skills_set, resume_skills_set):
    """
    Match candidate resume skills against required JD skills.
    
    Formula:
    Skill Score = (Matched Skills Count / Total Required Skills) * 100
    
    Returns:
    - skill_score (float rounded to 2 decimals, 0-100)
    - matched_skills (list of str)
    - missing_skills (list of str)
    """
    if not required_skills_set:
        return 100.0, list(resume_skills_set), []

    # Case-insensitive comparison mapping
    req_map = {s.lower(): s for s in required_skills_set}
    res_map = {s.lower(): s for s in resume_skills_set}

    matched = []
    missing = []

    for req_lower, req_orig in req_map.items():
        if req_lower in res_map:
            matched.append(req_orig)
        else:
            missing.append(req_orig)

    score = (len(matched) / len(required_skills_set)) * 100.0
    return round(min(100.0, max(0.0, score)), 2), sorted(matched), sorted(missing)
