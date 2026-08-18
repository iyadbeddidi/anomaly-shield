import numpy as np
import pandas as pd

from pipeline import clean_chunk, run_pipeline


def test_clean_chunk_strips_and_drops():
    df = pd.DataFrame({
        ' Max Packet Length': [1.0, 2.0],
        ' Packet Length Variance': [0.0, np.inf],
    })
    cleaned = clean_chunk(df)
    assert 'Max Packet Length' in cleaned.columns
    assert len(cleaned) == 1


def test_run_pipeline_end_to_end(tmp_path, normal_flow, attack_flow):
    rows = pd.DataFrame([normal_flow, attack_flow])
    third = pd.DataFrame([normal_flow])
    third.loc[0, 'Packet Length Variance'] = np.inf
    rows = pd.concat([rows, third], ignore_index=True)

    csv_path = tmp_path / 'flows.csv'
    rows.to_csv(csv_path, index=False)

    out = tmp_path / 'out'
    summary = run_pipeline(str(csv_path), output_dir=str(out), chunksize=2)

    assert summary['total_flux'] == 2
    assert summary['alertes'] == 1
    assert (out / 'alerts.csv').exists()
