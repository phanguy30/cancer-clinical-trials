import requests
import json
from pathlib import Path

OUT = Path("data/raw")
OUT.mkdir(parents=True, exist_ok=True)

URL = "https://clinicaltrials.gov/api/v2/studies"

# Initial parameters for the API request
params = {
    "query.term": "cancer",
    "pageSize": 1000,
}

# A list to hold all downloaded studies
all_studies = []

# Pagination loop
next_page_token = None

while True:
    if next_page_token:
        #Add the page token to the parameters if it does not exist
        params["pageToken"] = next_page_token

    # Make the API request
    r = requests.get(URL, params=params)
    r.raise_for_status()
    data = r.json()
    
    # Extract studies and set next page token
    all_studies.extend(data["studies"])
    next_page_token = data.get("nextPageToken")
    
    #Print progress
    print(f"Downloaded {len(all_studies)} studies")

    #Stop if there are no more pages
    if not next_page_token:
        break

# Save the collected studies to a JSON file
with open(OUT / "cancer_trials_raw.json", "w") as f:
    json.dump(all_studies, f)
