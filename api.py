from fastapi import FastAPI
from pydantic import BaseModel
from predict import AnomalyShield

app = FastAPI(
    title='AnomalyShield API',
    description='Network Anomaly Detection using MLP',
    version='1.0'
)

model = AnomalyShield()


class FlowData(BaseModel):
    flows: list[dict]


@app.get('/')
def root():
    return {'status': 'ok', 'model': 'MLP Supervise', 'features': len(model.features)}


@app.post('/predict')
def predict(data: FlowData):
    results = model.predict(data.flows)
    return {'predictions': results}


@app.post('/predict/single')
def predict_single(flow: dict):
    result = model.predict(flow)
    return result
