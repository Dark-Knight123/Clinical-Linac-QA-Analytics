CREATE TABLE machines (
    machine_id TEXT PRIMARY KEY,
    model TEXT,
    install_date DATE
);

CREATE TABLE daily_qa_logs (
    qa_date DATE,
    machine_id TEXT,
    laser_delta_mm REAL,
    odi_delta_mm REAL,
    photon_output_dev_pct REAL,
    passed_qa INTEGER
);
