import streamlit as st
import pandas as pd
import ast
import tempfile
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from resume_parser import extract_resume_text
from skill_extractor import extract_skills


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Resume Job Matching System",
    page_icon="💼",
    layout="wide"
)


# ==========================================
# TITLE
# ==========================================

st.title("💼 Resume Job Matching System")

st.write(
    "Upload your resume to find relevant job opportunities "
    "based on resume content and technical skills."
)


# ==========================================
# LOAD JOB DATA
# ==========================================

@st.cache_data
def load_jobs():

    df = pd.read_csv("jobs_with_skills.csv")

    df["job_skills"] = df["job_skills"].apply(
        ast.literal_eval
    )

    return df


df = load_jobs()


# ==========================================
# RESUME UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"]
)


# ==========================================
# MATCHING
# ==========================================

if uploaded_file is not None:

    # Save uploaded file temporarily
    suffix = os.path.splitext(
        uploaded_file.name
    )[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        temp_file.write(
            uploaded_file.getbuffer()
        )

        temp_path = temp_file.name


    # Extract resume text
    resume_text = extract_resume_text(
        temp_path
    )


    # Extract resume skills
    resume_skills = extract_skills(
        resume_text
    )


    # ======================================
    # DISPLAY RESUME SKILLS
    # ======================================

    st.subheader("📋 Extracted Resume Skills")

    if resume_skills:

        skill_text = " • ".join(
            resume_skills
        )

        st.info(skill_text)

    else:

        st.warning(
            "No predefined technical skills were detected."
        )


    # ======================================
    # TF-IDF SIMILARITY
    # ======================================

    documents = (
        [resume_text]
        +
        df["job_text"].fillna("").tolist()
    )


    vectorizer = TfidfVectorizer(
        stop_words="english"
    )


    tfidf_matrix = vectorizer.fit_transform(
        documents
    )


    resume_vector = tfidf_matrix[0]

    job_vectors = tfidf_matrix[1:]


    similarities = cosine_similarity(
        resume_vector,
        job_vectors
    ).flatten()


    # ======================================
    # SKILL MATCHING
    # ======================================

    def calculate_skill_score(job_skills):

        if len(resume_skills) == 0:
            return 0

        matched_skills = set(
            resume_skills
        ).intersection(
            set(job_skills)
        )

        return (
            len(matched_skills)
            /
            len(resume_skills)
        )


    df["text_similarity"] = similarities

    df["skill_score"] = df[
        "job_skills"
    ].apply(
        calculate_skill_score
    )


    # ======================================
    # FINAL SCORE
    # ======================================

    df["match_score"] = (
        0.70 * df["text_similarity"]
        +
        0.30 * df["skill_score"]
    )


    df["match_percentage"] = (
        df["match_score"] * 100
    )


    # Sort by score
    results = df.sort_values(
        "match_score",
        ascending=False
    ).head(10)


    # ======================================
    # DISPLAY RESULTS
    # ======================================

    st.subheader(
        "🎯 Top Job Recommendations"
    )

    for index, (_, job) in enumerate(
        results.iterrows(),
        start=1
    ):

        matched_skills = sorted(
            set(resume_skills).intersection(
                set(job["job_skills"])
            )
        )


        with st.container():

            st.markdown(
                f"### {index}. {job['title']}"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(
                    f"🏢 **Company:** "
                    f"{job['company']}"
                )

            with col2:
                st.write(
                    f"📍 **Location:** "
                    f"{job['location']}"
                )

            with col3:
                st.write(
                    f"🎯 **Match Score:** "
                    f"{job['match_percentage']:.2f}%"
                )


            st.write(
                f"**Text Similarity:** "
                f"{job['text_similarity'] * 100:.2f}%"
            )


            st.write(
                f"**Skill Match:** "
                f"{job['skill_score'] * 100:.2f}%"
            )


            if matched_skills:

                st.write(
                    "**Matched Skills:** "
                    +
                    ", ".join(
                        matched_skills
                    )
                )

            else:

                st.write(
                    "**Matched Skills:** None"
                )


            st.link_button(
                "🔗 View Job",
                job["job_url"]
            )


            st.divider()


    # ======================================
    # CLEAN TEMP FILE
    # ======================================

    os.remove(temp_path)