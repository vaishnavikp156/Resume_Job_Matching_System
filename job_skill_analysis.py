import pandas as pd
import ast
import matplotlib.pyplot as plt


# ==========================================
# LOAD JOB DATA
# ==========================================

df = pd.read_csv("jobs_with_skills.csv")


# ==========================================
# COUNT SKILLS
# ==========================================

skill_counts = {}

for skill_list in df["job_skills"]:

    skills = ast.literal_eval(skill_list)

    for skill in skills:

        if skill not in skill_counts:
            skill_counts[skill] = 0

        skill_counts[skill] += 1


skill_counts = pd.Series(skill_counts).sort_values(
    ascending=False
)


# ==========================================
# DISPLAY RESULTS
# ==========================================

print("\n========== JOB SKILL FREQUENCY ==========\n")

print(skill_counts.to_string())

print("\n==========================================")


# ==========================================
# TOP 15 SKILLS
# ==========================================

top_skills = skill_counts.head(15)

print("\nTop 15 skills:\n")
print(top_skills)


# ==========================================
# VISUALIZATION
# ==========================================

plt.figure(figsize=(12, 6))

top_skills.plot(kind="bar")

plt.title("Top 15 Technical Skills in Job Postings")
plt.xlabel("Skill")
plt.ylabel("Number of Job Postings")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()