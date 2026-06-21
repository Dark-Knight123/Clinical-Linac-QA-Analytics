import os
import glob
import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# =====================================================
# 1. EXTRACT + TRANSFORM
# =====================================================

def extract_and_transform(data_dir="data/raw_excel"):

    all_files = glob.glob(
        os.path.join(data_dir, "**", "*.xlsx"),
        recursive=True
    )

    if not all_files:
        raise FileNotFoundError(
            "No Excel files found in data/raw_excel/"
        )

    dfs = []

    for file in all_files:

        df = pd.read_excel(
            file,
            sheet_name="Daily_QA"
        )

        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    print(f"Loaded {len(df)} QA records")

    # ----------------------------
    # Data Cleaning
    # ----------------------------

    df["Date"] = pd.to_datetime(df["Date"])

    numeric_cols = [
        "Laser_Delta_mm",
        "ODI_Delta_mm",
        "Photon_Output_Dev_Pct"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df.drop_duplicates(inplace=True)

    df.dropna(inplace=True)

    # ----------------------------
    # TG-142 Pass / Fail Logic
    # ----------------------------

    df["passed_qa"] = np.where(
        (df["Laser_Delta_mm"].abs() <= 1.0)
        &
        (df["ODI_Delta_mm"].abs() <= 1.0)
        &
        (df["Photon_Output_Dev_Pct"].abs() <= 3.0),
        1,
        0
    )

    return df


# =====================================================
# 2. LOAD TO SQLITE
# =====================================================

def load_to_sqlite(df):

    conn = sqlite3.connect("linac_qa.db")

    df.to_sql(
        "daily_qa_logs",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print(
        f"Loaded {len(df)} records into SQLite database."
    )


# =====================================================
# 3. SUMMARY METRICS
# =====================================================

def create_summary_metrics(df):

    summary = (
        df.groupby("Machine_ID")
        .agg(
            Total_Checks=("Machine_ID", "count"),
            Passed_QA=("passed_qa", "sum"),
            Avg_Output_Deviation=(
                "Photon_Output_Dev_Pct",
                "mean"
            )
        )
        .reset_index()
    )

    summary["Compliance_Rate_%"] = (
        summary["Passed_QA"]
        /
        summary["Total_Checks"]
        * 100
    ).round(2)

    print("\n=== MACHINE SUMMARY ===")
    print(summary)

    return summary


# =====================================================
# 4. VISUALIZATION
# =====================================================

def generate_physics_plots(df):

    os.makedirs("outputs", exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid")

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(14, 10)
    )

    # -----------------------------------
    # Plot 1
    # Photon Output Drift
    # -----------------------------------

    for machine in df["Machine_ID"].unique():

        machine_df = (
            df[df["Machine_ID"] == machine]
            .sort_values("Date")
        )

        ax1.plot(
            machine_df["Date"],
            machine_df["Photon_Output_Dev_Pct"],
            label=machine
        )

    ax1.axhline(
        3,
        linestyle="--",
        alpha=0.8
    )

    ax1.axhline(
        -3,
        linestyle="--",
        alpha=0.8
    )

    ax1.set_title(
        "Photon Output Constancy Monitoring"
    )

    ax1.set_ylabel(
        "Output Deviation (%)"
    )

    ax1.legend()

    # -----------------------------------
    # Plot 2
    # Laser Variability
    # -----------------------------------

    sns.boxplot(
        data=df,
        x="Machine_ID",
        y="Laser_Delta_mm",
        ax=ax2
    )

    ax2.axhline(
        1.0,
        linestyle="--",
        alpha=0.8
    )

    ax2.set_title(
        "Laser Alignment Distribution"
    )

    ax2.set_ylabel(
        "Laser Delta (mm)"
    )

    plt.tight_layout()

    plt.savefig(
        "outputs/linac_qa_trends.png",
        dpi=300
    )

    plt.close()

    print(
        "Saved outputs/linac_qa_trends.png"
    )


# =====================================================
# 5. MONTHLY COMPLIANCE REPORT
# =====================================================

def generate_monthly_report(df):

    df["Month"] = (
        df["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    report = (
        df.groupby(
            ["Month", "Machine_ID"]
        )
        .agg(
            Total_Days=("passed_qa", "count"),
            Days_Passed=("passed_qa", "sum")
        )
        .reset_index()
    )

    report["Compliance_Rate_%"] = (
        report["Days_Passed"]
        /
        report["Total_Days"]
        * 100
    ).round(2)

    report.to_csv(
        "outputs/monthly_compliance_report.csv",
        index=False
    )

    print(
        "Saved outputs/monthly_compliance_report.csv"
    )

    return report


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print(
        "\n=== LINAC QA ANALYTICS PIPELINE ===\n"
    )

    df = extract_and_transform()

    load_to_sqlite(df)

    summary = create_summary_metrics(df)

    monthly_report = generate_monthly_report(df)

    generate_physics_plots(df)

    print("\nPipeline completed successfully.")

    