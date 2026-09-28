from resume_parser import extract_resume_text
import re


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
# EXTRACT SKILLS
# ==========================================

def extract_skills(text):

    found_skills = []

    text_lower = text.lower()

    for skill in skills:

        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"

        if re.search(pattern, text_lower):

            canonical_skill = skill_aliases.get(skill, skill)

            if canonical_skill not in found_skills:
                found_skills.append(canonical_skill)

    return found_skills


# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    file_path = input("Enter resume file path: ")

    resume_text = extract_resume_text(file_path)

    found_skills = extract_skills(resume_text)

    print("\n========== EXTRACTED SKILLS ==========\n")

    for skill in found_skills:
        print("-", skill)

    print("\n======================================")
    print("Skill extraction completed.")