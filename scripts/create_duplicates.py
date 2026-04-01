import csv
import random
import re
from pathlib import Path

RANDOM_SEED = 42
NUM_REPORTS = 100
SOURCE_CSV = Path(__file__).resolve().parents[1] / "data" / "godot_bug_reports.csv"
OUTPUT_CSV = Path(__file__).resolve().parents[1] / "data" / "godot_duplicate_bug_reports.csv"

SYNONYM_MAP = {
    "fix": ["resolve", "address", "patch", "remedy"],
    "issue": ["problem", "defect", "fault", "failure case"],
    "crash": ["terminate unexpectedly", "close abruptly", "hard-stop", "shut down"],
    "error": ["failure", "unexpected behavior", "fault", "incorrect behavior"],
    "broken": ["not working", "malfunctioning", "failing", "in a bad state"],
    "missing": ["absent", "not present", "gone", "unavailable"],
    "update": ["change", "upgrade", "refresh", "modify"],
    "when": ["while", "during", "after", "as soon as"],
    "always": ["consistently", "every time", "on each attempt"],
    "sometimes": ["intermittently", "occasionally", "on some runs"],
    "button": ["control", "UI button", "action control", "toolbar button"],
    "window": ["editor window", "panel", "application window", "view"],
    "scene": ["project scene", "loaded scene", "active scene graph", "level scene"],
    "project": ["workspace", "project setup", "current project", "working project"],
    "save": ["store", "persist", "write to disk", "save out"],
    "load": ["open", "read in", "import", "reload"],
    "fails": ["does not complete", "breaks", "stops working", "returns unsuccessfully"],
    "slow": ["laggy", "delayed", "sluggish", "noticeably slow"],
}

PERSPECTIVE_OPENERS = [
    "From my side, this appears during regular editor use.",
    "Observed while validating a normal workflow on my machine.",
    "I ran into this while reproducing the same sequence multiple times.",
    "In day-to-day usage, this behavior is easy to trigger.",
]

IMPACT_LINES = [
    "This blocks progress because the expected result never appears.",
    "The behavior interrupts the workflow and forces a restart.",
    "The result is inconsistent with what the editor UI suggests.",
    "This makes the feature unreliable for practical use.",
]

REPRO_PREFIXES = [
    "Repro pattern:",
    "How this shows up:",
    "What I can reproduce:",
    "Observed sequence:",
]

TITLE_PREFIXES = [
    "Regression:",
    "Observed behavior:",
    "Unexpected result:",
    "Workflow failure:",
]


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
        return apply_synonym_swaps(text, max_swaps=random.randint(3, 8))

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


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def clean_sentence(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if text and text[-1] not in ".!?":
        text += "."
    return text


def apply_synonym_swaps(text: str, max_swaps: int = 5) -> str:
    """Replace multiple domain terms to make wording substantially different."""
    updated = text
    keys = list(SYNONYM_MAP.keys())
    random.shuffle(keys)
    swaps = 0

    for original in keys:
        if swaps >= max_swaps:
            break
        pattern = rf"\b{re.escape(original)}\b"
        if re.search(pattern, updated, flags=re.IGNORECASE):
            replacement = random.choice(SYNONYM_MAP[original])
            updated = re.sub(pattern, replacement, updated, count=1, flags=re.IGNORECASE)
            swaps += 1

    return clean_sentence(updated)


def perspective_rewrite(title: str, body: str) -> str:
    """Rewrite bug body from a different perspective and structure."""
    source = body.strip() if body.strip() else title.strip()
    sentences = split_sentences(source)
    if not sentences:
        sentences = [clean_sentence(source)]

    primary = apply_synonym_swaps(random.choice(sentences), max_swaps=random.randint(4, 9))
    detail_pool = [s for s in sentences if s != primary]
    detail_sentence = (
        apply_synonym_swaps(random.choice(detail_pool), max_swaps=random.randint(2, 5))
        if detail_pool
        else apply_synonym_swaps(title, max_swaps=random.randint(2, 4))
    )

    parts = [
        random.choice(PERSPECTIVE_OPENERS),
        f"{random.choice(REPRO_PREFIXES)} {primary}",
        f"Additional detail: {detail_sentence}",
        random.choice(IMPACT_LINES),
    ]

    rewritten = " ".join(clean_sentence(p) for p in parts if p.strip())
    return clean_sentence(re.sub(r"\s+", " ", rewritten))


def perspective_title(original_title: str, rewritten_body: str) -> str:
    candidates = split_sentences(rewritten_body)
    stem = candidates[1] if len(candidates) > 1 else candidates[0] if candidates else original_title
    stem = re.sub(r"^(Repro pattern:|How this shows up:|What I can reproduce:|Observed sequence:)\s*", "", stem)
    stem = stem.strip()
    if len(stem) > 90:
        stem = stem[:87].rstrip() + "..."
    return f"{random.choice(TITLE_PREFIXES)} {stem}"


def make_description(title: str, body: str) -> str:
    """Create a short summary-style description from title/body."""
    body = body.strip()
    first_sentence = split_sentences(body)[0] if body else ""
    candidate = first_sentence if first_sentence else title
    candidate = candidate.strip()
    if len(candidate) > 280:
        candidate = candidate[:277] + "..."
    return apply_synonym_swaps(candidate, max_swaps=random.randint(3, 6))


def generate_duplicate_row(source_row: dict, fake_id: int) -> dict:
    """Create one duplicate row plus mapping to original report ID."""
    original_title = source_row["title"]
    original_body = source_row["body"]

    new_body = perspective_rewrite(original_title, original_body)
    new_title = perspective_title(original_title, new_body)

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