import ast
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data", "jobs_with_skills.csv")

TFIDF_PATH = os.path.join(BASE_DIR, "data", "tfidf_vectorizer.joblib")
TFIDF_MATRIX_PATH = os.path.join(BASE_DIR, "data", "job_tfidf_matrix.joblib")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "data", "job_embeddings.npy")

MODEL_NAME = "all-MiniLM-L6-v2"

DEFAULT_WEIGHTS = {
    "tfidf": 0.40,
    "embedding": 0.40,
    "skill": 0.20,
}


# ============================================================
# DATA LOADING
# ============================================================

def load_jobs():
    """Load the processed job dataset."""

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Job dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    if "job_text" not in df.columns:
        raise ValueError(
            "job_text column is missing from jobs_with_skills.csv"
        )

    if "job_skills" not in df.columns:
        raise ValueError(
            "job_skills column is missing from jobs_with_skills.csv"
        )

    df["job_text"] = df["job_text"].fillna("").astype(str)
    df["job_skills"] = df["job_skills"].fillna("[]").astype(str)

    return df


# ============================================================
# SKILL PARSING
# ============================================================

def parse_skills(value):
    """Convert the stored skill-list string into a Python list."""

    if isinstance(value, list):
        return value

    try:
        parsed = ast.literal_eval(value)

        if isinstance(parsed, list):
            return [str(skill) for skill in parsed]

    except (ValueError, SyntaxError):
        pass

    return []


# ============================================================
# TF-IDF
# ============================================================

def build_tfidf(df):
    """Build TF-IDF representations for all job descriptions."""

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=20000,
        ngram_range=(1, 2)
    )

    matrix = vectorizer.fit_transform(df["job_text"])

    joblib.dump(vectorizer, TFIDF_PATH)
    joblib.dump(matrix, TFIDF_MATRIX_PATH)

    return vectorizer, matrix


def load_or_build_tfidf(df):
    """Load cached TF-IDF objects or build them if unavailable."""

    if os.path.exists(TFIDF_PATH) and os.path.exists(TFIDF_MATRIX_PATH):
        vectorizer = joblib.load(TFIDF_PATH)
        matrix = joblib.load(TFIDF_MATRIX_PATH)

        return vectorizer, matrix

    return build_tfidf(df)


# ============================================================
# SEMANTIC EMBEDDINGS
# ============================================================

def load_embedding_model():
    """Load the Sentence Transformer model."""

    return SentenceTransformer(MODEL_NAME)


def build_embeddings(df, model):
    """Generate and cache embeddings for all job descriptions."""

    embeddings = model.encode(
        df["job_text"].tolist(),
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(embeddings)

    np.save(EMBEDDINGS_PATH, embeddings)

    return embeddings


def load_or_build_embeddings(df, model):
    """Load cached embeddings or generate them if unavailable."""

    if os.path.exists(EMBEDDINGS_PATH):
        embeddings = np.load(EMBEDDINGS_PATH)

        if len(embeddings) == len(df):
            return embeddings

    return build_embeddings(df, model)


# ============================================================
# SKILL MATCHING
# ============================================================

def calculate_skill_score(resume_skills, job_skills):
    """
    Calculate resume-skill coverage.

    Score = matched resume skills / total resume skills

    This measures how much of the candidate's extracted skill set
    is relevant to the job.
    """

    resume_set = {
        skill.strip().lower()
        for skill in resume_skills
    }

    job_set = {
        skill.strip().lower()
        for skill in job_skills
    }

    if not resume_set:
        return 0.0

    matched = resume_set.intersection(job_set)

    return len(matched) / len(resume_set)


def get_matched_skills(resume_skills, job_skills):
    """Return skills present in both resume and job."""

    resume_set = {
        skill.strip().lower()
        for skill in resume_skills
    }

    return [
        skill for skill in job_skills
        if skill.strip().lower() in resume_set
    ]


def get_missing_skills(resume_skills, job_skills):
    """Return job skills missing from the resume."""

    resume_set = {
        skill.strip().lower()
        for skill in resume_skills
    }

    return [
        skill for skill in job_skills
        if skill.strip().lower() not in resume_set
    ]


# ============================================================
# HYBRID MATCHING
# ============================================================

def match_jobs(
    resume_text,
    resume_skills,
    top_n=10,
    weights=None
):
    """
    Rank jobs using a hybrid matching approach.

    Components:
        TF-IDF similarity
        Semantic embedding similarity
        Job-skill coverage
    """

    if not resume_text or not str(resume_text).strip():
        raise ValueError("Resume text cannot be empty.")

    df = load_jobs()

    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()

    total_weight = sum(weights.values())

    if total_weight <= 0:
        raise ValueError("Matching weights must have a positive sum.")

    weights = {
        key: value / total_weight
        for key, value in weights.items()
    }

    # --------------------------------------------------------
    # TF-IDF
    # --------------------------------------------------------

    vectorizer, tfidf_matrix = load_or_build_tfidf(df)

    resume_tfidf = vectorizer.transform([resume_text])

    tfidf_scores = cosine_similarity(
        resume_tfidf,
        tfidf_matrix
    )[0]

    # --------------------------------------------------------
    # Semantic similarity
    # --------------------------------------------------------

    model = load_embedding_model()

    job_embeddings = load_or_build_embeddings(df, model)

    resume_embedding = model.encode(
        [resume_text],
        normalize_embeddings=True
    )

    embedding_scores = cosine_similarity(
        resume_embedding,
        job_embeddings
    )[0]

    # --------------------------------------------------------
    # Skill matching
    # --------------------------------------------------------

    skill_scores = []

    matched_skills = []
    missing_skills = []

    for value in df["job_skills"]:

        job_skills = parse_skills(value)

        skill_scores.append(
            calculate_skill_score(
                resume_skills,
                job_skills
            )
        )

        matched_skills.append(
            get_matched_skills(
                resume_skills,
                job_skills
            )
        )

        missing_skills.append(
            get_missing_skills(
                resume_skills,
                job_skills
            )
        )

    skill_scores = np.array(skill_scores)

    # --------------------------------------------------------
    # Hybrid score
    # --------------------------------------------------------

    hybrid_scores = (
        weights["tfidf"] * tfidf_scores
        + weights["embedding"] * embedding_scores
        + weights["skill"] * skill_scores
    )

    results = df.copy()

    results["tfidf_score"] = tfidf_scores
    results["embedding_score"] = embedding_scores
    results["skill_score"] = skill_scores
    results["match_score"] = hybrid_scores
    results["matched_skills"] = matched_skills
    results["missing_skills"] = missing_skills

    results = results.sort_values(
        "match_score",
        ascending=False
    ).reset_index(drop=True)

    return results.head(top_n)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("HYBRID MATCHER TEST")
    print("=" * 60)

    jobs = load_jobs()

    print(f"Jobs loaded: {len(jobs)}")

    print("\nBuilding/loading TF-IDF...")

    vectorizer, matrix = load_or_build_tfidf(jobs)

    print(f"TF-IDF matrix shape: {matrix.shape}")

    print("\nLoading embedding model...")

    model = load_embedding_model()

    print(f"Embedding model loaded: {MODEL_NAME}")

    print("\nBuilding/loading job embeddings...")

    embeddings = load_or_build_embeddings(
        jobs,
        model
    )

    print(f"Embedding matrix shape: {embeddings.shape}")

    print("\n" + "=" * 60)
    print("MATCHER INITIALIZATION SUCCESSFUL")
    print("=" * 60)