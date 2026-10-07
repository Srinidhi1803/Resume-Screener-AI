import re

def extract_experience(text):
    """
    Extract total work experience in years from resume text using regex patterns.
    
    Checks:
    1. Explicit phrases: "5+ years of experience", "3 yrs experience", "Experience: 4 years"
    2. Date ranges: "2019 - 2023", "Jan 2020 - Present", "2018 to 2022"
    3. Maximum reasonable value found in resume.
    """
    if not text:
        return 0.0

    years_found = []

    # Pattern 1: Explicit years of experience mentions
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:\+|\s*plus)?\s*(?:years?|yrs?)(?:\s*of)?\s*(?:work|relevant|total|professional)?\s*(?:experience|exp)',
        r'(?:experience|exp)\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\s*(?:\+|\s*plus)?\s*(?:years?|yrs?)',
        r'(\d+(?:\.\d+)?)\s*(?:\+|\s*plus)?\s*(?:years?|yrs?)\s*(?:in|as|with|of)'
    ]

    for pat in patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        for m in matches:
            try:
                val = float(m)
                if 0.5 <= val <= 40:  # Reasonable range for years of experience
                    years_found.append(val)
            except ValueError:
                continue

    # Pattern 2: Calculate experience from date ranges (e.g., 2018 - 2023, 2020 - Present)
    # Match years like 199X or 20XX
    date_range_pat = r'\b(19\d\d|20\d\d)\s*(?:-|–|to|until)\s*(19\d\d|20\d\d|present|current|now)\b'
    date_matches = re.findall(date_range_pat, text, re.IGNORECASE)

    current_year = 2026
    total_range_years = 0.0

    for start_str, end_str in date_matches:
        try:
            start_yr = int(start_str)
            if end_str.lower() in ['present', 'current', 'now']:
                end_yr = current_year
            else:
                end_yr = int(end_str)

            if end_yr >= start_yr and 1980 <= start_yr <= current_year:
                diff = end_yr - start_yr
                if diff == 0:
                    diff = 0.5  # Less than a year
                total_range_years += diff
        except ValueError:
            continue

    if total_range_years > 0:
        years_found.append(total_range_years)

    if years_found:
        # Return the maximum realistic experience value found
        return round(max(years_found), 1)

    return 0.0

def calculate_experience_score(candidate_exp, required_exp):
    """
    Calculate Experience Match Score %.
    
    Formula:
    Score = (Candidate Experience / Required Experience) * 100
    Capped at 100%.
    If Required Experience == 0, returns 100%.
    """
    try:
        req = float(required_exp)
    except (ValueError, TypeError):
        req = 0.0

    try:
        cand = float(candidate_exp)
    except (ValueError, TypeError):
        cand = 0.0

    if req <= 0:
        return 100.0

    if cand <= 0:
        return 0.0

    score = (cand / req) * 100.0
    return round(min(100.0, score), 2)
