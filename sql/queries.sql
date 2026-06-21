-- machines with largest output drift

SELECT
    machine_id,
    COUNT(*) AS near_tolerance_incidents,
    ROUND(
        AVG(
            ABS(photon_output_dev_pct)
        ),
        3
    ) AS avg_absolute_deviation
FROM daily_qa_logs
WHERE ABS(photon_output_dev_pct) > 2
GROUP BY machine_id
ORDER BY near_tolerance_incidents DESC;


-- monthly compliance

SELECT
    substr(qa_date,1,7) AS qa_month,
    machine_id,
    COUNT(*) AS total_days_checked,
    SUM(passed_qa) AS days_passed,
    ROUND(
        100.0 *
        SUM(passed_qa)
        /
        COUNT(*),
        2
    ) AS compliance_rate_pct
FROM daily_qa_logs
GROUP BY qa_month, machine_id;
