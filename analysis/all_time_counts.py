import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from common_variables import demographic_variables, clinical_variables

pd.set_option("display.max_rows", 50)
results_path = "output/practice_summ.txt"
stratifiers = list(demographic_variables.keys())
long_covid_codelists = [
    "opensafely-nice-managing-the-long-term-effects-of-covid-19",
    "opensafely-referral-and-signposting-for-long-covid",
    "opensafely-assessment-instruments-and-outcome-measures-for-long-covid",
]
combined_codelists = [
    pd.read_csv(f"codelists/{path}.csv", index_col="code")
    for path in long_covid_codelists
]
combined_codelists = pd.concat(combined_codelists)


def crosstab(idx):
    cols = ["No long COVID", "Long COVID", "Rate per 100,000", "%"]
    counts = pd.crosstab(idx, df["long_covid"], normalize=False, dropna=False)
    rates = (
        pd.crosstab(idx, df["long_covid"], normalize="index", dropna=False)[1] * 100000
    ).round(1)
    percentages = (
        pd.crosstab(idx, df["long_covid"], normalize="columns", dropna=False)[1] * 100
    ).round(1)
    all_cols = pd.concat([counts, rates, percentages], axis=1)
    all_cols.columns = cols
    return all_cols


def redact_small_numbers(df, column):
    mask = df[column].isin([1, 2, 3, 4, 5])
    df.loc[mask, :] = np.nan
    return df


def write_to_file(text_to_write, erase=False):
    if erase and os.path.isfile(results_path):
        os.remove(results_path)
    with open(results_path, "a") as txt:
        txt.writelines(f"{text_to_write}\n")
        print(text_to_write)
        txt.writelines("\n")
        print("\n")


df = pd.read_csv(
    "output/input_cohort.csv",
    index_col="patient_id",
    parse_dates=["first_long_covid_date"],
)

## Crosstabs
crosstabs = [crosstab(df[v]) for v in stratifiers]
all_together = pd.concat(
    crosstabs, axis=0, keys=stratifiers + ["imd"], names=["Attribute", "Category"]
)
print(all_together)
redact_small_numbers(all_together, "Long COVID").to_csv("output/counts_table.csv")

## All long-covid codes table
codes = [str(code) for code in combined_codelists.index]
df.columns = df.columns.str.lstrip("snomed_")
all_codes = df[codes].sum().T
all_codes = all_codes.rename("Total records")
all_codes.index = all_codes.index.astype("int64")
all_codes = combined_codelists.join(all_codes)
all_codes["%"] = (all_codes["Total records"] / all_codes["Total records"].sum()) * 100
redact_small_numbers(all_codes, "Total records").to_csv(
    "output/all_long_covid_codes.csv"
)
print(all_codes.columns)

## Descriptives by practice
by_practice = (
    df[["long_covid", "practice_id"]].groupby("practice_id").sum()["long_covid"]
)
write_to_file(f"Total patients coded: {by_practice.sum()}", erase=True)
top_10_count = by_practice.sort_values().tail(10).sum()
write_to_file(f"Patients coded in the highest 10 practices: {top_10_count}")
practice_summ = by_practice.describe()
write_to_file(f"Summary stats by practice:\n{practice_summ}")
ranges = [-1, 0, 1, 2, 3, 4, 5, 10, 10000]
practice_distribution = by_practice.groupby(pd.cut(by_practice, ranges)).count()
write_to_file(f"Distribution of coding within practices: {practice_distribution}")

## Counts over time graph
def line_format(label):
    """
    Convert time label to the format of pandas line plot
    """
    lab = label.month_name()[:3]
    if lab == "Jan":
        lab += f"\n{label.year}"
    if lab == "Feb" and label.year == 2019:
        lab = f"\n{label.year}"
    return lab


def generic_graph_settings():
    xlim = ax.get_xlim()
    ax.grid(b=False)
    ax.set_title(title, loc="left")
    ax.set_xlim(xlim)
    ax.set_ylim(ymin=0)
    ax.set_ylabel("Count of code use per week")
    plt.tight_layout()


monthly_counts = (
    df.set_index("first_long_covid_date")["long_covid"].resample("M").count()
)
monthly_counts.loc[monthly_counts.isin([1, 2, 3, 4, 5])] = np.nan
print(monthly_counts)
ax = monthly_counts.plot(kind="bar", width=1, zorder=0)
title = "Code use per week"
ax.set_xticklabels(map(line_format, monthly_counts.index), rotation="horizontal")
ax.xaxis.label.set_visible(False)
generic_graph_settings()
plt.savefig("output/code_use_per_week.svg")
plt.close()
