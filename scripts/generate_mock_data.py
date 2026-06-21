import pandas as pd
import numpy as np

dates = pd.date_range("2026-01-01", "2026-01-31")

for machine in ["Linac_A", "Linac_B", "Linac_C"]:

    df = pd.DataFrame({
        "Date": dates,
        "Machine_ID": machine,
        "Laser_Delta_mm": np.round(np.random.normal(0.4,0.2,len(dates)),2),
        "ODI_Delta_mm": np.round(np.random.normal(0.5,0.2,len(dates)),2),
        "Photon_Output_Dev_Pct": np.round(np.random.normal(0.0,1.0,len(dates)),2),
        "Performed_By": np.random.choice(["FY","AB","CD"],len(dates))
    })

    df.to_excel(
        f"../data/January/{machine}_DailyQA.xlsx",
        sheet_name="Daily_QA",
        index=False
    )

print("Files created successfully.")
