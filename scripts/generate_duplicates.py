"""
Generate 100 duplicate bug reports from godot_bug_reports.csv.

Each duplicate is a textual paraphrase of an original report, designed to be
detectable by an NLP duplicate-detection system.  Output columns:

    title, description, body, ground_truth_id
"""

import csv
import random
import re
import textwrap

random.seed(42)

SRC_CSV = "data/godot_bug_reports.csv"
DST_CSV = "data/duplicate_bug_reports.csv"
NUM_DUPLICATES = 100

# ---------------------------------------------------------------------------
# Synonym / phrase substitution tables
# ---------------------------------------------------------------------------
SYNONYM_MAP = {
    "crash": ["freeze", "hang", "stop responding", "terminate unexpectedly"],
    "crashes": ["freezes", "hangs", "stops responding", "terminates unexpectedly"],
    "bug": ["defect", "issue", "problem", "flaw"],
    "fix": ["resolve", "patch", "correct", "address"],
    "error": ["fault", "failure", "exception", "mistake"],
    "broken": ["not working", "malfunctioning", "faulty", "defective"],
    "incorrect": ["wrong", "invalid", "inaccurate", "erroneous"],
    "missing": ["absent", "not present", "unavailable", "lacking"],
    "issue": ["problem", "defect", "bug", "glitch"],
    "causes": ["leads to", "results in", "triggers", "produces"],
    "when": ["while", "during", "upon", "if"],
    "fails": ["does not work", "breaks", "stops working", "errors out"],
    "display": ["render", "show", "present", "draw"],
    "remove": ["delete", "strip", "eliminate", "drop"],
    "add": ["include", "introduce", "insert", "append"],
    "loading": ["importing", "reading", "opening", "fetching"],
    "save": ["write", "store", "persist", "export"],
    "project": ["workspace", "project files", "project directory"],
    "editor": ["IDE", "Godot editor", "development environment"],
    "scene": ["level", "scene file", "scene tree"],
    "node": ["element", "object", "scene node"],
    "resource": ["asset", "file resource", "data resource"],
    "running": ["executing", "in progress", "active"],
    "window": ["viewport", "application window", "display window"],
    "mouse": ["cursor", "pointer", "mouse input"],
    "keyboard": ["key input", "keyboard input", "keypress"],
    "click": ["press", "tap", "select"],
    "button": ["control", "UI button", "widget"],
    "menu": ["dropdown", "context menu", "popup menu"],
    "rendering": ["drawing", "displaying", "painting"],
    "texture": ["image", "bitmap", "graphic"],
    "shader": ["GPU shader", "shader program", "material shader"],
    "animation": ["anim", "animated sequence", "motion"],
    "script": ["code", "GDScript", "source file"],
    "function": ["method", "routine", "procedure"],
    "variable": ["parameter", "field", "property"],
    "memory": ["RAM", "heap memory", "allocated memory"],
    "performance": ["speed", "efficiency", "frame rate"],
    "reproducible": ["can be reproduced", "consistently occurs", "reliably triggered"],
    "sometimes": ["intermittently", "occasionally", "sporadically", "once in a while"],
    "always": ["every time", "consistently", "without fail"],
    "regression": ["newly introduced bug", "recent breakage", "regression issue"],
    "workaround": ["temporary fix", "interim solution", "hack"],
}

TITLE_PREFIXES = [
    "", "Bug: ", "Issue: ", "[Bug] ", "Problem: ", "Defect - ",
    "Report: ", "", "", "",
]

BODY_INTROS = [
    "I've encountered a problem where ",
    "There appears to be an issue: ",
    "I noticed that ",
    "After updating, I found that ",
    "While working on my project, ",
    "I ran into a situation where ",
    "This might be a regression — ",
    "Not sure if this is known, but ",
    "Reporting a potential bug: ",
    "Hey, I think I found something: ",
    "",
]

BODY_OUTROS = [
    "",
    " Any help would be appreciated.",
    " Please look into this.",
    " Let me know if you need more info.",
    " Happy to provide a minimal reproduction project.",
    " This is blocking my workflow.",
    " I can reproduce this consistently.",
    " Steps above should be enough to trigger it.",
    " Tested on the latest stable release.",
]

SYSTEM_INFOS = [
    "",
    " (Tested on Windows 11, Vulkan renderer, RTX 3070)",
    " (macOS Sequoia, Metal backend, M2 chip)",
    " (Ubuntu 24.04, Vulkan Forward+, GTX 1080)",
    " (Fedora 42, OpenGL Compatibility, integrated GPU)",
    " (Windows 10, Direct3D 12, Ryzen 7)",
    " (Arch Linux, Wayland, RTX 3060)",
]


