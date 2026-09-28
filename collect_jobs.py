import os
import requests
import pandas as pd
import time

# ==============================
# API CREDENTIALS
# ==============================

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# ==============================
# JOB ROLES
# ==============================

job_roles = [
    "Python Developer",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "Software Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Java Developer",
    "Web Developer",
    "AI Engineer"
]

# ==============================
# INDIAN LOCATIONS
# ==============================

locations = [
    "Bengaluru",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Mumbai",
    "Delhi",
    "Noida",
    "Gurgaon",
    "Kolkata",
    "Ahmedabad"
]

# ==============================
# API URL
# ==============================

url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

all_jobs = []

# ==============================
# COLLECT JOBS
# ==============================

for role in job_roles:

    for location in locations:

        print(f"\nSearching: {role} | {location}")

        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": 20,
            "what": role,
            "where": location,
            "content-type": "application/json"
        }

        try:

            response = requests.get(url, params=params)

            if response.status_code == 200:

                data = response.json()

                jobs = data.get("results", [])

                print("Jobs received:", len(jobs))

                for job in jobs:

                    all_jobs.append({
                        "job_id": job.get("id"),
                        "title": job.get("title"),
                        "company": job.get("company", {}).get("display_name"),
                        "location": job.get("location", {}).get("display_name"),
                        "description": job.get("description"),
                        "category": job.get("category", {}).get("label"),
                        "salary_min": job.get("salary_min"),
                        "salary_max": job.get("salary_max"),
                        "contract_type": job.get("contract_type"),
                        "contract_time": job.get("contract_time"),
                        "created": job.get("created"),
                        "job_url": job.get("redirect_url")
                    })

            else:

                print("API Error:", response.status_code)

        except Exception as e:

            print("Error:", e)

        # Small delay between requests
        time.sleep(1)


# ==============================
# CREATE DATAFRAME
# ==============================

df = pd.DataFrame(all_jobs)

print("\n================================")
print("RAW JOBS COLLECTED:", len(df))
print("================================")

# ==============================
# REMOVE DUPLICATE JOBS
# ==============================

df = df.drop_duplicates(subset="job_id")

print("UNIQUE JOBS:", len(df))

# ==============================
# SAVE DATASET
# ==============================

df.to_csv("jobs_raw.csv", index=False)

print("\nDataset saved as jobs_raw.csv")

print("\nDataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())