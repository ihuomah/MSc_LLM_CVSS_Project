from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# Locate project root automatically
# ------------------------------------------------------------

def find_project_root(marker="main_study"):
    current_file = Path(__file__).resolve()

    for parent in current_file.parents:
        if (parent / marker).is_dir():
            return parent

    raise FileNotFoundError(
        f"Could not locate project root containing '{marker}/'"
    )


PROJECT_ROOT = find_project_root()

INPUT_FILE = (
    PROJECT_ROOT
    / "main_study"
    / "results"
    / "analysis"
    / "accuracy"
    / "main_accuracy_summary.xlsx"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "main_study"
    / "notebooks"
    / "chapter4"
    / "figures"
)

OUTPUT_FILE = OUTPUT_DIR / "figure_4_5_condition_flip_analysis.png"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Project root : {PROJECT_ROOT}")
print(f"Reading      : {INPUT_FILE}")
print(f"Input exists : {INPUT_FILE.exists()}")

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")


# ------------------------------------------------------------
# Load validated results
# ------------------------------------------------------------

df = pd.read_excel(INPUT_FILE, sheet_name="condition_flips")


# ------------------------------------------------------------
# Prepare plotting data
# ------------------------------------------------------------

metric_order = ["AV", "AC", "PR", "UI", "S", "C", "I", "A"]
provider_order = ["openai", "gemini", "ollama"]

display_names = {
    "openai": "GPT-5.5",
    "gemini": "Gemini 2.5 Pro",
    "ollama": "Llama 3:8B",
}

plot_df = (
    df.pivot(
        index="metric",
        columns="provider",
        values="flip_rate_percent",
    )
    .loc[metric_order, provider_order]
)

x = np.arange(len(metric_order))
bar_width = 0.25


# ------------------------------------------------------------
# Plot figure
# ------------------------------------------------------------

plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
})

fig, ax = plt.subplots(figsize=(9.5, 4.8))

bars = {}

bars["openai"] = ax.bar(
    x - bar_width,
    plot_df["openai"],
    bar_width,
    label=display_names["openai"],
)

bars["gemini"] = ax.bar(
    x,
    plot_df["gemini"],
    bar_width,
    label=display_names["gemini"],
)

bars["ollama"] = ax.bar(
    x + bar_width,
    plot_df["ollama"],
    bar_width,
    label=display_names["ollama"],
)

ax.set_xlabel("CVSS Base Metric")
ax.set_ylabel("Condition Flip Rate (%)")

ax.set_xticks(x)
ax.set_xticklabels(metric_order)

ax.set_ylim(0, 55)

ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.5)
ax.set_axisbelow(True)

ax.legend(loc="upper left", frameon=False)


# ------------------------------------------------------------
# Add value labels
# ------------------------------------------------------------

label_offset = ax.get_ylim()[1] * 0.012

for provider in provider_order:
    for bar in bars[provider]:
        height = bar.get_height()

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + label_offset,
            f"{height:.1f}",
            ha="center",
            va="bottom",
            fontsize=8,
            rotation=0,
        )


plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print(f"Saved figure: {OUTPUT_FILE}")