import pytest

from predict import AnomalyShield


EXAMPLE_NORMAL = {
    'Max Packet Length': 6.0, 'Packet Length Variance': 0.0, 'Avg Bwd Segment Size': 0.0,
    'Packet Length Std': 0.0, 'Bwd Packet Length Max': 0.0, 'Average Packet Size': 9.0,
    'Total Length of Bwd Packets': 0.0, 'Bwd Packet Length Std': 0.0, 'Bwd Packet Length Mean': 0.0,
    'Subflow Fwd Packets': 2.0, 'Destination Port': 54865.0, 'Packet Length Mean': 6.0,
    'Subflow Fwd Bytes': 12.0, 'Total Fwd Packets': 2.0, 'PSH Flag Count': 0.0,
    'Fwd IAT Max': 3.0, 'act_data_pkt_fwd': 1.0, 'Fwd Header Length': 40.0,
    'Subflow Bwd Bytes': 0.0, 'Fwd Header Length.1': 40.0, 'Total Length of Fwd Packets': 12.0,
    'Bwd Header Length': 0.0, 'Init_Win_bytes_backward': -1.0, 'Fwd Packet Length Max': 6.0,
    'Flow IAT Std': 0.0, 'Idle Mean': 0.0, 'Bwd Packets/s': 0.0,
    'Init_Win_bytes_forward': 33.0, 'Flow Bytes/s': 4000000.0, 'Fwd IAT Min': 3.0,
}

EXAMPLE_ATTACK = {
    'Max Packet Length': 5840.0, 'Packet Length Variance': 3435230.673, 'Avg Bwd Segment Size': 1658.142857,
    'Packet Length Std': 1853.437529, 'Bwd Packet Length Max': 5840.0, 'Average Packet Size': 1163.3,
    'Total Length of Bwd Packets': 11607.0, 'Bwd Packet Length Std': 2137.29708, 'Bwd Packet Length Mean': 1658.142857,
    'Subflow Fwd Packets': 3.0, 'Destination Port': 80.0, 'Packet Length Mean': 1057.545455,
    'Subflow Fwd Bytes': 26.0, 'Total Fwd Packets': 3.0, 'PSH Flag Count': 1.0,
    'Fwd IAT Max': 744.0, 'act_data_pkt_fwd': 2.0, 'Fwd Header Length': 72.0,
    'Subflow Bwd Bytes': 11607.0, 'Fwd Header Length.1': 72.0, 'Total Length of Fwd Packets': 26.0,
    'Bwd Header Length': 152.0, 'Init_Win_bytes_backward': 229.0, 'Fwd Packet Length Max': 20.0,
    'Flow IAT Std': 430865.8067, 'Idle Mean': 0.0, 'Bwd Packets/s': 5.410452376,
    'Init_Win_bytes_forward': 8192.0, 'Flow Bytes/s': 8991.398927, 'Fwd IAT Min': 3.0,
}


@pytest.fixture(scope='session')
def model():
    return AnomalyShield()


@pytest.fixture()
def normal_flow():
    return dict(EXAMPLE_NORMAL)


@pytest.fixture()
def attack_flow():
    return dict(EXAMPLE_ATTACK)
