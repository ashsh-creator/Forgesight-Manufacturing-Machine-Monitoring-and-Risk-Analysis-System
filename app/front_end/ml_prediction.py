"""AI4I 2020 ML demonstration page for ForgeSight.

Uses the AI4I feature schema only, not the CNC_1–CNC_7 sensor readings.
"""
from pathlib import Path
import json
from html import escape

import joblib
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / 'ml_models' / 'ai4i_failure_model.joblib'
INFO_PATH = PROJECT_ROOT / 'ml_models' / 'ai4i_model_info.json'
EXAMPLES = {
    'Normal conditions': {'Type': 'M', 'Air temperature [K]': 298.0, 'Process temperature [K]': 308.0, 'Rotational speed [rpm]': 1500, 'Torque [Nm]': 40.0, 'Tool wear [min]': 100},
    'Failure-labeled example (UDI 70)': {'Type': 'L', 'Air temperature [K]': 298.9, 'Process temperature [K]': 309.0, 'Rotational speed [rpm]': 1410, 'Torque [Nm]': 65.7, 'Tool wear [min]': 191},
}
INPUT_KEYS = {
    'Type': 'ml_type', 'Air temperature [K]': 'ml_air',
    'Process temperature [K]': 'ml_process', 'Rotational speed [rpm]': 'ml_speed',
    'Torque [Nm]': 'ml_torque', 'Tool wear [min]': 'ml_wear',
}


def _apply_example():
    values = EXAMPLES[st.session_state['ml_example']]
    for field, key in INPUT_KEYS.items():
        st.session_state[key] = values[field]
    st.session_state.pop('ml_prediction_result', None)


FEATURES = [
    'Type', 'Air temperature [K]', 'Process temperature [K]',
    'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]',
]


@st.cache_resource(show_spinner=False)
def _load_model(path, modified_time):
    """Load only the model trained locally; joblib files must be trusted."""
    return joblib.load(path)


def _style():
    st.markdown('''<style>
    .ml-heading{font-size:29px;font-weight:750;letter-spacing:-.03em;color:#17243A;margin-bottom:4px}
    .ml-subtitle{color:#64748B;font-size:13px;margin-bottom:20px}
    .ml-card{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:20px;margin:12px 0}
    .ml-eyebrow{color:#64748B;font-size:11px;font-weight:700;letter-spacing:.07em;text-transform:uppercase}
    .ml-result{font-size:25px;font-weight:750;margin:8px 0}
    .ml-detail{font-size:13px;color:#475569;line-height:1.7}
    .ml-info{background:#EFF6FF;border:1px solid #BFDBFE;color:#1E40AF;border-radius:11px;padding:16px 18px;margin:0 0 16px;font-size:13px;line-height:1.7}
    .ml-section-title{font-size:21px;font-weight:750;color:#17243A;margin:0 0 8px}
    .ml-prob-label{font-size:12px;color:#64748B;font-weight:650;margin-bottom:6px}
    .ml-prob-value{font-size:30px;color:#17243A;font-weight:750;margin-bottom:12px}
    .ml-track{width:100%;height:11px;background:#E9EFF8;border-radius:99px;overflow:hidden}
    .ml-fill{height:100%;border-radius:99px}
    .ml-note{font-size:12px;color:#64748B;line-height:1.65;margin-top:12px}
    /* Streamlit input labels must remain legible in both light/dark browser themes. */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stNumberInput"] label p,
    [data-testid="stSelectbox"] label p {color:#334155!important;opacity:1!important;font-weight:600!important}
    [data-testid="stNumberInput"] [data-testid="stNumberInputContainer"],
    [data-testid="stNumberInput"] [data-baseweb="input"],
    [data-testid="stSelectbox"] [data-baseweb="select"]>div {background:#FFFFFF!important;color:#17243A!important}
    [data-testid="stNumberInput"] input {background:#FFFFFF!important;color:#17243A!important;-webkit-text-fill-color:#17243A!important}
    [data-testid="stNumberInput"] button {background:#F1F5FB!important;color:#2457C5!important;border-color:#D9E3F1!important}
    [data-testid="stNumberInput"] button:hover {background:#E3ECFC!important}
    [data-testid="stNumberInput"] button svg {fill:#2457C5!important;stroke:#2457C5!important}
    [data-testid="stSelectbox"] [data-baseweb="select"] * {color:#17243A!important}
    /* Override global red button styles specifically for the prediction form. */
    div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button,
    div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button[kind="primary"],
    div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primary"] {
        background-color:#2457C5!important;
        color:#FFFFFF!important;
        border:1px solid #2457C5!important;
    }
    div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] button:hover {
        background-color:#1945A5!important;
        color:#FFFFFF!important;
        border-color:#1945A5!important;
    }
    .ml-cmatrix{width:100%;border-collapse:separate;border-spacing:0;
        border:1px solid #E2E8F0;border-radius:10px;overflow:hidden;background:#FFFFFF;
        font-size:13px;color:#17243A}
    .ml-cmatrix th{background:#F5F7FB;color:#475569;font-weight:700;text-align:left}
    .ml-cmatrix td,.ml-cmatrix th{padding:13px 16px;border-bottom:1px solid #E2E8F0}
    .ml-cmatrix tr:last-child td{border-bottom:0}
    .ml-cmatrix td:not(:first-child){text-align:right;font-variant-numeric:tabular-nums}
    .ml-cmatrix td:first-child{font-weight:600;color:#334155}
    [data-testid="stFormSubmitButton"] button[kind="primary"],
    [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primary"] {
        background:#2457C5!important;color:#FFFFFF!important;border:1px solid #2457C5!important;
    }
    [data-testid="stFormSubmitButton"] button[kind="primary"]:hover,
    [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primary"]:hover {
        background:#1945A5!important;color:#FFFFFF!important;border-color:#1945A5!important;
    }
    </style>''', unsafe_allow_html=True)