# ---------------------------------------------------------------------------
# Text-transformation helpers
# ---------------------------------------------------------------------------

def _synonym_replace(text: str, intensity: float = 0.3) -> str:
    """Replace some words with synonyms from the map."""
    words = text.split()
    out = []
    for w in words:
        key = w.lower().strip(".,;:!?()[]\"'")
        if key in SYNONYM_MAP and random.random() < intensity:
            replacement = random.choice(SYNONYM_MAP[key])
            if w[0].isupper():
                replacement = replacement.capitalize()
            out.append(replacement)
        else:
            out.append(w)
    return " ".join(out)


def _shuffle_sentences(text: str) -> str:
    """Lightly shuffle sentence order (keep first sentence in place)."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) <= 2:
        return text
    first = sentences[0]
    rest = sentences[1:]
    random.shuffle(rest)
    return " ".join([first] + rest)


def _drop_sentences(text: str, drop_prob: float = 0.2) -> str:
    """Randomly drop some sentences to simulate partial reports."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) <= 2:
        return text
    kept = [s for s in sentences if random.random() > drop_prob]
    if not kept:
        kept = [sentences[0]]
    return " ".join(kept)


def _insert_filler(text: str) -> str:
    """Occasionally insert filler phrases."""
    fillers = [
        "basically", "essentially", "it seems like", "I think",
        "apparently", "for some reason", "interestingly",
    ]
    sentences = re.split(r'(?<=[.!?])\s+', text)
    out = []
    for s in sentences:
        if random.random() < 0.15 and len(s) > 20:
            pos = random.randint(0, max(0, len(s.split()) - 1))
            words = s.split()
            words.insert(pos, random.choice(fillers))
            s = " ".join(words)
        out.append(s)
    return " ".join(out)


def _paraphrase(text: str) -> str:
    """Apply a pipeline of lightweight transformations."""
    text = _synonym_replace(text, intensity=random.uniform(0.15, 0.40))
    if random.random() < 0.4:
        text = _shuffle_sentences(text)
    if random.random() < 0.3:
        text = _drop_sentences(text, drop_prob=0.15)
    if random.random() < 0.35:
        text = _insert_filler(text)
    return text


def _make_description(title: str, body: str) -> str:
    """Produce a short 1-2 sentence description (summary) from the original."""
    first_sentence = re.split(r'(?<=[.!?])\s+', body.strip())
    desc = first_sentence[0] if first_sentence else body[:200]
    if len(desc) > 300:
        desc = desc[:297] + "..."
    return _synonym_replace(desc, intensity=0.2)


def _make_title(original_title: str) -> str:
    """Generate a paraphrased title."""
    prefix = random.choice(TITLE_PREFIXES)
    new_title = _synonym_replace(original_title, intensity=random.uniform(0.2, 0.5))
    return prefix + new_title


def _make_body(original_body: str) -> str:
    """Generate a paraphrased body."""
    intro = random.choice(BODY_INTROS)
    outro = random.choice(BODY_OUTROS)
    sys_info = random.choice(SYSTEM_INFOS)

    body = _paraphrase(original_body)

    if intro:
        first_char = body[0].lower() if body else ""
        body = intro + first_char + body[1:]

    body = body.rstrip() + sys_info + outro
    return body


# ---------------------------------------------------------------------------
# Main generation logic
# ---------------------------------------------------------------------------

def load_originals(path: str):
    """Load original bug reports from CSV, return list of dicts."""
    reports = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("title") and row.get("body") and len(row["body"].strip()) > 50:
                reports.append(row)
    return reports


def generate_duplicates(originals, n: int = 100):
    """Generate *n* duplicate reports sampled from *originals*."""
    duplicates = []
    sources = random.choices(originals, k=n)

    for i, src in enumerate(sources, start=200001):
        dup = {
            "id": i,
            "title": _make_title(src["title"]),
            "description": _make_description(src["title"], src["body"]),
            "body": _make_body(src["body"]),
            "ground_truth_id": src["id"],
        }
        duplicates.append(dup)

    return duplicates


def write_csv(duplicates, path: str):
    fieldnames = ["id", "title", "description", "body", "ground_truth_id"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(duplicates)


def main():
    originals = load_originals(SRC_CSV)
    print(f"Loaded {len(originals)} original bug reports.")

    duplicates = generate_duplicates(originals, NUM_DUPLICATES)
    write_csv(duplicates, DST_CSV)

    print(f"Wrote {len(duplicates)} duplicate reports to {DST_CSV}")

    ids_used = {d["ground_truth_id"] for d in duplicates}
    print(f"Duplicates drawn from {len(ids_used)} unique originals.")


if __name__ == "__main__":
    main()
