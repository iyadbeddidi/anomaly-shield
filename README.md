# AnomalyShield

> Système intelligent de détection d'anomalies pour le monitoring des logs et infrastructures informatiques
> Stage DSI Ministère de la Transition Énergétique et du Développement Durable

AnomalyShield est un pipeline complet de détection d'anomalies réseau basé sur le Machine Learning, sur le dataset **CICIDS 2017** (~2.5M flux × 79 colonnes).

---

## Fonctionnalités

- Détection d'anomalies binaire (trafic **normal** vs **attaque**) via un **MLP supervisé** (PyTorch)
- **API REST** (FastAPI) pour l'inférence
- **Dashboard** interactif (Streamlit) : saisie manuelle + upload CSV + visualisations
- **Alerting** : log des alertes + notification email (SMTP optionnel)
- **Pipeline end-to-end** : nettoyage -> prédiction -> alerte, par chunks (adapté aux gros CSV)
- **Tests** unitaires (pytest)
- **Conteneurisation** (Docker / Docker Compose)

---

## Modèle déployé

Le **MLP supervisé** (30 features, StandardScaler) est le modèle déployé. Résultats obtenus en Phase 3 :

| Modèle | Type | AUC-ROC | F1-score |
|---|---|---|---|
| **Random Forest** | Supervisé | 0.9998 | 0.9963 |
| **MLP Supervisé** | Supervisé | 0.9996 | 0.9814 |
| Dense Autoencoder | Non-supervisé | 0.8888 | 0.4651 |
| Isolation Forest | Non-supervisé | 0.7852 | 0.5851 |
| LSTM Autoencoder | Non-supervisé | 0.5000 | 0.1576 (échec) |

> Le MLP a été retenu pour l'API car plus léger (~4K paramètres) avec des performances quasi identiques au Random Forest. Le LSTM est abandonné : absence de données temporelles réelles dans CICIDS 2017.

---

## Structure du projet

```
anomaly-shield/
├── predict.py            # Classe AnomalyShield ; inférence
├── api.py                # API FastAPI
├── dashboard.py          # Dashboard Streamlit
├── alerting.py           # AlertManager — log + email
├── pipeline.py           # Pipeline end-to-end
├── pkls/                 # Modèles et objets sérialisés
├── tests/                # Tests pytest
├── data/                 # CICIDS 2017 (non versionné)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Installation

### Option 1 : Docker (recommandé)

```powershell
# Construire et lancer l'API + le dashboard
docker compose up --build

# API    : http://localhost:8000
# Dashboard : http://localhost:8501
```

### Option 2 : Installation locale

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Usage

### API (FastAPI)

```powershell
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

| Endpoint | Méthode | Description |
|---|---|---|
| `/` | GET | Health check |
| `/predict` | POST | Prédiction batch (`{"flows": [{...}, ...]}`) |
| `/predict/single` | POST | Prédiction d'un flux unique |

### Dashboard (Streamlit)

```powershell
python -m streamlit run dashboard.py
```

### Pipeline end-to-end

```powershell
python pipeline.py data/dataset.csv -o output
python pipeline.py data/dataset.csv -o output --nrows 100000 -t 0.7
```

| Argument | Description |
|---|---|
| `input` | CSV à analyser |
| `-o` / `--output` | Dossier de sortie (défaut : `output`) |
| `-t` / `--threshold` | Seuil d'alerte (défaut : `0.5`) |
| `--chunksize` | Taille des chunks (défaut : `50000`) |
| `--nrows` | Limiter le nombre de lignes (test) |

### Tests

```powershell
python -m pytest
```

---

## Configuration (alerting)

Copier `.env.example` en `.env` et adapter :

| Variable | Description |
|---|---|
| `ANOMALY_THRESHOLD` | Seuil de score pour déclencher une alerte |
| `ALERT_LOG_FILE` | Chemin du fichier de log des alertes |
| `SMTP_HOST` / `SMTP_PORT` | Serveur SMTP (optionnel) |
| `SMTP_USER` / `SMTP_PASSWORD` | Identifiants SMTP |
| `ALERT_EMAIL_FROM` / `ALERT_EMAIL_TO` | Expéditeur / destinataire des alertes |

> Si `SMTP_HOST` n'est pas configuré, les alertes sont uniquement écrites dans le fichier de log.

---

## Dataset

**CICIDS 2017** : Canadian Institute for Cybersecurity Intrusion Detection Evaluation Dataset. ~2.8M flux réseau, 78 features (CICFlowMeter), classes : BENIGN, DDoS, PortScan, Brute Force, Web Attack, Infiltration, Bot.

> Les données réelles du ministère étant confidentielles, ce dataset public de référence est utilisé pour la validation du système.

---

## Auteur

**Iyad** — Étudiant Ingénieur IDSCC, ENSA Oujda
Stage DSI Ministère de la Transition Énergétique et du Développement Durable

## Licence

Usage académique et institutionnel uniquement.
