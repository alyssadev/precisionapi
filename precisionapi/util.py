from requests import get as _get
import json
from .variables import API_URL
from sys import stderr

def get(endpoint, *args, **kwargs):
    return _get(API_URL + endpoint, *args, **kwargs)

def retrieve_all_results(endpoint, params, limit=None):
    results = []
    page = 0
    while True:
        params["page"] = page
        try:
            resp = get(endpoint, params=params)
            data = resp.json()
        except json.decoder.JSONDecodeError:
            print(resp.text, file=stderr)
            raise
        if not data:
            break
#        print(f"page {page}", file=stderr)
        results += data
        if limit:
            break
        page += 1
    return results
