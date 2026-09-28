import pandas as pd
import re


# ==========================================
# LOAD JOB DATASET
# ==========================================

df = pd.read_csv("jobs_clean.csv")


# ==========================================
# SKILL LIST
# ==========================================

skills = [
    "Python",
    "Java",
    "C++",
    "C",
    "SQL",
    "JavaScript",
    "React.js",
    "Node.js",
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "TensorFlow",
    "PyTorch",
    "AWS",
    "Azure",
    "Docker",
    "Kubernetes",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "Streamlit",
    "Excel",
    "Data Visualization"
]


# ==========================================
# SKILL ALIASES
# ==========================================

skill_aliases = {
    "React.js": "React",
    "Natural Language Processing": "NLP"
}


# ==========================================
# EXTRACT SKILLS FROM JOB TEXT
# ==========================================

def extract_skills(text):

    found_skills = []

    text = str(text)
    text_lower = text.lower()

    for skill in skills:

        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"

        if re.search(pattern, text_lower):

            canonical_skill = skill_aliases.get(skill, skill)

            if canonical_skill not in found_skills:
                found_skills.append(canonical_skill)

    return found_skills


# ==========================================
# APPLY SKILL EXTRACTION TO ALL JOBS
# ==========================================

df["job_skills"] = df["job_text"].apply(extract_skills)


# ==========================================
# SAVE UPDATED DATASET
# ==========================================

df.to_csv("jobs_with_skills.csv", index=False)


# ==========================================
# DISPLAY RESULTS
# ==========================================

print("\n========== JOB SKILL EXTRACTION ==========\n")

print("Total jobs:", len(df))

print("\nSample extracted skills:\n")

for i in range(min(10, len(df))):

    print("Job:", df.iloc[i]["title"])
    print("Skills:", df.iloc[i]["job_skills"])
    print("-" * 60)


print("\n==========================================")
print("Saved as: jobs_with_skills.csv")
print("Job skill extraction completed.")