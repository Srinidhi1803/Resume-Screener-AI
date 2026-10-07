# NLP-Based Intelligent Resume Screening and Candidate Ranking System

An intelligent, full-stack Natural Language Processing (NLP) and Information Retrieval (IR) application built for automated resume screening, feature extraction, weighted match scoring, and candidate ranking.

---

## 1. Project Objective
The objective of this project is to automate the recruitment screening process by evaluating multiple candidate resumes against a target Job Description (JD). Using NLP techniques (spaCy, tokenization, lemmatization), Information Retrieval models (TF-IDF Vectorization, Cosine Similarity), and rule-based feature extractors (Skills, Experience, Education), the system produces an objective, explainable score (0–100%) and ranks candidates from highest fit to lowest.

---

## 2. System Architecture

```
                      Job Description
                             │
                     Text Preprocessing (spaCy)
                             │
                   JD Feature Extraction
                             │
     ┌───────────────────────┼───────────────────────┐
     ▼                       ▼                       ▼
Required Skills     Min Experience          Required Education
     │                       │                       │
     └───────────────────────┼───────────────────────┘
                             │
                    Candidate Resumes (PDF / DOCX / TXT)
                             │
                    Text Parser (PyMuPDF / python-docx)
                             │
                     Text Preprocessing (spaCy)
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
      Feature Extraction        TF-IDF Vector Space
   (Skills/Exp/Education)               │
                │                         │
                └────────────┬────────────┘
                             ▼
                    Feature Matching Engine
                             │
     ┌───────────────────────┼───────────────────────┬───────────────────────┐
     ▼                       ▼                       ▼                       ▼
Skill Match Score     Experience Score       Education Score         TF-IDF Cosine Score
  (Weight: 40%)        (Weight: 20%)          (Weight: 15%)            (Weight: 25%)
     └───────────────────────┼───────────────────────┴───────────────────────┘
                             ▼
                   Weighted Scoring Engine
                             │
                   Final Candidate Score (%)
                             │
                    Candidate Ranking (1..N)
                             │
                SQLite DB ───┴─── Web Dashboard
```

---

## 3. Tech Stack

- **Frontend**: HTML5, CSS3 (Vanilla CSS with CSS variables, Glassmorphism, Responsive Grid), JavaScript, Chart.js for data visualization.
- **Backend**: Python Flask web server.
- **NLP & Processing**: `spaCy` (`en_core_web_sm`), `scikit-learn` (`TfidfVectorizer`, `cosine_similarity`), `pandas`.
- **Resume Parsers**: `PyMuPDF` (`fitz`) for PDF files, `python-docx` for Word DOCX files.
- **Database**: SQLite (`database.db`).

---

## 4. How TF-IDF Works in This Project
**TF-IDF (Term Frequency - Inverse Document Frequency)** measures how important a word or bigram (2-word combination) is within the corpus consisting of the Job Description and Candidate Resume.

1. **Term Frequency (TF)**: Calculates how frequently a token appears in a document.
2. **Inverse Document Frequency (IDF)**: Down-weights common general words across documents while boosting domain-specific technical terms.
3. In this project, `TfidfVectorizer(ngram_range=(1,2), stop_words='english')` converts both preprocessed texts into high-dimensional numerical feature vectors.

---

## 5. Why Cosine Similarity is Used
**Cosine Similarity** calculates the cosine of the angle between the Job Description vector ($\vec{A}$) and the Candidate Resume vector ($\vec{B}$):

$$\text{Cosine Similarity} = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|}$$

- **Length Independence**: Unlike Euclidean distance, Cosine Similarity evaluates directional similarity regardless of resume length (preventing long resumes from getting artificially higher scores simply due to word volume).
- Returns a score between `0.0` and `1.0`, converted to percentage `0–100%`.

---

## 6. How Skills Are Extracted
1. A taxonomy dictionary categorizes over 80+ technical skills (Programming Languages, Web Frameworks, AI/ML libraries, Cloud/DevOps tools, Databases).
2. The extractor uses regex boundary patterns to detect exact skills in both the Job Description and Resume.
3. Special technical terms containing symbols (`C++`, `C#`, `.NET`, `Node.js`, `REST API`, `B.Tech`) are protected during spaCy preprocessing so punctuation removal does not alter them.
4. **Skill Match Score Formula**:

$$\text{Skill Score} = \left(\frac{\text{Matched Required Skills Count}}{\text{Total Required Skills Count}}\right) \times 100$$

---

## 7. How Experience is Scored
1. Regex patterns scan resume text for explicit experience statements (e.g., `"5+ years of experience"`, `"3 yrs exp"`) and date ranges (e.g., `"2019 - 2023"`, `"Jan 2021 - Present"`).
2. The maximum valid experience in years is extracted.
3. **Experience Match Score Formula**:

$$\text{Experience Score} = \min\left(100, \frac{\text{Candidate Experience}}{\text{Required Experience}} \times 100\right)$$

- If Candidate has 2 years and Required is 3 years: $\frac{2}{3} \times 100 = 66.67\%$.
- If Candidate has 5 years and Required is 3 years: Capped at $100\%$.
- If Required is 0, defaults to $100\%$.

---

## 8. How Education is Scored
1. Recognizes degrees: Doctorate (`Ph.D`), Master's (`M.Tech`, `M.E.`, `MSc`, `MCA`, `MBA`), Bachelor's (`B.Tech`, `B.E.`, `BSc`, `BCA`), and `Diploma`.
2. **Equivalence & Matching Matrix**:
   - Exact or Equivalent Degree Match (e.g. B.Tech $\equiv$ B.E., MCA $\equiv$ MSc CS): **100%**
   - Higher Level Tech Degree than required: **100%**
   - Related Tech Degree: **75%**
   - Unrelated Detected Degree: **40%**
   - No Degree Detected: **0%**

