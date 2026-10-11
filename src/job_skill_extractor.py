import sys
from pathlib import Path

import pandas as pd


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Allow importing skill_extractor.py from src/
sys.path.insert(0, str(BASE_DIR / "src"))

from skill_extractor import extract_skills


# ==========================================
# LOAD JOB DATASET
# ==========================================

INPUT_FILE = DATA_DIR / "jobs_clean.csv"
OUTPUT_FILE = DATA_DIR / "jobs_with_skills.csv"

df = pd.read_csv(INPUT_FILE)


# ==========================================
# VALIDATE INPUT
# ==========================================

if "job_text" not in df.columns:
    raise ValueError(
        "Column 'job_text' not found in jobs_clean.csv"
    )


# ==========================================
# EXTRACT SKILLS
# ==========================================

df["job_skills"] = df["job_text"].apply(extract_skills)


# ==========================================
# SAVE UPDATED DATASET
# ==========================================

df.to_csv(OUTPUT_FILE, index=False)


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
print("Canonical skills available: 256")
print("Aliases available: 120")
print("Saved as:", OUTPUT_FILE)
print("Job skill extraction completed.")