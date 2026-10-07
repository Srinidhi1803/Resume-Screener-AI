def calculate_final_score(skill_score, tfidf_score, exp_score, edu_score):
    """
    Weighted scoring formula:
    Final Score = 0.40 * Skill Match + 0.25 * TF-IDF Similarity + 0.20 * Experience Match + 0.15 * Education Match
    
    All input scores are on a 0-100 scale.
    Returns final score rounded to 2 decimal places.
    """
    w_skill = 0.40
    w_tfidf = 0.25
    w_exp   = 0.20
    w_edu   = 0.15

    final = (
        (w_skill * float(skill_score)) +
        (w_tfidf * float(tfidf_score)) +
        (w_exp   * float(exp_score)) +
        (w_edu   * float(edu_score))
    )

    return round(min(100.0, max(0.0, final)), 2)

def rank_candidates(candidate_list):
    """
    Takes a list of candidate dictionaries containing 'final_score',
    sorts descending by final_score, and updates their 'rank' field (1, 2, 3...).
    """
    sorted_candidates = sorted(candidate_list, key=lambda c: c['final_score'], reverse=True)
    
    for idx, candidate in enumerate(sorted_candidates, start=1):
        candidate['rank'] = idx

    return sorted_candidates