---

## 9. Final Weighted Scoring Formula

$$\text{Final Score} = (0.40 \times \text{Skill Match}) + (0.25 \times \text{TF-IDF Similarity}) + (0.20 \times \text{Experience Match}) + (0.15 \times \text{Education Match})$$

All scores are rounded to 2 decimal places. Candidates are sorted descending by Final Score and assigned numerical ranks ($1, 2, 3, \dots$).

---

## 10. Folder Structure

```
resume_screening/
│
├── app.py                     # Main Flask web application & routes
├── database.py                # SQLite database setup & CRUD functions
├── requirements.txt           # Project dependencies
├── README.md                  # Comprehensive project documentation
│
├── static/
│   ├── css/
│   │   └── style.css          # Recruiter dashboard theme & responsive styles
│   └── js/
│       └── script.js          # Client-side file drag-and-drop & animations
│
├── templates/
│   ├── index.html             # PAGE 1: Home Page
│   ├── screening.html         # PAGE 2: Resume Screening Form Page
│   ├── results.html           # PAGE 3: Results Dashboard & Candidate Ranking
│   └── candidate.html         # PAGE 4: Candidate Detailed Analysis Page
│
├── utils/
│   ├── __init__.py            # Utils package init
│   ├── parser.py              # Resume text extraction (PDF, DOCX, TXT)
│   ├── preprocessing.py       # spaCy NLP preprocessing & protected term handler
│   ├── skill_extractor.py     # Skill taxonomy matching & scoring
│   ├── experience_extractor.py# Regex & date range experience extraction
│   ├── education_extractor.py # Degree parsing & equivalence scoring
│   ├── similarity.py          # TF-IDF Vectorizer & Cosine Similarity
│   └── scoring.py             # Weighted final score aggregator & ranking
│
├── uploads/                   # Uploaded candidate resumes storage
└── sample_data/               # Pre-populated test dataset
    ├── sample_job_description.txt
    └── sample_resumes/        # 10 sample candidate resumes (.txt)
```

---

## 11. Installation & Running Instructions

### Step 1: Install Dependencies
Open terminal/cmd in the project root directory and run:
```bash
pip install -r requirements.txt
```

### Step 2: Download spaCy Language Model
```bash
python -m spacy download en_core_web_sm
```

### Step 3: Launch Flask Application
```bash
python app.py
```

### Step 4: Open in Web Browser
Navigate to:
```
http://127.0.0.1:5000
```

---

## 12. Sample Input / Output Demonstration

### Sample Job Description:
- **Title**: Senior NLP & Full Stack Python Engineer
- **Required Skills**: Python, NLP, spaCy, Flask, SQL, Machine Learning, Scikit-learn, AWS, Docker, Git, REST API
- **Required Experience**: 3 Years
- **Required Education**: B.Tech / B.E. / M.Tech / MCA

### Ranked Output Example:

| Rank | Candidate Name | Skills Match | Experience Match | Education Match | TF-IDF Similarity | Final Score |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **1** | **Rahul Sharma** | 91.67% | 100.00% | 100.00% | 84.12% | **92.70%** |
| **2** | **Priya Patel** | 83.33% | 100.00% | 100.00% | 81.05% | **88.59%** |
| **3** | **Kavita Rao** | 75.00% | 100.00% | 100.00% | 72.40% | **83.10%** |
| **4** | **Anjali Gupta** | 58.33% | 100.00% | 100.00% | 61.20% | **73.63%** |
| **5** | **Vikram Singh** | 50.00% | 100.00% | 100.00% | 48.50% | **67.13%** |
| **6** | **Neha Reddi** | 50.00% | 100.00% | 100.00% | 45.10% | **66.28%** |
| **7** | **Amit Kumar** | 41.67% | 66.67% | 75.00% | 38.20% | **50.80%** |
| **8** | **Sanya Verma** | 33.33% | 16.67% | 75.00% | 29.50% | **35.29%** |
| **9** | **Rohan Mehta** | 16.67% | 0.00% | 40.00% | 12.10% | **15.70%** |
| **10**| **Siddharth Joshi**| 0.00% | 100.00% | 40.00% | 8.50% | **28.13%** |

---

## 13. System Limitations

1. **Varied Resume Formatting**: Multi-column tables, scanned images without OCR, or stylized graphic resumes may result in text extraction noise.
2. **Rule-Based Skill Synonym Matching**: Novel or rare technical acronyms not present in the skill dictionary might be missed.
3. **Date Ambiguity**: Non-standard date formats (e.g. Roman numerals or implicit dates) may miscalculate exact experience duration.
4. **TF-IDF Semantic Gap**: TF-IDF compares lexical frequency and n-gram overlap, but does not capture deep context compared to transformer embeddings (e.g., BERT/SBERT).
5. **Recruiter Decision Support**: The system is designed as an automated screening aid for recruiters, not a final autonomous hiring decision maker.
6. **Bias Prevention**: Personal information such as age, gender, photo, religion, caste, marital status, or home address is strictly excluded from scoring.

---

## 14. Future Enhancements

- **SBERT / Transformer Embeddings**: Integrate Sentence-BERT for semantic sentence-level similarity.
- **Tesseract OCR Integration**: Support image-based scanned PDF resumes.
- **Recruiter Feedback Loop**: Allow recruiters to adjust individual component weights dynamically via the UI dashboard.
- **Export Reports**: Generate PDF / Excel summary reports of candidate rankings for HR departments.
