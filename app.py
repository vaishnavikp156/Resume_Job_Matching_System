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
# CUSTOM STYLING
# ==========================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #666666;
        margin-bottom: 25px;
    }

    .job-card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid rgba(128, 128, 128, 0.35);
    margin-bottom: 20px;
    background-color: transparent;
}

    .score {
        font-size: 28px;
        font-weight: 700;
    }

    .skill-badge {
    display: inline-block;
    padding: 5px 10px;
    margin: 3px;
    border-radius: 15px;
    background-color: rgba(128, 128, 128, 0.20);
    color: inherit !important;
    border: 1px solid rgba(128, 128, 128, 0.35);
    font-size: 14px;
    font-weight: 500;
}

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# TITLE
# ==========================================

st.markdown(
    '<div class="main-title">💼 Resume Job Matching System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Find relevant job opportunities based on your resume content and technical skills.'
    '</div>',
    unsafe_allow_html=True
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
# SIDEBAR
# ==========================================

st.sidebar.header("🔎 Recommendation Filters")

location_options = ["All Locations"] + sorted(
    df["location"].dropna().unique().tolist()
)

selected_location = st.sidebar.selectbox(
    "📍 Location",
    location_options
)

minimum_score = st.sidebar.slider(
    "🎯 Minimum Match Score (%)",
    min_value=0,
    max_value=100,
    value=0,
    step=5
)

number_of_jobs = st.sidebar.selectbox(
    "🔢 Number of Recommendations",
    [5, 10, 15, 20],
    index=1
)


# ==========================================
# RESUME UPLOAD
# ==========================================

st.subheader("📄 Upload Your Resume")

uploaded_file = st.file_uploader(
    "Choose a PDF or DOCX resume",
    type=["pdf", "docx"]
)


# ==========================================
# MATCHING
# ==========================================

if uploaded_file is not None:

    # ======================================
    # SAVE UPLOADED FILE TEMPORARILY
    # ======================================

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


    # ======================================
    # EXTRACT RESUME TEXT
    # ======================================

    resume_text = extract_resume_text(
        temp_path
    )


    # ======================================
    # EXTRACT RESUME SKILLS
    # ======================================

    resume_skills = extract_skills(
        resume_text
    )


    # ======================================
    # DISPLAY RESUME INFORMATION
    # ======================================

    st.subheader("🧠 Extracted Resume Skills")

    if resume_skills:

        skill_html = ""

        for skill in resume_skills:

            skill_html += (
                f'<span class="skill-badge">'
                f'{skill}'
                f'</span>'
            )

        st.markdown(
            skill_html,
            unsafe_allow_html=True
        )

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
    # FINAL MATCH SCORE
    # ======================================

    df["match_score"] = (
        0.70 * df["text_similarity"]
        +
        0.30 * df["skill_score"]
    )

    df["match_percentage"] = (
        df["match_score"] * 100
    )


    # ======================================
    # APPLY LOCATION FILTER
    # ======================================

    filtered_df = df.copy()

    if selected_location != "All Locations":

        filtered_df = filtered_df[
            filtered_df["location"]
            ==
            selected_location
        ]


    # ======================================
    # APPLY SCORE FILTER
    # ======================================

    filtered_df = filtered_df[
        filtered_df["match_percentage"]
        >=
        minimum_score
    ]


    # ======================================
    # SORT RESULTS
    # ======================================

    results = filtered_df.sort_values(
        "match_score",
        ascending=False
    ).head(
        number_of_jobs
    )


    # ======================================
    # SUMMARY
    # ======================================

    st.subheader("📊 Matching Summary")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Jobs Analyzed",
            f"{len(df):,}"
        )

    with col2:

        st.metric(
            "Resume Skills",
            len(resume_skills)
        )

    with col3:

        st.metric(
            "Jobs Recommended",
            len(results)
        )


    # ======================================
    # DISPLAY RESULTS
    # ======================================

    st.subheader("🎯 Recommended Jobs")

    if len(results) == 0:

        st.warning(
            "No jobs match the selected filters. "
            "Try lowering the minimum score or selecting All Locations."
        )

    else:

        for index, (_, job) in enumerate(
            results.iterrows(),
            start=1
        ):

            matched_skills = sorted(
                set(resume_skills).intersection(
                    set(job["job_skills"])
                )
            )


            # ==================================
            # JOB CARD
            # ==================================

            st.markdown(
                '<div class="job-card">',
                unsafe_allow_html=True
            )

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

                st.markdown(
                    f'<div class="score">'
                    f'🎯 {job["match_percentage"]:.2f}%'
                    f'</div>',
                    unsafe_allow_html=True
                )

                st.caption("Match Score")


            # ==================================
            # SCORE DETAILS
            # ==================================

            score_col1, score_col2 = st.columns(2)

            with score_col1:

                st.write(
                    f"**Text Similarity:** "
                    f"{job['text_similarity'] * 100:.2f}%"
                )

            with score_col2:

                st.write(
                    f"**Skill Match:** "
                    f"{job['skill_score'] * 100:.2f}%"
                )


            # ==================================
            # MATCHED SKILLS
            # ==================================

            if matched_skills:

                st.write("**Matched Skills:**")

                skill_html = ""

                for skill in matched_skills:

                    skill_html += (
                        f'<span class="skill-badge">'
                        f'{skill}'
                        f'</span>'
                    )

                st.markdown(
                    skill_html,
                    unsafe_allow_html=True
                )

            else:

                st.write(
                    "**Matched Skills:** None"
                )


            # ==================================
            # VIEW JOB
            # ==================================

            if pd.notna(job["job_url"]):

                st.link_button(
                    "🔗 View Job",
                    job["job_url"]
                )


            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


    # ======================================
    # CLEAN TEMP FILE
    # ======================================

    os.remove(temp_path)