import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from predict import AnomalyShield
from alerting import AlertManager


def clean_chunk(chunk):
    chunk = chunk.rename(columns=lambda c: c.strip())
    chunk = chunk.replace([np.inf, -np.inf], np.nan)
    return chunk.dropna()


def run_pipeline(input_csv, output_dir='output', threshold=0.5, chunksize=50000, nrows=None):
    model = AnomalyShield()
    alerting = AlertManager(threshold=threshold)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    total_alerts = 0
    alert_rows = []

    reader = pd.read_csv(input_csv, low_memory=False, chunksize=chunksize, nrows=nrows)

    for chunk in reader:
        chunk = clean_chunk(chunk)
        if chunk.empty:
            continue

        results = model.predict(chunk)
        if isinstance(results, dict):
            results = [results]

        alerting.process(results)

        for i, r in zip(chunk.index, results):
            if r['prediction'] == 1:
                total_alerts += 1
                alert_rows.append({'index': int(i), 'score': r['score']})

        total += len(results)
        print(f'[pipeline] {total} flux traites, {total_alerts} alertes (cumule)')

    if alert_rows:
        pd.DataFrame(alert_rows).to_csv(output_dir / 'alerts.csv', index=False)

    summary = {
        'total_flux': total,
        'alertes': total_alerts,
        'taux_alerte': total_alerts / total if total else 0.0,
        'output_dir': str(output_dir),
    }
    print('\n=== Resume ===')
    print(f"Flux traites  : {summary['total_flux']}")
    print(f"Alertes       : {summary['alertes']}")
    print(f"Taux d'alerte : {summary['taux_alerte']:.4%}")
    print(f"Sortie        : {summary['output_dir']}")
    return summary


def main():
    parser = argparse.ArgumentParser(description='AnomalyShield - pipeline end-to-end')
    parser.add_argument('input', help='CSV CICIDS 2017 a analyser')
    parser.add_argument('-o', '--output', default='output', help='Dossier de sortie')
    parser.add_argument('-t', '--threshold', type=float, default=0.5, help='Seuil d\'alerte')
    parser.add_argument('--chunksize', type=int, default=50000, help='Taille des chunks')
    parser.add_argument('--nrows', type=int, default=None, help='Limiter le nombre de lignes (test)')
    args = parser.parse_args()

    run_pipeline(
        args.input,
        output_dir=args.output,
        threshold=args.threshold,
        chunksize=args.chunksize,
        nrows=args.nrows,
    )


if __name__ == '__main__':
    main()
