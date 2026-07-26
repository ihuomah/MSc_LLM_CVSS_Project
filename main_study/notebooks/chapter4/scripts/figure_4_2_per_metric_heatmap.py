from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


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

OUTPUT_FILE = OUTPUT_DIR / "figure_4_2_per_metric_heatmap.png"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Project root : {PROJECT_ROOT}")
print(f"Reading      : {INPUT_FILE}")
print(f"Input exists : {INPUT_FILE.exists()}")

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")


# ------------------------------------------------------------
# Read validated results
# ------------------------------------------------------------
df = pd.read_excel(
    INPUT_FILE,
    sheet_name="metric_agreement"
)

# Use the all-attempted denominator
df = df[df["denominator_mode"] == "all_attempted"].copy()


# ------------------------------------------------------------
# Prepare heatmap data
# ------------------------------------------------------------
provider_order = ["openai", "gemini", "ollama"]
condition_order = ["conventional", "structured"]

display_names = {
    "openai": "GPT-5.5",
    "gemini": "Gemini 2.5 Pro",
    "ollama": "Llama 3:8B",
}

condition_names = {
    "conventional": "Conv",
    "structured": "Struct",
}

metric_columns = [
    ("AV", "AV_agreement_percent"),
    ("AC", "AC_agreement_percent"),
    ("PR", "PR_agreement_percent"),
    ("UI", "UI_agreement_percent"),
    ("S", "S_agreement_percent"),
    ("C", "C_agreement_percent"),
    ("I", "I_agreement_percent"),
    ("A", "A_agreement_percent"),
]

rows = []
row_labels = []

for provider in provider_order:
    for condition in condition_order:

        match = df[
            (df["provider"] == provider)
            & (df["condition"] == condition)
        ]

        if match.empty:
            raise ValueError(
                f"Missing row for provider={provider}, condition={condition}"
            )

        row = match.iloc[0]

        rows.append(
            [row[column] for _, column in metric_columns]
        )

        row_labels.append(
            f"{display_names[provider]}\n({condition_names[condition]})"
        )

heatmap = pd.DataFrame(
    rows,
    index=row_labels,
    columns=[metric for metric, _ in metric_columns],
)


# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})

fig, ax = plt.subplots(figsize=(9.5, 5.6))

image = ax.imshow(
    heatmap.values,
    cmap="Blues",
    vmin=0,
    vmax=100,
    aspect="auto",
)

# Major ticks
ax.set_xticks(range(len(heatmap.columns)))
ax.set_xticklabels(heatmap.columns)

ax.set_yticks(range(len(heatmap.index)))
ax.set_yticklabels(heatmap.index)

# ------------------------------------------------------------
# Add thin white gridlines between cells
# ------------------------------------------------------------
ax.set_xticks(
    [x - 0.5 for x in range(1, len(heatmap.columns))],
    minor=True
)

ax.set_yticks(
    [y - 0.5 for y in range(1, len(heatmap.index))],
    minor=True
)

ax.grid(
    which="minor",
    color="white",
    linestyle="-",
    linewidth=1
)

ax.tick_params(
    which="minor",
    bottom=False,
    left=False,
)

# ------------------------------------------------------------
# Annotate cells
# ------------------------------------------------------------
for i in range(heatmap.shape[0]):
    for j in range(heatmap.shape[1]):

        value = heatmap.iloc[i, j]

        text_colour = "white" if value >= 75 else "black"

        ax.text(
            j,
            i,
            f"{value:.1f}",
            ha="center",
            va="center",
            color=text_colour,
            fontsize=10,
            zorder=3,
        )

# ------------------------------------------------------------
# Colour bar
# ------------------------------------------------------------
cbar = fig.colorbar(
    image,
    ax=ax,
    fraction=0.04,
    pad=0.03,
)

cbar.set_label("Agreement (%)")

plt.tight_layout()

plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print(f"Saved figure: {OUTPUT_FILE}")