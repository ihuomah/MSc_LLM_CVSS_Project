from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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

OUTPUT_FILE = OUTPUT_DIR / "figure_4_6_epss_correlation.png"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Project root : {PROJECT_ROOT}")
print(f"Reading      : {INPUT_FILE}")
print(f"Input exists : {INPUT_FILE.exists()}")

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")


df = pd.read_excel(INPUT_FILE, sheet_name="epss_correlation")

baseline_row = df[df["provider"] == "official_cvss"].iloc[0]
baseline_rho = baseline_row["spearman_rho"]

model_df = df[df["provider"] != "official_cvss"].copy()

provider_order = ["openai", "gemini", "ollama"]
condition_order = ["conventional", "structured"]

display_names = {
    "openai": "GPT-5.5",
    "gemini": "Gemini 2.5 Pro",
    "ollama": "Llama 3:8B",
}

plot_df = (
    model_df.pivot(
        index="provider",
        columns="condition",
        values="spearman_rho",
    )
    .loc[provider_order, condition_order]
)

models = [display_names[p] for p in provider_order]

x = np.arange(len(models))
bar_width = 0.35


plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9,
})

fig, ax = plt.subplots(figsize=(7.0, 4.6))

bars_conventional = ax.bar(
    x - bar_width / 2,
    plot_df["conventional"],
    bar_width,
    label="Conventional Prompt",
)

bars_structured = ax.bar(
    x + bar_width / 2,
    plot_df["structured"],
    bar_width,
    label="Structured Prompt",
)

ax.axhline(
    baseline_rho,
    linestyle="--",
    linewidth=1.5,
    color="black",
    label=f"Official CVSS–EPSS baseline (ρ = {baseline_rho:.3f})",
)

ax.set_ylabel("Spearman's Correlation (ρ)")
ax.set_xticks(x)
ax.set_xticklabels(models)

ax.set_ylim(0, 0.68)

ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.5)
ax.set_axisbelow(True)

ax.legend(loc="lower center",
    bbox_to_anchor=(0.5, 1.00),
    ncol=3,
    frameon=False,)

label_offset = ax.get_ylim()[1] * 0.015

for bars in [bars_conventional, bars_structured]:
    for bar in bars:
        height = bar.get_height()

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + label_offset,
            f"{height:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

plt.tight_layout(rect=[0, 0, 1, 0.92])

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print(f"Saved figure: {OUTPUT_FILE}")