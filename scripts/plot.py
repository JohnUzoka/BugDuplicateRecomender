# plot.py

import matplotlib.pyplot as plt
from collections import Counter
from vector_model import VectorSpaceModel
from duplicate_test import reports, tests, test_ground_truth


def find_report_by_id(report_id):
    for report in reports:
        if report["id"] == report_id:
            return report
    return None


def evaluate_found_rate(top_k=10):
    model = VectorSpaceModel(max_features=5000)
    model.build_model(reports, verbose=False)

    found = 0
    not_found = 0

    for test_case in tests:
        case_id = test_case["id"]
        correct_id = test_ground_truth[case_id]

        recs = model.find_similar(test_case, top_k=top_k, verbose=False)

        found_match = any(r["issue_id"] == correct_id for r in recs)

        if found_match:
            found += 1
        else:
            not_found += 1

    total = found + not_found
    found_rate = found / total if total else 0

    print("\nFound Rate Summary")
    print("=" * 40)
    print(f"Total test cases: {total}")
    print(f"Found in top {top_k}: {found}")
    print(f"Not found in top {top_k}: {not_found}")
    print(f"Catch Rate: {found_rate:.3f}")

    return found, not_found, total


def plot_found_rate(top_k=10):
    found, not_found, total = evaluate_found_rate(top_k)

    labels = ["Found", "Not Found"]
    values = [found, not_found]
    percentages = [(v / total) * 100 if total else 0 for v in values]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values)

    plt.xlabel(f"Result in Top {top_k}")
    plt.ylabel("Number of Duplicate Reports")
    plt.title("Duplicate Catch Rate")


    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig("found_rate.png")
    plt.show()

    print("\nSaved graph to found_rate.png")


def get_top_duplicated_originals(top_n=10):
    original_counts = Counter(test_ground_truth.values())
    most_common = original_counts.most_common(top_n)

    labels = []
    counts = []

    print("\nTop Most Duplicated Original Bugs")
    print("=" * 40)

    for original_id, count in most_common:
        report = find_report_by_id(original_id)
        title = report["title"] if report else "[Missing Title]"
        short_label = f"{original_id}"
        labels.append(short_label)
        counts.append(count)

        print(f"#{original_id} | {count} duplicates | {title}")

    return labels, counts


def plot_top_duplicated_originals(top_n=10):
    labels, counts = get_top_duplicated_originals(top_n)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, counts)

    plt.xlabel("Original Bug ID")
    plt.ylabel("Number of Synthetic Duplicates")
    plt.title(f"Top {top_n} Most Duplicated Original Bugs")

    
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig("top_duplicated_originals.png")
    plt.show()

    print("\nSaved graph to top_duplicated_originals.png")


def main():
    plot_found_rate(top_k=10)
    plot_top_duplicated_originals(top_n=10)


if __name__ == "__main__":
    main()