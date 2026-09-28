import pandas as pd

# ==========================================
# LOAD RAW DATA
# ==========================================

df = pd.read_csv("jobs_raw.csv")

print("Original dataset shape:", df.shape)


# ==========================================
# HANDLE MISSING COMPANY
# ==========================================

df["company"] = df["company"].fillna("Not Specified")


# ==========================================
# HANDLE MISSING CONTRACT INFORMATION
# ==========================================

df["contract_type"] = df["contract_type"].fillna("Not Specified")

df["contract_time"] = df["contract_time"].fillna("Not Specified")


# ==========================================
# CLEAN TEXT COLUMNS
# ==========================================

text_columns = [
    "title",
    "company",
    "location",
    "description",
    "category"
]

for column in text_columns:
    df[column] = df[column].astype(str).str.strip()


# ==========================================
# CONVERT DATE
# ==========================================

df["created"] = pd.to_datetime(
    df["created"],
    errors="coerce"
)


# ==========================================
# REMOVE DUPLICATE JOB IDs
# ==========================================

df = df.drop_duplicates(subset="job_id")


# ==========================================
# CREATE COMBINED TEXT FOR MATCHING
# ==========================================

df["job_text"] = (
    df["title"] + " " +
    df["description"] + " " +
    df["category"]
)


# ==========================================
# SAVE CLEAN DATASET
# ==========================================

df.to_csv("jobs_clean.csv", index=False)


# ==========================================
# DISPLAY RESULTS
# ==========================================

print("\n========== CLEAN DATASET ==========")

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\nMissing values:")
print(df.isnull().sum())

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset saved as jobs_clean.csv")