import pandas as pd


def test_features_count(model):
    assert len(model.features) == 30


def test_predict_normal_dict(model, normal_flow):
    result = model.predict(normal_flow)
    assert result['prediction'] == 0
    assert 'verdict' in result
    assert 'score' in result


def test_predict_attack_dict(model, attack_flow):
    result = model.predict(attack_flow)
    assert result['prediction'] == 1


def test_predict_list_of_dicts(model, normal_flow, attack_flow):
    results = model.predict([normal_flow, attack_flow])
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]['prediction'] == 0
    assert results[1]['prediction'] == 1


def test_predict_dataframe(model, normal_flow, attack_flow):
    df = pd.DataFrame([normal_flow, attack_flow])
    results = model.predict(df)
    assert isinstance(results, list)
    assert len(results) == 2


def test_predict_dataframe_strips_columns(model, normal_flow):
    df = pd.DataFrame([normal_flow])
    df.columns = [' ' + c for c in df.columns]
    result = model.predict(df)
    assert result['prediction'] == 0