def show_ml_prediction_page():
    _style()
    st.markdown(
        '<div class="ml-heading">ML Failure Prediction</div>'
        '<div class="ml-subtitle">Random Forest · AI4I 2020 demonstration dataset</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="ml-info"><strong>About this prediction</strong><div>'
        'This page uses a trained model on the AI4I 2020 synthetic dataset. '
        'It is separate from the rule-based CNC machine assessments. '
        'The output is a failure classification at the observation, '
        'not a forecast of days until failure.</div></div>',
        unsafe_allow_html=True,
    )

    if not MODEL_PATH.is_file():
        st.error('Trained model not found. Run `python train_model.py` from the Manufacturing_AI project root first.')
        st.code(str(MODEL_PATH))
        return

    try:
        model = _load_model(str(MODEL_PATH), MODEL_PATH.stat().st_mtime)
    except Exception as exc:
        st.error(f'Unable to load the trained model: {exc}')
        return

    for field, key in INPUT_KEYS.items():
        if key not in st.session_state:
            st.session_state[key] = EXAMPLES['Normal conditions'][field]

    st.selectbox(
        'Quick-fill example',
        list(EXAMPLES),
        key='ml_example',
        on_change=_apply_example,
        help='Selecting an example fills all six fields. The failure example is a labeled dataset row, not a guarantee of model output.',
    )

    with st.container(border=True):
        st.markdown('<div class="ml-section-title">Machine operating conditions</div>', unsafe_allow_html=True)
        st.caption('Enter measurements using the units below. These are AI4I dataset features, not CNC sensor fields.')
        with st.form('ml_prediction_form'):
            left, right = st.columns(2, gap='large')
            with left:
                machine_type = st.selectbox(
                    'Product quality type', ['L', 'M', 'H'], key='ml_type',
                    help='AI4I product category: Low, Medium, High quality.',
                )
                air_temp = st.number_input('Air temperature (K)', min_value=200.0,
                                           max_value=500.0, step=0.1, key='ml_air')
                process_temp = st.number_input('Process temperature (K)', min_value=200.0,
                                               max_value=500.0, step=0.1, key='ml_process')
            with right:
                speed = st.number_input('Rotational speed (rpm)', min_value=0,
                                        max_value=10000, step=1, key='ml_speed')
                torque = st.number_input('Torque (Nm)', min_value=0.0,
                                         max_value=200.0, step=0.1, key='ml_torque')
                wear = st.number_input('Tool wear (minutes)', min_value=0,
                                       max_value=1000, step=1, key='ml_wear')
            predict = st.form_submit_button('Predict Failure', type='primary', use_container_width=True)

    if predict:
        row = pd.DataFrame([{
            'Type': machine_type,
            'Air temperature [K]': air_temp,
            'Process temperature [K]': process_temp,
            'Rotational speed [rpm]': speed,
            'Torque [Nm]': torque,
            'Tool wear [min]': wear,
        }], columns=FEATURES)
        try:
            prediction = int(model.predict(row)[0])
            probability = float(model.predict_proba(row)[0][list(model.classes_).index(1)])
        except Exception as exc:
            st.error(f'Prediction failed: {exc}')
            return
        st.session_state['ml_prediction_result'] = {
            'prediction': prediction,
            'probability': probability,
            'inputs': row.iloc[0].to_dict(),
        }

    result = st.session_state.get('ml_prediction_result')
    if result:
        prediction = result['prediction']
        probability = result['probability']
        label = 'Failure predicted' if prediction == 1 else 'No failure predicted'
        accent = '#C43D4B' if prediction == 1 else '#16845B'
        width = max(0.0, min(100.0, probability * 100))
        st.markdown(
            '<div class="ml-card"><div class="ml-eyebrow">Model result</div>'
            f'<div class="ml-result" style="color:{accent}">{escape(label)}</div>'
            '<div class="ml-detail">Binary prediction for the last submitted operating conditions. '
            'A positive result means the model classified this observation as a failure case '
            'in the AI4I task.</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="ml-card">'
            '<div class="ml-prob-label">Estimated failure-class model score</div>'
            f'<div class="ml-prob-value">{probability * 100:.1f}%</div>'
            '<div class="ml-track">'
            f'<div class="ml-fill" style="width:{width:.4f}%;background:{accent}"></div>'
            '</div><div class="ml-note">This is a model score, not a calibrated real-world '
            'failure probability or a prediction of remaining useful life. '
            'Results depend on the synthetic training data.</div></div>',
            unsafe_allow_html=True,
        )

    with st.expander('Model details and limitations'):
        st.write('**Algorithm:** Random Forest classifier')
        st.write('**Training data:** UCI AI4I 2020 predictive maintenance (synthetic)')
        st.write('**Input features:** Type, air temperature, process temperature, rotational speed, torque, tool wear.')
        st.write('**Output:** Failure (1) or no failure (0) at the observation.')
        st.write('**Not supported:** CNC vibration/current/pressure inference, '
                 'time-to-failure prediction, or validated industrial deployment.')
        if INFO_PATH.is_file():
            try:
                info = json.loads(INFO_PATH.read_text(encoding='utf-8'))
                if 'roc_auc' in info:
                    st.write(f'**Held-out test ROC-AUC:** {info["roc_auc"]:.3f}')
            except (OSError, ValueError, TypeError):
                pass

    st.markdown('<div class="ml-section-title" style="margin-top:26px">Model evaluation</div>', unsafe_allow_html=True)
    st.caption('Held-out AI4I synthetic test set: 2,000 observations, including 68 labeled failures. '
               'Results describe this dataset only, not real CNC equipment.')
    a, b, c, d = st.columns(4)
    a.metric('Accuracy', '97.4%')
    b.metric('Failure precision', '58.9%')
    c.metric('Failure recall', '77.9%')
    d.metric('Failure F1-score', '67.1%')
    st.markdown('**Confusion matrix — held-out test set**')
    st.markdown(
        '<table class="ml-cmatrix">'
        '<thead><tr><th>Actual outcome</th><th>Predicted: No failure</th>'
        '<th>Predicted: Failure</th></tr></thead>'
        '<tbody>'
        '<tr><td>Actual: No failure</td><td>1,895</td><td>37</td></tr>'
        '<tr><td>Actual: Failure</td><td>15</td><td>53</td></tr>'
        '</tbody></table>',
        unsafe_allow_html=True,
    )
    st.caption('37 false alarms and 15 missed failures. These numbers are from the training run '
               'you shared; retraining the model may change them.')
