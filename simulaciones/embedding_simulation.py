#!/usr/bin/env python3
"""
Word Embedding Error Injection Experiment with Argentinean Provinces

Tests the hypothesis: "A word with a random error is semantically closer
to its original than other unrelated words are."

For each province:
1. Create an error version (typo)
2. Measure: distance(original, error)
3. Measure: distance(original, other_provinces)
4. Check: Is dist(original, error) < dist(original, other_province)?
"""

import os
import random
import string

import matplotlib.pyplot as plt
import numpy as np
import ollama
from scipy.spatial.distance import cosine


def get_embedding(word, model="embeddinggemma"):
    """Get embedding for a word using Ollama."""
    try:
        response = ollama.embeddings(model=model, prompt=word)
        return np.array(response["embedding"])
    except Exception as e:
        print(f"Error getting embedding for '{word}': {e}")
        return None


def inject_error(word):
    """
    Inject a random Damerau-Levenshtein error into a word.

    Operations: insertion, deletion, substitution, transposition
    """
    if not word:
        return word

    # Remove spaces and special chars for error injection, then restore
    clean_word = word.replace(" ", "").replace("-", "").lower()
    if not clean_word:
        return word

    error_type = random.choice(["insert", "delete", "substitute", "transpose"])

    if error_type == "insert":
        pos = random.randint(0, len(clean_word))
        char = random.choice(string.ascii_lowercase)
        modified = clean_word[:pos] + char + clean_word[pos:]

    elif error_type == "delete" and len(clean_word) > 1:
        pos = random.randint(0, len(clean_word) - 1)
        modified = clean_word[:pos] + clean_word[pos + 1 :]

    elif error_type == "substitute" and len(clean_word) > 0:
        pos = random.randint(0, len(clean_word) - 1)
        char = random.choice(string.ascii_lowercase)
        while char == clean_word[pos]:
            char = random.choice(string.ascii_lowercase)
        modified = clean_word[:pos] + char + clean_word[pos + 1 :]

    elif error_type == "transpose" and len(clean_word) > 1:
        pos = random.randint(0, len(clean_word) - 2)
        modified = (
            clean_word[:pos]
            + clean_word[pos + 1]
            + clean_word[pos]
            + clean_word[pos + 2 :]
        )

    else:
        # Fallback to substitution
        pos = random.randint(0, len(clean_word) - 1)
        char = random.choice(string.ascii_lowercase)
        while char == clean_word[pos]:
            char = random.choice(string.ascii_lowercase)
        modified = clean_word[:pos] + char + clean_word[pos + 1 :]

    return modified


def run_experiment(provinces, model="embeddinggemma"):
    """
    Run the error injection experiment.

    For each province:
    1. Create an error version (typo)
    2. Measure distance from original to error
    3. Measure distance from original to all other provinces
    4. Check if error is closer than other provinces

    Returns list of experiment results.
    """
    print("Getting embeddings for all provinces...")

    # Get all embeddings first
    embeddings = {}
    for province in provinces:
        emb = get_embedding(province, model)
        if emb is not None:
            embeddings[province] = emb

    results = []

    print("\nRunning experiments...")
    for target_province in provinces:
        if target_province not in embeddings:
            continue

        # Create error version
        error_province = inject_error(target_province)
        error_embedding = get_embedding(error_province, model)

        if error_embedding is None:
            continue

        print(f"  {target_province} -> {error_province}")

        # Measure distance from original to error
        dist_original_to_error = cosine(embeddings[target_province], error_embedding)

        # Get all other provinces
        other_provinces = [p for p in provinces if p != target_province]

        # Measure distance from original to each other province
        for other_province in other_provinces:
            if other_province not in embeddings:
                continue

            dist_original_to_other = cosine(
                embeddings[target_province], embeddings[other_province]
            )

            # Check if error is closer to original than this other province
            error_is_closer = dist_original_to_error < dist_original_to_other

            results.append(
                {
                    "target": target_province,
                    "error": error_province,
                    "other": other_province,
                    "dist_original_to_error": dist_original_to_error,
                    "dist_original_to_other": dist_original_to_other,
                    "error_is_closer": error_is_closer,
                }
            )

    return results


