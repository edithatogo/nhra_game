import json

import requests

headers = {"Accept": "application/vnd.sdmx.structure+json;version=1.0"}
url = "https://data.api.abs.gov.au/rest/dataflow/ABS/WPI/1.2.0?references=descendants"

try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        with open("wpi_metadata.json", "w") as f:
            json.dump(data, f, indent=2)
        print("Saved metadata to wpi_metadata.json")
    else:
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
