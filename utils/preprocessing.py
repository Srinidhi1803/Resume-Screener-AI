import re
import spacy

# Map special tech terms to safe alpha tokens during tokenization/lemmatization
PROTECTED_TERMS = {
    'c++': 'cplusplus',
    'c#': 'csharp',
    '.net': 'dotnet',
    'asp.net': 'aspdotnet',
    'node.js': 'nodejs',
    'react.js': 'reactjs',
    'vue.js': 'vuejs',
    'next.js': 'nextjs',
    'express.js': 'expressjs',
    'd3.js': 'd3js',
    'three.js': 'threejs',
    'b.tech': 'btech',
    'm.tech': 'mtech',
    'b.e.': 'be',
    'm.e.': 'me',
    'b.sc': 'bsc',
    'm.sc': 'msc',
    'ph.d': 'phd',
    'ci/cd': 'cicd',
    'rest api': 'restapi',
    'restful api': 'restfulapi',
}

REVERSE_PROTECTED_TERMS = {v: k for k, v in PROTECTED_TERMS.items()}

# Global nlp object lazy loaded
_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load('en_core_web_sm')
        except Exception:
            try:
                import spacy.cli
                spacy.cli.download('en_core_web_sm')
                _nlp = spacy.load('en_core_web_sm')
            except Exception as e:
                print(f"Warning: Could not load or download spacy en_core_web_sm: {e}. Using blank English model.")
                _nlp = spacy.blank('en')
    return _nlp

def preprocess_text(text):
    """
    Preprocess raw text using spaCy:
    - Lowercasing
    - Preserving technical terms (C++, C#, .NET, Node.js, B.Tech, etc.)
    - Tokenization
    - Stopword removal
    - Punctuation removal
    - Lemmatization
    Returns clean tokenized string for TF-IDF and NLP analysis.
    """
    if not text:
        return ""

    lowered = text.lower()

    # Protect technical terms with safe substitutes
    for term, safe in PROTECTED_TERMS.items():
        # Replace occurrences using regex boundary or string replace
        pattern = re.escape(term)
        lowered = re.sub(pattern, f" {safe} ", lowered)

    nlp = get_nlp()
    doc = nlp(lowered)

    cleaned_tokens = []
    for token in doc:
        # Ignore stopwords, punctuation, whitespace, and numbers-only tokens
        if token.is_stop or token.is_punct or token.is_space:
            continue
        
        lemma = token.lemma_.strip()
        
        # Restore protected terms if needed or keep cleaned alpha token
        if lemma in REVERSE_PROTECTED_TERMS:
            cleaned_tokens.append(REVERSE_PROTECTED_TERMS[lemma])
        elif len(lemma) > 1 and re.match(r'^[a-zA-Z0-9\+\#\.\_\-]+$', lemma):
            cleaned_tokens.append(lemma)

    return " ".join(cleaned_tokens)