def analyze_and_plot(results, output_dir="simulaciones"):
    """Analyze results and create visualization."""

    if not results:
        print("No results to analyze!")
        return

    # Count successes (error is closer than other province)
    total = len(results)
    error_closer_count = sum(1 for r in results if r["error_is_closer"])
    success_rate = (error_closer_count / total) * 100

    # Print results
    print("\n" + "=" * 70)
    print("EXPERIMENT RESULTS - ARGENTINEAN PROVINCES")
    print("=" * 70)
    print(f"Total comparisons: {total}")
    print(f"Error word was closer to original: {error_closer_count} times")
    print(f"Other province was closer to original: {total - error_closer_count} times")
    print(f"Success rate: {success_rate:.1f}%")
    print("=" * 70)
    print("\nHypothesis: 'A province name with error is closer to its original than")
    print("            another province in the list is to that original'")
    print("=" * 70)

    # Print sample results
    print("\nSample comparisons (first 20):")
    print(
        f"{'Target':<25} {'Error':<15} {'Other':<25} {'Dist(Orig,Err)':<15} {'Dist(Orig,Other)':<15} {'Error Closer?'}"
    )
    print("-" * 100)
    for r in results[:20]:
        closer = "Yes" if r["error_is_closer"] else "No"
        print(
            f"{r['target']:<25} {r['error']:<15} {r['other']:<25} {r['dist_original_to_error']:<15.4f} {r['dist_original_to_other']:<15.4f} {closer}"
        )

    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Plot 1: Bar chart showing success vs failure
    if success_rate >= 50:
        colors = ["lightgreen", "lightcoral"]
        labels = ["Error Closer (Success)", "Other Closer (Failure)"]
    else:
        colors = ["lightcoral", "lightgreen"]
        labels = ["Error Closer", "Other Closer"]

    values = [error_closer_count, total - error_closer_count]

    bars1 = ax1.bar(labels, values, color=colors, edgecolor="black", linewidth=1.5)
    ax1.set_ylabel("Count", fontsize=12)
    ax1.set_title(
        f"Hypothesis Test Results\nSuccess Rate: {success_rate:.1f}%", fontsize=14
    )
    ax1.tick_params(axis="x", rotation=0)

    # Add value labels
    for bar, val in zip(bars1, values):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            str(val),
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    # Plot 2: Show distance comparison for each test
    n_comparisons = len(results)
    x = np.arange(n_comparisons)
    width = 0.35

    dist_to_error = [r["dist_original_to_error"] for r in results]
    dist_to_other = [r["dist_original_to_other"] for r in results]
    error_closer_flags = [r["error_is_closer"] for r in results]

    bars_error = ax2.bar(
        x - width / 2,
        dist_to_error,
        width,
        label="Distance to Error",
        color="orange",
        alpha=0.7,
    )
    bars_other = ax2.bar(
        x + width / 2,
        dist_to_other,
        width,
        label="Distance to Other Province",
        color="skyblue",
        alpha=0.7,
    )

    ax2.set_xlabel("Comparison Index", fontsize=12)
    ax2.set_ylabel("Cosine Distance", fontsize=12)
    ax2.set_title(
        f"Distance Comparison: Original→Error vs Original→Other\n"
        f"(Green = Error is closer, Red = Other is closer)",
        fontsize=12,
    )
    ax2.legend()

    # Add horizontal line for mean distances
    mean_error = np.mean(dist_to_error)
    mean_other = np.mean(dist_to_other)
    ax2.axhline(y=mean_error, color="orange", linestyle="--", linewidth=2, alpha=0.8)
    ax2.axhline(y=mean_other, color="skyblue", linestyle="--", linewidth=2, alpha=0.8)

    # Add text annotation for means
    ax2.text(
        0.98,
        0.95,
        f"Mean Dist to Error: {mean_error:.4f}\nMean Dist to Other: {mean_other:.4f}",
        transform=ax2.transAxes,
        fontsize=10,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    plt.tight_layout()

    # Save plot
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "provinces_error_injection_results.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"\nPlot saved to: {output_file}")
    plt.show()


def main():
    # Argentinean provinces list
    provinces = [
        "Buenos Aires",
        "Catamarca",
        "Chaco",
        "Chubut",
        "Córdoba",
        "Corrientes",
        "Entre Ríos",
        "Formosa",
        "Jujuy",
        "La Pampa",
        "La Rioja",
        "Mendoza",
        "Misiones",
        "Neuquén",
        "Río Negro",
        "Salta",
        "San Juan",
        "San Luis",
        "Santa Cruz",
        "Santa Fe",
        "Santiago del Estero",
        "Tierra del Fuego",
        "Tucumán",
    ]

    print("=" * 70)
    print("WORD EMBEDDING ERROR INJECTION EXPERIMENT")
    print("ARGENTINEAN PROVINCES")
    print("=" * 70)
    print(f"Provinces: {len(provinces)}")
    print(f"Model: embeddinggemma (via Ollama)")
    print("=" * 70)
    print("\nHypothesis: A province name with a random error is closer to its original")
    print("            than another province in the list is to that original.")
    print("=" * 70)

    # Run experiment
    results = run_experiment(provinces)

    if not results:
        print("No valid experiments completed.")
        return

    # Analyze and plot
    analyze_and_plot(results)


if __name__ == "__main__":
    main()
