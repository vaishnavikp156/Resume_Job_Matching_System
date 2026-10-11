import os
import sys
import tempfile

import pandas as pd
import streamlit as st

# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.matcher import match_jobs
from src.resume_parser import extract_resume_text
from src.skill_extractor import extract_skills


# ------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="ResumeMatch",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------
# Styling
# ------------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 3rem;
        font-weight: 750;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }

    .job-card {
        padding: 1.3rem;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        margin-bottom: 1rem;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .job-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .job-company {
        color: #4b5563;
        margin-bottom: 0.2rem;
    }

    .job-location {
        color: #6b7280;
        margin-bottom: 0.8rem;
    }

    .score-box {
        padding: 0.8rem;
        border-radius: 10px;
        background: #f8fafc;
        border: 1px solid #e5e7eb;
    }

    .skill-badge {
        display: inline-block;
        padding: 5px 10px;
        margin: 3px 4px 3px 0;
        border-radius: 999px;
        background: #eef2ff;
        color: #3730a3;
        border: 1px solid #c7d2fe;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .missing-badge {
        display: inline-block;
        padding: 5px 10px;
        margin: 3px 4px 3px 0;
        border-radius: 999px;
        background: #fff7ed;
        color: #9a3412;
        border: 1px solid #fed7aa;
        font-size: 0.85rem;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.markdown(
    '<div class="main-title">ResumeMatch</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Personalized job recommendations using text similarity and skill matching.'
    '</div>',
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

with st.sidebar:

    st.header("ResumeMatch")

    st.write(
        "Upload your resume and get ranked job recommendations "
        "based on your skills and resume content."
    )

    st.divider()

    # Location filter
    location_options = [
        "All Locations",
        "Ahmedabad",
        "Bengaluru",
        "Bhopal",
        "Bhubaneswar",
        "Chandigarh",
        "Chennai",
        "Coimbatore",
        "Delhi",
        "Gurgaon",
        "Hyderabad",
        "Indore",
        "Jaipur",
        "Kochi",
        "Kolkata",
        "Lucknow",
        "Mangaluru",
        "Mumbai",
        "Mysuru",
        "Nagpur",
        "Noida",
        "Pune",
        "Surat",
        "Thiruvananthapuram",
        "Vadodara",
        "Visakhapatnam",
    ]

    selected_location = st.selectbox(
        "Location",
        location_options,
        index=0,
    )

    st.divider()

    # Number of recommendations
    top_n = st.number_input(
        "Number of recommendations",
        min_value=1,
        max_value=3000,
        value=10,
        step=1,
    )

    if top_n > 100:
        st.warning(
            "⚠️ Maximum 100 recommendations allowed.\n\n"
            "Please enter a number between 1 and 100."
        )

    st.divider()

    st.caption("Matching methodology")

    st.write(
        """
        **40%** TF-IDF text similarity  
        **40%** semantic similarity  
        **20%** skill coverage
        """
    )

    st.caption(
        "The final score is a hybrid similarity score used to rank jobs."
    )

# ------------------------------------------------------------
# Dataset information
# ------------------------------------------------------------

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "jobs_with_skills.csv",
)

try:

    jobs_df = pd.read_csv(DATA_PATH)

    job_count = len(jobs_df)

    location_count = (
        jobs_df["location"].nunique()
        if "location" in jobs_df.columns
        else 0
    )

except Exception:

    job_count = 3085
    location_count = 25


col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Jobs", f"{job_count:,}")

with col2:
    st.metric("Locations", location_count)

with col3:
    st.metric("Matching", "Resume + Skills")


st.divider()


# ------------------------------------------------------------
# Resume upload
# ------------------------------------------------------------

st.subheader("Upload your resume")

uploaded_file = st.file_uploader(
    "Upload a PDF or DOCX resume",
    type=["pdf", "docx"],
    help="Your resume is processed locally for skill extraction and matching.",
)


# ------------------------------------------------------------
# Main processing
# ------------------------------------------------------------

if uploaded_file is not None:

    suffix = os.path.splitext(uploaded_file.name)[1]

    temp_path = None

    try:

        # ----------------------------------------------------
        # Save uploaded file temporarily
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name


        # ----------------------------------------------------
        # Extract resume text
        # ----------------------------------------------------

        with st.spinner("Reading your resume..."):

            resume_text = extract_resume_text(temp_path)


        if not resume_text.strip():

            st.error(
                "Could not extract text from the uploaded resume."
            )

            st.stop()


        # ----------------------------------------------------
        # Extract skills
        # ----------------------------------------------------

        resume_skills = extract_skills(resume_text)


        st.success(
            f"Resume processed successfully — "
            f"{len(resume_skills)} skills detected."
        )


        # ----------------------------------------------------
        # Resume skills display
        # ----------------------------------------------------

        st.subheader("Detected Skills")

        if resume_skills:

            skill_html = ""

            for skill in resume_skills:

                skill_html += (
                    f'<span class="skill-badge">{skill}</span>'
                )

            st.markdown(
                skill_html,
                unsafe_allow_html=True,
            )

        else:

            st.info(
                "No recognized technical skills were detected."
            )


        st.divider()

        # ----------------------------------------------------
        # Matching
        # ----------------------------------------------------

        if top_n > 100:
            st.stop()

        with st.spinner(
            "Finding the best matching jobs..."
        ):

            results = match_jobs(
                resume_text,
                resume_skills,
                top_n=len(jobs_df),
            )

        # Apply location filter after ranking all jobs
        if selected_location != "All Locations":
            results = results[
                results["location"].str.contains(
                    selected_location,
                    case=False,
                    na=False,
                )
            ].reset_index(drop=True)

        # Show only requested number of jobs
        results = results.head(top_n)

        # ----------------------------------------------------
        # Results
        # ----------------------------------------------------

        st.subheader("Recommended Jobs")

        st.caption(
            f"Showing the top {min(top_n, len(results))} "
            "jobs ranked by hybrid match score."
        )


        for rank, (_, job) in enumerate(
            results.iterrows(),
            start=1,
        ):

            matched_skills = job.get(
                "matched_skills",
                [],
            )

            missing_skills = job.get(
                "missing_skills",
                [],
            )


            # ----------------------------------------------
            # Job card
            # ----------------------------------------------

            st.markdown(
                '<div class="job-card">',
                unsafe_allow_html=True,
            )


            st.markdown(
                f'<div class="job-title">'
                f'#{rank} — {job["title"]}'
                f'</div>',
                unsafe_allow_html=True,
            )


            company = job.get(
                "company",
                "Not specified",
            )

            location = job.get(
                "location",
                "Not specified",
            )


            st.markdown(
                f'<div class="job-company">'
                f'🏢 {company}'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div class="job-location">'
                f'📍 {location}'
                f'</div>',
                unsafe_allow_html=True,
            )


            # ----------------------------------------------
            # Overall score
            # ----------------------------------------------

            match_score = float(
                job.get("match_score", 0)
            )


            st.markdown(
                f"### Overall Match Score: "
                f"{match_score * 100:.2f}%",
            )


            # ----------------------------------------------
            # Component scores
            # ----------------------------------------------

            score_col1, score_col2, score_col3 = st.columns(3)


            with score_col1:

                st.write(
                    f"**TF-IDF Similarity:** "
                    f"{job['tfidf_score'] * 100:.2f}%"
                )


            with score_col2:

                st.write(
                    f"**Semantic Similarity:** "
                    f"{job['embedding_score'] * 100:.2f}%"
                )


            with score_col3:

                st.write(
                    f"**Skill Coverage:** "
                    f"{job['skill_score'] * 100:.2f}%"
                )


            # ----------------------------------------------
            # Matched skills
            # ----------------------------------------------

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
                    unsafe_allow_html=True,
                )

            else:

                st.write(
                    "**Matched Skills:** None"
                )


            # ----------------------------------------------
            # Missing skills
            # ----------------------------------------------

            if missing_skills:

                with st.expander(
                    "Skills you may want to develop for this job"
                ):

                    missing_html = ""

                    for skill in missing_skills:

                        missing_html += (
                            f'<span class="missing-badge">'
                            f'{skill}'
                            f'</span>'
                        )

                    st.markdown(
                        missing_html,
                        unsafe_allow_html=True,
                    )

            else:

                st.success(
                    "No additional extracted skills identified."
                )


            # ----------------------------------------------
            # Job link
            # ----------------------------------------------

            if pd.notna(job.get("job_url")):

                st.link_button(
                    "🔗 View Job",
                    job["job_url"],
                )


            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )


    except Exception as e:

        st.error(
            f"An error occurred while processing the resume: {e}"
        )

        st.exception(e)


    finally:

        if temp_path and os.path.exists(temp_path):

            os.remove(temp_path)


# ------------------------------------------------------------
# Methodology
# ------------------------------------------------------------

st.divider()

with st.expander("How ResumeMatch works"):

    st.markdown(
        """
        ### 1. Resume processing
        The uploaded PDF or DOCX resume is converted into text.

        ### 2. Skill extraction
        Technical skills are identified using a controlled skill
        vocabulary and alias normalization.

        ### 3. Job data
        Job postings are retrieved from the collected Adzuna dataset.

        ### 4. Text similarity
        TF-IDF and cosine similarity compare the resume text
        with job posting text.

        ### 5. Semantic similarity
        Sentence embeddings provide a semantic comparison between
        the resume and job descriptions.

        ### 6. Skill coverage
        The proportion of the candidate's extracted skills that
        are also present in the job posting is calculated.

        ### 7. Hybrid ranking
        The final ranking score combines:

        - 40% TF-IDF similarity
        - 40% semantic similarity
        - 20% skill coverage

        The system then ranks the job postings and displays
        matched and missing skills.
        """
    )


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.caption(
    "ResumeMatch — Personalized job recommendations using "
    "text similarity and skill matching."
)
