import re

# Comprehensive Degree List and Canonical Categorization
DEGREE_PATTERNS = {
    'phd': ('Doctorate', ['phd', 'ph.d', 'doctor of philosophy', 'doctorate']),
    'mtech': ('Master of Technology', ['m.tech', 'mtech', 'master of technology']),
    'me': ('Master of Engineering', ['m.e.', 'me', 'master of engineering']),
    'msc': ('Master of Science', ['m.sc', 'msc', 'master of science', 'ms', 'm.s.']),
    'mca': ('Master of Computer Applications', ['mca', 'master of computer applications', 'master of computer application']),
    'mba': ('Master of Business Administration', ['mba', 'master of business administration']),
    'btech': ('Bachelor of Technology', ['b.tech', 'btech', 'bachelor of technology']),
    'be': ('Bachelor of Engineering', ['b.e.', 'be', 'bachelor of engineering']),
    'bsc': ('Bachelor of Science', ['b.sc', 'bsc', 'bachelor of science', 'bs', 'b.s.']),
    'bca': ('Bachelor of Computer Applications', ['bca', 'bachelor of computer applications', 'bachelor of computer application']),
    'ba': ('Bachelor of Arts', ['b.a.', 'ba', 'bachelor of arts']),
    'bcom': ('Bachelor of Commerce', ['b.com', 'bcom', 'bachelor of commerce']),
    'diploma': ('Diploma', ['diploma', 'polytechnic'])
}

# Degree Equivalence Groups
EQUIVALENT_GROUPS = [
    {'btech', 'be', 'bca', 'bsc'},         # Tech/CS Bachelor equivalents
    {'mtech', 'me', 'mca', 'msc', 'phd'},  # Tech Master/Advanced equivalents
    {'mba', 'msc', 'mca', 'mtech', 'me'},   # Postgraduate equivalents
]

# Field relevance (CS/Engineering degrees vs General)
TECH_DEGREES = {'btech', 'be', 'bca', 'mca', 'mtech', 'me', 'bsc', 'msc', 'phd'}

def extract_education(text):
    """
    Detect degrees present in resume text.
    Returns:
    - degrees_found (list of canonical strings, e.g. ['Bachelor of Technology'])
    - highest_degree_key (str key like 'btech')
    """
    if not text:
        return [], "none"

    found_keys = []
    text_lower = text.lower()

    for key, (canonical, aliases) in DEGREE_PATTERNS.items():
        for alias in aliases:
            escaped = re.escape(alias)
            # Boundary pattern matching
            pattern = r'(?:^|[\s,.\(\)\[\]/:\-])' + escaped + r'(?:$|[\s,.\(\)\[\]/:\-])'
            if re.search(pattern, text_lower):
                if key not in found_keys:
                    found_keys.append(key)
                break

    if not found_keys:
        return ["No Degree Detected"], "none"

    # Hierarchy priority
    hierarchy = ['phd', 'mtech', 'me', 'mca', 'msc', 'mba', 'btech', 'be', 'bsc', 'bca', 'bcom', 'ba', 'diploma']
    highest = "none"
    for rank_key in hierarchy:
        if rank_key in found_keys:
            highest = rank_key
            break

    canonical_names = [DEGREE_PATTERNS[k][0] for k in found_keys]
    return canonical_names, highest

def evaluate_education_score(required_education_str, resume_text):
    """
    Evaluate Education Score (0 to 100) based on requirements:
    - Exact or equivalent match = 100
    - Related degree = 75
    - Unrelated detected degree = 40
    - No degree detected = 0
    """
    if not required_education_str or required_education_str.lower().strip() in ['any', 'none', 'not specified', '']:
        return 100.0, "Any degree acceptable"

    req_text = required_education_str.lower()
    
    # Identify required degree key
    req_key = None
    for key, (canonical, aliases) in DEGREE_PATTERNS.items():
        for alias in aliases:
            if alias in req_text:
                req_key = key
                break
        if req_key:
            break

    cand_degrees, cand_highest_key = extract_education(resume_text)

    if cand_highest_key == "none":
        return 0.0, "No degree detected in resume"

    # If required degree couldn't be parsed specifically from requirement string
    if not req_key:
        # Check if candidate has any tech/recognized degree
        if cand_highest_key in TECH_DEGREES:
            return 100.0, f"Detected: {', '.join(cand_degrees)}"
        else:
            return 75.0, f"Detected: {', '.join(cand_degrees)}"

    # Check 1: Exact match
    if req_key in [k for k in DEGREE_PATTERNS if DEGREE_PATTERNS[k][0] in cand_degrees]:
        return 100.0, f"Exact Match ({DEGREE_PATTERNS[req_key][0]})"

    # Check 2: Equivalent group match
    for group in EQUIVALENT_GROUPS:
        if req_key in group and cand_highest_key in group:
            return 100.0, f"Equivalent Degree ({DEGREE_PATTERNS[cand_highest_key][0]} for {DEGREE_PATTERNS[req_key][0]})"

    # Check 3: Candidate has higher level tech degree than required (e.g., M.Tech when B.Tech required)
    if req_key in ['btech', 'be', 'bca', 'bsc'] and cand_highest_key in ['mtech', 'me', 'mca', 'msc', 'phd']:
        return 100.0, f"Higher Qualification ({DEGREE_PATTERNS[cand_highest_key][0]})"

    # Check 4: Related degree (e.g. both are tech/engineering)
    if req_key in TECH_DEGREES and cand_highest_key in TECH_DEGREES:
        return 75.0, f"Related Degree ({DEGREE_PATTERNS[cand_highest_key][0]})"

    # Check 5: Unrelated degree detected
    return 40.0, f"Unrelated Degree ({DEGREE_PATTERNS[cand_highest_key][0]})"
