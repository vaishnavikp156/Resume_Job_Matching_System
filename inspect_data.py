import pandas as pd

# Load dataset
df = pd.read_csv("jobs_raw.csv")

print("========== DATASET INFO ==========")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\n========== COLUMNS ==========")
print(df.columns.tolist())

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== DUPLICATE ROWS ==========")
print(df.duplicated().sum())

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== JOB CATEGORIES ==========")
print(df["category"].value_counts())

print("\n========== CONTRACT TYPES ==========")
print(df["contract_type"].value_counts(dropna=False))

print("\n========== SALARY AVAILABILITY ==========")
print("Salary available:",
      df["salary_min"].notna().sum())

print("Salary missing:",
      df["salary_min"].isna().sum())

print("\n========== DESCRIPTION LENGTH ==========")
df["description_length"] = df["description"].fillna("").str.len()

print(df["description_length"].describe())

print("\n========== FIRST 5 JOBS ==========")
print(df[["title", "company", "location"]].head())