import os
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
    cols = ["No long-covid", "Long-covid", "Rate per 100,000", "%"]
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
all_together.to_csv("output/counts_table.csv")

## Table with first covid codes
first_long_covid_code = crosstab(df["first_long_covid_code"])
first_long_covid_code = combined_codelists.join(first_long_covid_code)
first_long_covid_code.to_csv("output/first_long_covid_code.csv")
print(first_long_covid_code)

## All long-covid codes table
codes = [str(code) for code in combined_codelists.index]
df.columns = df.columns.str.lstrip("snomed_")
all_codes = df[codes].sum().T
all_codes = all_codes.rename("Total records")
all_codes.index = all_codes.index.astype("int64")
all_codes = combined_codelists.join(all_codes)
all_codes["%"] = (all_codes["Total records"] / all_codes["Total records"].sum()) * 100
all_codes.to_csv("output/all_long_covid_codes.csv")
print(all_codes)

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
