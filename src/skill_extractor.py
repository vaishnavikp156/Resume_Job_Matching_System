import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


# --------------------------------------------------
# Load skill vocabulary and aliases
# --------------------------------------------------

with open(BASE_DIR / "skills.json", "r", encoding="utf-8") as f:
    SKILL_CATEGORIES = json.load(f)

with open(BASE_DIR / "aliases.json", "r", encoding="utf-8") as f:
    ALIASES = json.load(f)


# --------------------------------------------------
# Build canonical skill set
# --------------------------------------------------

CANONICAL_SKILLS = set()

for skills in SKILL_CATEGORIES.values():
    CANONICAL_SKILLS.update(skills)


# --------------------------------------------------
# Normalize text
# --------------------------------------------------

def normalize_text(text):
    """
    Normalize text for reliable skill matching.
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()

    # Normalize common punctuation variations
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("’", "'")

    # Keep useful programming symbols
    text = re.sub(r"\s+", " ", text)

    return text


# --------------------------------------------------
# Create safe regex patterns
# --------------------------------------------------

def build_pattern(skill):
    """
    Build a regex pattern for a skill.

    Handles:
    - normal multi-word skills
    - short skills such as C and R
    - programming languages containing symbols such as C++ and C#
    """

    skill_lower = skill.lower().strip()

    # Short / ambiguous skills
    if skill_lower in {"c", "r", "go"}:
        return rf"(?<![a-z0-9+#]){re.escape(skill_lower)}(?![a-z0-9+#])"

    # Skills containing programming symbols
    if skill_lower in {"c++", "c#"}:
        return rf"(?<![a-z0-9]){re.escape(skill_lower)}(?![a-z0-9])"

    # Normal skills
    escaped = re.escape(skill_lower)

    # Allow flexible whitespace between words
    escaped = escaped.replace(r"\ ", r"\s+")

    return rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"
# --------------------------------------------------
# Build lookup patterns
# --------------------------------------------------

PATTERNS = []

# --------------------------------------------------
# Add all canonical skills
# --------------------------------------------------

for canonical in CANONICAL_SKILLS:

    pattern = build_pattern(canonical)

    PATTERNS.append(
        (
            pattern,
            canonical
        )
    )


# --------------------------------------------------
# Add aliases
# --------------------------------------------------

for alias, canonical in ALIASES.items():

    if canonical not in CANONICAL_SKILLS:
        # Ignore aliases pointing to unknown skills
        continue

    pattern = build_pattern(alias)

    PATTERNS.append(
        (
            pattern,
            canonical
        )
    )


# Remove duplicate pattern + canonical pairs
PATTERNS = list(set(PATTERNS))


# Sort longer patterns first
PATTERNS.sort(
    key=lambda x: len(x[0]),
    reverse=True
)

# Sort longer aliases first.
# Example:
# "machine learning" should be checked before "learning".
PATTERNS.sort(
    key=lambda x: len(x[0]),
    reverse=True
)


# --------------------------------------------------
# Extract skills
# --------------------------------------------------

def extract_skills(text):
    if not text:
        return []

    text = str(text)
    found = set()

    for pattern, canonical in PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.add(canonical)

    # Normalize equivalent skills to one canonical name
    normalization = {
        "AI": "Artificial Intelligence",
        "ML": "Machine Learning",
        "DL": "Deep Learning",
        "OOP": "Object-Oriented Programming",
        "NLP": "Natural Language Processing",
        "LLM": "Large Language Models",
        "Airflow": "Apache Airflow",
    }
    normalized = set()

    for skill in found:
        normalized.add(normalization.get(skill, skill))

    return sorted(normalized)

# --------------------------------------------------
# Convenience function
# --------------------------------------------------

def extract_skills_from_text(text):
    """
    Alias for extract_skills().
    """
    return extract_skills(text)


# --------------------------------------------------
# Testing
# --------------------------------------------------

if __name__ == "__main__":

    test_sentences = [

        "Experienced in Python, JavaScript, React.js and Node.js.",

        "Worked on ML, NLP and natural language processing projects.",

        "Developed applications using C++, C#, Java and SQL.",

        "Experience with sklearn, NumPy, Pandas and TensorFlow.",

        "Built REST APIs using FastAPI, Express.js and PostgreSQL.",

        "Worked with AWS, Azure, GCP and Kubernetes.",

        "Knowledge of Git, GitHub, Docker and CI/CD.",

        "Strong skills in data structures, algorithms and OOP.",

        "Experience in C and R programming."
    ]

    print("\n========== SKILL EXTRACTION TEST ==========\n")

    for i, sentence in enumerate(test_sentences, start=1):

        skills = extract_skills(sentence)

        print(f"Test {i}:")
        print(f"Text   : {sentence}")
        print(f"Skills : {skills}")
        print("-" * 70)

    print("\n===========================================\n")

    print(f"Canonical skills loaded : {len(CANONICAL_SKILLS)}")
    print(f"Aliases loaded          : {len(ALIASES)}")
    print(f"Patterns loaded         : {len(PATTERNS)}")