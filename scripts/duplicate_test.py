import csv
import os
from vector_model import VectorSpaceModel

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

REPORTS_CSV = os.path.join(DATA_DIR, "godot_bug_reports.csv")
DEFAULT_DUPLICATES_CSV = os.path.join(DATA_DIR, "godot_bug_reports_duplicates.csv")
LEGACY_DUPLICATES_CSV = os.path.join(DATA_DIR, "duplicate_bug_reports.csv")


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


if os.path.exists(DEFAULT_DUPLICATES_CSV):
    duplicates_csv = DEFAULT_DUPLICATES_CSV
elif os.path.exists(LEGACY_DUPLICATES_CSV):
    duplicates_csv = LEGACY_DUPLICATES_CSV
else:
    raise FileNotFoundError(
        "No duplicates CSV found. Expected one of: "
        f"{DEFAULT_DUPLICATES_CSV} or {LEGACY_DUPLICATES_CSV}"
    )

reports = load_csv(REPORTS_CSV)
tests = load_csv(duplicates_csv)

for r in reports:
    r["id"] = int(r["id"])
for t in tests:
    t["id"] = int(t["id"])
    t["ground_truth_id"] = int(t["ground_truth_id"])

test_ground_truth = {t["id"]: t["ground_truth_id"] for t in tests}

print(f"Loaded {len(reports)} original reports, {len(tests)} duplicate test cases\n")

model = VectorSpaceModel(max_features=5000)
model.build_model(reports, verbose=False)

threshold = 0.20
top_k = 10

top_scores_by_case = {}

for t in tests:
    recs = model.find_similar(t, top_k=top_k, verbose=False)
    print(f"\nTest case #{t['id']}: {t['title']}")
    if not recs:
        print("  No similar reports found")
        top_scores_by_case[t['id']] = 0.0
        continue
    top = recs[0]
    top_scores_by_case[t['id']] = top['similarity']
    verdict = "DUPLICATE" if top['similarity'] >= threshold else "NOT DUPLICATE"
    print(f"  Top match: #{top['issue_id']} | score={top['similarity']:.3f} | {top['title']}")
    print(f"  Verdict (@{threshold:.2f}): {verdict}")
    print("  All suggestions (highest similarity first):")
    for rank, r in enumerate(recs, start=1):
        print(f"    {rank:>2}. #{r['issue_id']} | score={r['similarity']:.3f} | {r['title']}")

print("\n" + "=" * 72)
print("Precision/Recall vs Threshold")
print("=" * 72)
print("Threshold | Precision | Recall | F1    | TP FP FN TN")
print("-" * 72)

for t in range(0, 21):
    current_threshold = t * 0.05
    tp = fp = fn = tn = 0

    for case in tests:
        case_id = case['id']
        actual_duplicate = test_ground_truth.get(case_id) is not None
        predicted_duplicate = top_scores_by_case.get(case_id, 0.0) >= current_threshold

        if predicted_duplicate and actual_duplicate:
            tp += 1
        elif predicted_duplicate and not actual_duplicate:
            fp += 1
        elif not predicted_duplicate and actual_duplicate:
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    print(
        f"{current_threshold:8.2f} | {precision:9.3f} | {recall:6.3f} | {f1:5.3f} |"
        f" {tp:>2} {fp:>2} {fn:>2} {tn:>2}"
    )
