import os
import requests

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": 10,
    "what": "python developer",
    "where": "Bengaluru",
    "content-type": "application/json"
}

response = requests.get(url, params=params)

print("Status Code:", response.status_code)

if response.status_code == 200:
    data = response.json()

    print("Total jobs found:", data.get("count"))

    for job in data.get("results", []):
        print("\nJob:", job.get("title"))
        print("Company:", job.get("company", {}).get("display_name"))
        print("Location:", job.get("location", {}).get("display_name"))
        print("Salary:", job.get("salary_min"), "-", job.get("salary_max"))
        print("URL:", job.get("redirect_url"))
else:
    print("Error:")
    print(response.text)