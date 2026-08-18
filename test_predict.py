import pandas as pd
from predict import AnomalyShield

# Charger le modele
shield = AnomalyShield()

# Charger les donnees (50k lignes pour avoir des attaques)
df = pd.read_csv('data/dataset.csv', nrows=50000)
label_col = [c for c in df.columns if c.strip() == 'Label'][0]
df = df.rename(columns=lambda c: c.strip())

# --- Test 1: DataFrame (10 lignes normales) ---
print("\n=== Test 1: DataFrame (10 lignes normales) ===")
normals = df[df['Label'] == 'BENIGN'].head(10)
results = shield.predict(normals)
for i, r in enumerate(results):
    print(f"  Normal {i}: score={r['score']:.4f}, pred={r['prediction']}, verdict={r['verdict']}")

# --- Test 2: Detection d'attaques ---
print("\n=== Test 2: Detection d'attaques ===")
attacks = df[df['Label'] != 'BENIGN'].head(5)
if len(attacks) > 0:
    attack_results = shield.predict(attacks)
    for i, r in enumerate(attack_results):
        print(f"  Attaque {i} ({attacks.iloc[i]['Label']}): score={r['score']:.4f}, pred={r['prediction']}, verdict={r['verdict']}")
else:
    print("  Pas d'attaque dans les 50000 premieres lignes")

# --- Test 3: dict (1 observation) ---
print("\n=== Test 3: dict (1 observation normale) ===")
sample = df[df['Label'] == 'BENIGN'].iloc[0].to_dict()
result = shield.predict(sample)
print(f"  score={result['score']:.4f}, pred={result['prediction']}, verdict={result['verdict']}")

# --- Test 4: dict (1 attaque) ---
print("\n=== Test 4: dict (1 attaque) ===")
if len(attacks) > 0:
    attack_sample = attacks.iloc[0].to_dict()
    result = shield.predict(attack_sample)
    print(f"  score={result['score']:.4f}, pred={result['prediction']}, verdict={result['verdict']}")

# --- Test 5: liste de dicts (3 observations mixtes) ---
print("\n=== Test 5: liste de dicts (3 mixtes) ===")
mix = [df[df['Label'] == 'BENIGN'].iloc[0].to_dict()]
if len(attacks) > 0:
    mix.append(attacks.iloc[0].to_dict())
    mix.append(attacks.iloc[1].to_dict() if len(attacks) > 1 else attacks.iloc[0].to_dict())
results = shield.predict(mix)
labels_check = ['Normal'] + ['Attaque'] * (len(mix) - 1)
for i, (r, l) in enumerate(zip(results, labels_check)):
    print(f"  {l} {i}: score={r['score']:.4f}, pred={r['prediction']}, verdict={r['verdict']}")

print("\n=== Tests termines ===")