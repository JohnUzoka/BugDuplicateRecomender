import matplotlib.pyplot as plt
from vector_model import VectorSpaceModel
from duplicate_test import reports, tests, test_ground_truth


def evaluate_correct_original_found(model, top_k=10):
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
    return found, not_found, total


def average_similarity_for_k(model, k):
    per_case_averages = []

    for test_case in tests:
        recs = model.find_similar(test_case, top_k=k, verbose=False)

        if not recs:
            per_case_averages.append(0.0)
            continue

        scores = [r["similarity"] for r in recs[:k]]
        per_case_averages.append(sum(scores) / len(scores))

    if not per_case_averages:
        return 0.0

    return sum(per_case_averages) / len(per_case_averages)


def plot_correct_original_found(model, top_k=10):
    found, not_found, total = evaluate_correct_original_found(model, top_k)

    labels = ["Correct Original Found", "Correct Original Not Found"]
    values = [found, not_found]
    percentages = [(v / total) * 100 if total else 0 for v in values]

    print("\nCorrect Original Found Summary")
    print("=" * 40)
    print(f"Total test cases: {total}")
    print(f"Correct original found in top {top_k}: {found}")
    print(f"Correct original not found in top {top_k}: {not_found}")
    print(f"Top-{top_k} retrieval rate: {found / total:.3f}" if total else f"Top-{top_k} retrieval rate: 0.000")

    plt.figure(figsize=(9, 5))
    bars = plt.bar(labels, values)

    plt.xlabel(f"Result in Top {top_k}")
    plt.ylabel("Number of Duplicate Reports")
    plt.title(f"Correct Original Retrieval in Top {top_k}")

    for i, bar in enumerate(bars):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{values[i]} ({percentages[i]:.1f}%)",
            ha="center"
        )

    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig("found_rate.png")
    plt.show()

    print("Saved graph to found_rate.png")


def plot_average_similarity(model):
    k_values = [3, 5, 10]
    avg_scores = []

    print("\nAverage Similarity by Top-K")
    print("=" * 40)

    for k in k_values:
        avg = average_similarity_for_k(model, k)
        avg_scores.append(avg)
        print(f"Top {k}: {avg:.3f}")

    plt.figure(figsize=(8, 5))
    bars = plt.bar([str(k) for k in k_values], avg_scores)

    plt.xlabel("Top-K Recommendations")
    plt.ylabel("Average Similarity Score")
    plt.title("Average Similarity Score by Top-K")
    plt.ylim(0, 1)

    for bar, score in zip(bars, avg_scores):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{score:.3f}",
            ha="center"
        )

    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig("average_similarity_by_k.png")
    plt.show()

    print("Saved graph to average_similarity_by_k.png")


def main():
    model = VectorSpaceModel(max_features=5000)
    model.build_model(reports, verbose=False)

    plot_correct_original_found(model, top_k=10)
    plot_average_similarity(model)


if __name__ == "__main__":
    main()