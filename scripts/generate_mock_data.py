import os
import pandas as pd
import numpy as np

# Reproducible results
np.random.seed(42)

# Monthly folders required by project
months = [
    "2025-07",
    "2025-08",
    "2025-09",
    "2025-10",
    "2025-11",
    "2025-12",
    "2026-01",
    "2026-02",
    "2026-03",
    "2026-04",
    "2026-05",
    "2026-06"
]

machines = ["Linac_A", "Linac_B", "Linac_C"]

therapists = ["FY", "AB", "CD", "EF"]

for month in months:

    start_date = f"{month}-01"

    dates = pd.date_range(
        start=start_date,
        periods=pd.Period(month).days_in_month,
        freq="D"
    )

    folder_path = f"data/raw_excel/{month}_QA"

    os.makedirs(folder_path, exist_ok=True)

    for machine in machines:

        laser = np.round(
            np.random.normal(0.4, 0.2, len(dates)),
            2
        )

        odi = np.round(
            np.random.normal(0.5, 0.2, len(dates)),
            2
        )

        photon = np.round(
            np.random.normal(0.0, 1.0, len(dates)),
            2
        )

        # Inject occasional QA failures
        for i in range(len(dates)):

            if np.random.random() < 0.03:
                laser[i] = np.round(
                    np.random.uniform(1.1, 1.5),
                    2
                )

            if np.random.random() < 0.03:
                odi[i] = np.round(
                    np.random.uniform(1.1, 1.5),
                    2
                )

            if np.random.random() < 0.03:
                photon[i] = np.round(
                    np.random.uniform(3.1, 4.5),
                    2
                )

        df = pd.DataFrame({
            "Date": dates,
            "Machine_ID": machine,
            "Laser_Delta_mm": laser,
            "ODI_Delta_mm": odi,
            "Photon_Output_Dev_Pct": photon,
            "Performed_By": np.random.choice(
                therapists,
                len(dates)
            )
        })

        file_path = (
            f"{folder_path}/"
            f"{machine}_DailyQA.xlsx"
        )

        df.to_excel(
            file_path,
            sheet_name="Daily_QA",
            index=False
        )

print("Successfully generated 12 months of QA data.")
print("Total Excel files created: 36")
