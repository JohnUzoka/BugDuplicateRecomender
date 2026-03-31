import csv
import random
import re
from pathlib import Path

RANDOM_SEED = 42
NUM_REPORTS = 100
SOURCE_CSV = Path(__file__).resolve().parents[1] / "data" / "godot_bug_reports.csv"
OUTPUT_CSV = Path(__file__).resolve().parents[1] / "data" / "godot_bug_reports_duplicates.csv"


def vary_text(text: str, variation_type: str) -> str:
    """Create lightweight textual variations while preserving meaning."""
    if not isinstance(text, str) or not text.strip():
        return text

    if variation_type == "typo":
        words = text.split()
        if words:
            idx = random.randint(0, len(words) - 1)
            if len(words[idx]) > 3:
                word = words[idx]
                pos = random.randint(1, len(word) - 2)
                words[idx] = word[:pos] + word[pos + 1] + word[pos] + word[pos + 2 :]
                return " ".join(words)
        return text

    if variation_type == "synonym":
        synonyms = {
            "fix": ["resolve", "repair", "correct"],
            "issue": ["problem", "bug", "defect"],
            "crash": ["freeze", "hang", "stop responding"],
            "error": ["failure", "bug", "issue"],
            "broken": ["not working", "faulty", "malfunctioning"],
            "missing": ["absent", "not present", "gone"],
            "update": ["upgrade", "change", "refresh"],
            "when": ["while", "if", "during"],
        }
        for original, replacements in synonyms.items():
            if re.search(rf"\b{re.escape(original)}\b", text, flags=re.IGNORECASE):
                replacement = random.choice(replacements)
                return re.sub(
                    rf"\b{re.escape(original)}\b",
                    replacement,
                    text,
                    count=1,
                    flags=re.IGNORECASE,
                )
        return text

    if variation_type == "restructure":
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        if len(sentences) > 1:
            head, tail = sentences[0], sentences[1:]
            random.shuffle(tail)
            return " ".join([head] + tail)
        return text

    if variation_type == "reword":
        prefixes = ["Bug report: ", "Issue observed: ", "Problem noted: "]
        if random.random() < 0.5:
            return random.choice(prefixes) + text[0].lower() + text[1:]
        return text

    return text


def make_description(title: str, body: str) -> str:
    """Create a short summary-style description from title/body."""
    body = body.strip()
    first_sentence = re.split(r"(?<=[.!?])\s+", body)[0] if body else ""
    candidate = first_sentence if first_sentence else title
    candidate = candidate.strip()
    if len(candidate) > 280:
        candidate = candidate[:277] + "..."
    return vary_text(candidate, random.choice(["synonym", "reword"]))


def generate_duplicate_row(source_row: dict, fake_id: int) -> dict:
    """Create one duplicate row plus mapping to original report ID."""
    original_title = source_row["title"]
    original_body = source_row["body"]

    new_title = vary_text(original_title, random.choice(["synonym", "reword", "typo"]))
    new_body = original_body
    for _ in range(random.randint(2, 4)):
        new_body = vary_text(new_body, random.choice(["synonym", "restructure", "reword", "typo"]))

    return {
        "id": fake_id,
        "title": new_title,
        "description": make_description(new_title, new_body),
        "body": new_body,
        "ground_truth_id": source_row["id"],
    }


def load_valid_reports(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))
    return [
        row
        for row in rows
        if row.get("id") and row.get("title", "").strip() and row.get("body", "").strip()
    ]


def main() -> None:
    random.seed(RANDOM_SEED)

    reports = load_valid_reports(SOURCE_CSV)
    if len(reports) < NUM_REPORTS:
        raise ValueError(f"Need at least {NUM_REPORTS} valid reports, found {len(reports)}.")

    sampled_reports = random.sample(reports, NUM_REPORTS)
    duplicates = []
    for i, source_row in enumerate(sampled_reports, start=200001):
        duplicates.append(generate_duplicate_row(source_row, fake_id=i))

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["id", "title", "description", "body", "ground_truth_id"]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(duplicates)

    print(f"Loaded {len(reports)} valid source reports from {SOURCE_CSV}")
    print(f"Sampled {NUM_REPORTS} originals and generated {len(duplicates)} duplicates")
    print(f"Saved duplicate dataset to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()