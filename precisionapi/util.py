from requests import get
import json
from .variables import API_URL
from sys import stderr

def retrieve_all_results(endpoint, params):
    url = API_URL + endpoint
    results = []
    page = 0
    while True:
        params["page"] = page
        try:
            resp = get(url, params=params)
            data = resp.json()
        except json.decoder.JSONDecodeError:
            print(resp.text, file=stderr)
            raise
        if not data:
            break
        print(f"page {page}", file=stderr)
        results += data
        page += 1
    return results
