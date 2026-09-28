import pandas as pd
import matplotlib.pyplot as plt
import re

# Load cleaned dataset
df = pd.read_csv("jobs_clean.csv")

# ==========================================
# 1. JOBS BY LOCATION
# ==========================================

location_counts = df["location"].value_counts().head(10)

plt.figure(figsize=(10, 6))
location_counts.plot(kind="bar")

plt.title("Top Job Locations")
plt.xlabel("Location")
plt.ylabel("Number of Jobs")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


# ==========================================
# 2. TOP JOB TITLES
# ==========================================

title_counts = df["title"].value_counts().head(10)

plt.figure(figsize=(10, 6))
title_counts.plot(kind="bar")

plt.title("Top 10 Job Titles")
plt.xlabel("Job Title")
plt.ylabel("Number of Jobs")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


# ==========================================
# 3. JOB CATEGORY DISTRIBUTION
# ==========================================

category_counts = df["category"].value_counts().head(10)

plt.figure(figsize=(10, 6))
category_counts.plot(kind="bar")

plt.title("Job Category Distribution")
plt.xlabel("Category")
plt.ylabel("Number of Jobs")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


# ==========================================
# 4. SALARY DISTRIBUTION
# ==========================================

salary_data = df["salary_min"].dropna()

plt.figure(figsize=(10, 6))
plt.hist(salary_data, bins=20)

plt.title("Salary Distribution")
plt.xlabel("Minimum Salary")
plt.ylabel("Number of Jobs")

plt.tight_layout()
plt.show()


# ==========================================
# 5. SKILL FREQUENCY ANALYSIS
# ==========================================

skills = [
    "Python", "Java", "C++", "C", "SQL",
    "JavaScript", "React", "Node.js",
    "Machine Learning", "Deep Learning",
    "TensorFlow", "PyTorch", "AWS", "Azure",
    "Docker", "Kubernetes", "Pandas", "NumPy",
    "Scikit-learn", "Excel"
]

skill_counts = {}

for skill in skills:

    # Use word boundaries to avoid incorrect matches
    # Example: "C" should not match "cloud", "technical", etc.
    pattern = r"\b" + re.escape(skill.lower()) + r"\b"

    count = df["job_text"].str.contains(
        pattern,
        case=False,
        na=False,
        regex=True
    ).sum()

    skill_counts[skill] = count


skill_counts = pd.Series(skill_counts).sort_values(ascending=False)

plt.figure(figsize=(12, 6))
skill_counts.plot(kind="bar")

plt.title("Frequency of Technical Skills in Job Postings")
plt.xlabel("Skill")
plt.ylabel("Number of Job Postings")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()