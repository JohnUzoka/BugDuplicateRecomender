"""
Fetch ~1000 bug-labeled issues from godotengine/godot and write them to CSV.

Usage:
    python scripts/fetch_godot_issues.py

Set GITHUB_TOKEN env var for higher rate limits (5000 req/hr vs 60).
"""

import csv
import os
import re
import time

import requests

API_URL = "https://api.github.com/repos/godotengine/godot/issues"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "godot_bug_reports.csv")
PAGES = 10
PER_PAGE = 100


def clean_body(text):
    """Collapse a GitHub issue body into a single plain-text line."""
    if not text:
        return ""
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def fetch_issues(token=None):
    """Fetch bug-labeled issues across multiple pages."""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    all_issues = []

    for page in range(1, PAGES + 1):
        params = {
            "labels": "bug",
            "state": "all",
            "per_page": PER_PAGE,
            "page": page,
        }

        print(f"Fetching page {page}/{PAGES} …")
        resp = requests.get(API_URL, headers=headers, params=params, timeout=30)

        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            reset = int(resp.headers.get("X-RateLimit-Reset", 0))
            wait = max(reset - int(time.time()), 5)
            print(f"Rate-limited. Waiting {wait}s …")
            time.sleep(wait)
            resp = requests.get(API_URL, headers=headers, params=params, timeout=30)

        resp.raise_for_status()
        batch = resp.json()

        if not batch:
            print(f"No more issues at page {page}. Stopping.")
            break

        for issue in batch:
            all_issues.append({
                "id": issue["number"],
                "title": issue["title"],
                "body": clean_body(issue.get("body")),
            })

        print(f"  Got {len(batch)} issues (total so far: {len(all_issues)})")

    return all_issues


def write_csv(issues, path):
    """Write issues to a CSV file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "title", "body"], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(issues)
    print(f"Wrote {len(issues)} issues to {path}")


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not set – using unauthenticated requests (60 req/hr limit).")

    issues = fetch_issues(token)
    output = os.path.normpath(OUTPUT_PATH)
    write_csv(issues, output)


if __name__ == "__main__":
    main()
