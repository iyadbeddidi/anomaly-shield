import streamlit as st
import pandas as pd
import plotly.express as px
from predict import AnomalyShield

st.set_page_config(
    page_title='AnomalyShield',
    page_icon='🛡️',
    layout='wide',
)

st.title('🛡️ AnomalyShield — Détection d\'anomalies réseau')
st.caption('Système intelligent de détection d\'anomalies basé sur le MLP (réseau de neurones supervisé)')

@st.cache_resource
def load_model():
    return AnomalyShield()

try:
    model = load_model()
    st.sidebar.success(f'✅ Modèle chargé — {len(model.features)} features (CPU)')
except Exception as e:
    st.sidebar.error(f'❌ Erreur de chargement du modèle: {e}')
    st.stop()

st.sidebar.header('Mode de prédiction')
mode = st.sidebar.radio('Choisir un mode', ['📁 Upload CSV (batch)', '✍️ Saisie manuelle'])

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


def display_single_result(result, col=None):
    score = result['score']
    is_anomaly = result['prediction'] == 1
    if col is not None:
        with col:
            if is_anomaly:
                st.error('🚨 **ALERT — Anomalie détectée**')
            else:
                st.success('✅ **Trafic normal**')
            st.metric('Score d\'anomalie', f'{score:.4f}')
            st.progress(min(float(score), 1.0))
            st.caption(f"Verdict: {result['verdict']}")


if mode == '✍️ Saisie manuelle':
    st.header('Saisie manuelle d\'un flux réseau')

    c1, c2 = st.columns(2)
    with c1:
        if st.button('🔵 Remplir avec un flux NORMAL'):
            st.session_state['flow_values'] = EXAMPLE_NORMAL
    with c2:
        if st.button('🔴 Remplir avec un flux D\'ATTAQUE (DDoS)'):
            st.session_state['flow_values'] = EXAMPLE_ATTACK

    defaults = st.session_state.get('flow_values', None)

    with st.form('manual_form'):
        st.subheader('Caractéristiques du flux (30 features)')
        values = {}
        cols = st.columns(3)
        for i, f in enumerate(model.features):
            default = defaults[f] if defaults else 0.0
            with cols[i % 3]:
                values[f] = st.number_input(f, value=float(default), format='%.6f', key=f)

        submitted = st.form_submit_button('🔍 Analyser le flux')

    if submitted:
        result = model.predict(values)
        display_single_result(result)
        with st.expander('Voir les détails'):
            st.json(result)

elif mode == '📁 Upload CSV (batch)':
    st.header('Analyse par lot (upload CSV)')
    st.caption('Le fichier doit contenir les colonnes du dataset CICIDS 2017 (avec ou sans espaces dans les noms).')

    uploaded = st.file_uploader('Choisir un fichier CSV', type=['csv'])

    if uploaded is not None:
        df = pd.read_csv(uploaded)
        st.info(f'📄 {len(df)} flux chargés')

        if st.button('🔍 Lancer l\'analyse'):
            with st.spinner('Analyse en cours...'):
                results = model.predict(df)

            df_results = pd.DataFrame(results)
            df_results['index'] = df.index

            n_alerts = int(df_results['prediction'].sum())
            n_normal = len(df_results) - n_alerts

            st.subheader('Résultats globaux')
            m1, m2, m3 = st.columns(3)
            m1.metric('Total flux', len(df_results))
            m2.metric('🚨 Anomalies détectées', n_alerts)
            m3.metric('✅ Flux normaux', n_normal)

            if n_alerts > 0:
                pct = n_alerts / len(df_results) * 100
                st.warning(f'⚠️ **{pct:.2f}%** du trafic est anormal')

            fig = px.pie(
                names=['Anomalies', 'Normaux'],
                values=[n_alerts, n_normal],
                color_discrete_sequence=['#ff4b4b', '#00c851'],
                title='Répartition des flux',
            )
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.histogram(
                df_results, x='score', nbins=50,
                title='Distribution des scores d\'anomalie',
                color_discrete_sequence=['#636efa'],
            )
            fig2.add_vline(x=0.5, line_dash='dash', line_color='red', annotation_text='Seuil 0.5')
            st.plotly_chart(fig2, use_container_width=True)

            st.subheader('Détail des anomalies')
            anomalies = df_results[df_results['prediction'] == 1]
            if len(anomalies) > 0:
                st.dataframe(anomalies.head(50), use_container_width=True)
            else:
                st.success('Aucune anomalie détectée dans ce lot.')

            csv = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                '⬇️ Télécharger les résultats',
                data=csv,
                file_name='anomalyshield_results.csv',
                mime='text/csv',
            )
