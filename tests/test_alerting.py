import pytest

from alerting import AlertManager


@pytest.fixture()
def manager(tmp_path):
    return AlertManager(threshold=0.5, log_file=str(tmp_path / 'alerts.log'))


def _flush(manager):
    for handler in manager.logger.handlers:
        handler.flush()


def test_threshold_value(manager):
    assert manager.threshold == 0.5


def test_process_returns_only_alerts(manager):
    results = [
        {'score': 0.9, 'prediction': 1, 'verdict': 'ALERT'},
        {'score': 0.1, 'prediction': 0, 'verdict': 'Normal'},
        {'score': 0.6, 'prediction': 1, 'verdict': 'ALERT'},
    ]
    alerts = manager.process(results)
    assert len(alerts) == 2


def test_process_single_dict(manager):
    alerts = manager.process({'score': 0.9, 'prediction': 1})
    assert len(alerts) == 1


def test_threshold_filters_low_score(manager):
    alerts = manager.process([{'score': 0.4, 'prediction': 1}])
    assert alerts == []


def test_alert_written_to_log(manager):
    manager.process([{'score': 0.9, 'prediction': 1}])
    _flush(manager)
    content = manager.log_file.read_text(encoding='utf-8')
    assert 'ALERT' in content


def test_no_email_without_smtp(manager):
    alerts = manager.process([{'score': 0.99, 'prediction': 1}])
    assert len(alerts) == 1
