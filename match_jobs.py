import pandas as pd
import ast

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from resume_parser import extract_resume_text
from skill_extractor import extract_skills


# ==========================================
# LOAD JOB DATASET
# ==========================================

df = pd.read_csv("jobs_with_skills.csv")


# Convert saved skill strings back to Python lists
df["job_skills"] = df["job_skills"].apply(ast.literal_eval)


# ==========================================
# GET RESUME
# ==========================================

resume_path = input("Enter resume file path: ")

resume_text = extract_resume_text(resume_path)

resume_skills = extract_skills(resume_text)


print("\n========== RESUME SKILLS ==========\n")

print(resume_skills)

print("\n===================================\n")


# ==========================================
# TF-IDF TEXT SIMILARITY
# ==========================================

documents = [resume_text] + df["job_text"].fillna("").tolist()

vectorizer = TfidfVectorizer(
    stop_words="english"
)

tfidf_matrix = vectorizer.fit_transform(documents)

resume_vector = tfidf_matrix[0]

job_vectors = tfidf_matrix[1:]


similarities = cosine_similarity(
    resume_vector,
    job_vectors
).flatten()


# ==========================================
# SKILL MATCHING
# ==========================================

def calculate_skill_score(job_skills):

    if len(resume_skills) == 0:
        return 0

    matched_skills = set(resume_skills).intersection(
        set(job_skills)
    )

    score = len(matched_skills) / len(resume_skills)

    return score


df["text_similarity"] = similarities

df["skill_score"] = df["job_skills"].apply(
    calculate_skill_score
)


# ==========================================
# FINAL MATCH SCORE
# ==========================================

df["match_score"] = (
    0.70 * df["text_similarity"]
    +
    0.30 * df["skill_score"]
)


# Convert to percentage
df["match_percentage"] = (
    df["match_score"] * 100
)


# ==========================================
# SORT JOBS
# ==========================================

df = df.sort_values(
    by="match_score",
    ascending=False
)

# ==========================================
# SAVE RECOMMENDATIONS
# ==========================================

recommendation_columns = [
    "title",
    "company",
    "location",
    "match_percentage",
    "text_similarity",
    "skill_score",
    "job_skills",
    "job_url"
]

df[recommendation_columns].head(20).to_csv(
    "recommendations.csv",
    index=False
)

print("\nRecommendations saved as: recommendations.csv")

# ==========================================
# DISPLAY TOP 10 JOBS
# ==========================================

print("\n========== TOP JOB RECOMMENDATIONS ==========\n")


for i, (_, job) in enumerate(
    df.head(10).iterrows(),
    start=1
):

    # Find only skills common to resume and job
    matched_skills = sorted(
        set(resume_skills).intersection(
            set(job["job_skills"])
        )
    )

    print(f"{i}. {job['title']}")
    print(f"   Company: {job['company']}")
    print(f"   Location: {job['location']}")
    print(f"   Match Score: {job['match_percentage']:.2f}%")
    print(
        f"   Text Similarity: "
        f"{job['text_similarity'] * 100:.2f}%"
    )
    print(
        f"   Skill Match: "
        f"{job['skill_score'] * 100:.2f}%"
    )
    print(f"   Matched Skills: {matched_skills}")
    print(f"   Job URL: {job['job_url']}")
    print("-" * 70)