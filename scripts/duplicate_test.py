from vector_model import VectorSpaceModel
from dummy_data import (
    get_dummy_bug_reports,
    get_test_cases,
    get_test_case_ground_truth,
)

reports = get_dummy_bug_reports()
tests = get_test_cases()

model = VectorSpaceModel(max_features=100)
model.build_model(reports, verbose=False)

threshold = 0.20
top_k = len(reports)

test_ground_truth = get_test_case_ground_truth()

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
