import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import joblib

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class MLP(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.net(x)


class AnomalyShield:
    def __init__(self, model_path='pkls/mlp_model.pt', scaler_path='pkls/scaler.pkl',
                 features_path='pkls/features.pkl'):
        self.features = joblib.load(features_path)
        self.scaler = joblib.load(scaler_path)

        self.model = MLP(len(self.features)).to(device)
        self.model.load_state_dict(torch.load(model_path, weights_only=True))
        self.model.eval()

        print(f'AnomalyShield loaded: {len(self.features)} features, device={device}')

    def predict(self, data):
        if isinstance(data, pd.DataFrame):
            data = data.rename(columns={c: c.strip() for c in data.columns})
            X = data[self.features].values
        elif isinstance(data, dict):
            data = {k.strip(): v for k, v in data.items()}
            X = np.array([[data.get(f, 0) for f in self.features]])
        elif isinstance(data, list):
            if isinstance(data[0], dict):
                X = np.array([[{k.strip(): v for k, v in d.items()}.get(f, 0) for f in self.features] for d in data])
            else:
                X = np.array(data).reshape(1, -1)
        else:
            X = np.array(data).reshape(1, -1)

        X_df = pd.DataFrame(X, columns=self.features)
        X_scaled = self.scaler.transform(X_df)

        with torch.no_grad():
            X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(device)
            logits = self.model(X_tensor)
            scores = torch.sigmoid(logits).cpu().numpy().flatten()

        predictions = (scores > 0.5).astype(int)
        verdicts = ['ALERT - Anomalie detectee' if p == 1 else 'Normal' for p in predictions]

        results = []
        for i in range(len(predictions)):
            results.append({
                'score': float(scores[i]),
                'prediction': int(predictions[i]),
                'verdict': verdicts[i]
            })

        if len(results) == 1:
            return results[0]
        return results
