from vector_model import VectorSpaceModel
from dummy_data import get_dummy_bug_reports, get_test_cases

reports = get_dummy_bug_reports()
tests = get_test_cases()

model = VectorSpaceModel(max_features=100)
model.build_model(reports, verbose=False)

threshold = 0.20
for t in tests:
    recs = model.find_similar(t, top_k=3, verbose=False)
    print(f"\nTest case #{t['id']}: {t['title']}")
    if not recs:
        print("  No similar reports found")
        continue
    top = recs[0]
    verdict = "DUPLICATE" if top['similarity'] >= threshold else "NOT DUPLICATE"
    print(f"  Top match: #{top['issue_id']} | score={top['similarity']:.3f} | {top['title']}")
    print(f"  Verdict (@{threshold:.2f}): {verdict}")
    print("  Top-3:")
    for r in recs:
        print(f"    - #{r['issue_id']} ({r['similarity']:.3f}) {r['title']}")
