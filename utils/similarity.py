from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.preprocessing import preprocess_text

def compute_tfidf_similarity(jd_raw_text, resume_raw_text):
    """
    Computes TF-IDF vector representations of the Job Description and Candidate Resume
    and calculates cosine similarity score between 0.0 and 100.0.
    """
    if not jd_raw_text or not resume_raw_text:
        return 0.0

    # Clean and preprocess both texts
    jd_clean = preprocess_text(jd_raw_text)
    resume_clean = preprocess_text(resume_raw_text)

    if not jd_clean.strip() or not resume_clean.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),  # capture unigrams & bigrams
            stop_words='english',
            min_df=1
        )
        
        # Fit and transform JD and resume
        tfidf_matrix = vectorizer.fit_transform([jd_clean, resume_clean])
        
        # Cosine similarity matrix shape (2, 2)
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        
        sim_score = float(similarity_matrix[0][0]) * 100.0
        return round(min(100.0, max(0.0, sim_score)), 2)
    except Exception as e:
        print(f"Error computing TF-IDF similarity: {e}")
        return 0.0
