"""ForgeSight machine details page; existing service and navigation contracts retained."""
import os
import sys
from datetime import datetime
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import DataLoader
from utils.logger_config import get_logger
from services.machines_service import machines_service, ServiceException

logger = get_logger(__name__)
data_loader = DataLoader()
BLUE = '#2457C5'
DARK = '#17243A'
MUTED = '#64748B'
RISK = {'High': ('#C43D4B', '#FFF0F2'), 'Medium': ('#B7791F', '#FFF6E5'), 'Low': ('#16845B', '#EAF9F1')}


def _css():
    st.markdown('''<style>
    .fd-title{font-size:29px;font-weight:750;letter-spacing:-.03em;color:#17243A;margin:0 0 4px}
    .fd-subtitle{font-size:13px;color:#64748B;margin-bottom:20px}
    .fd-section{font-size:19px;font-weight:700;color:#17243A;margin:22px 0 12px}
    .fd-card{background:white;border:1px solid #E2E8F0;border-radius:12px;padding:18px;margin-bottom:12px}
    .fd-label{font-size:11px;letter-spacing:.05em;text-transform:uppercase;font-weight:700;color:#64748B}
    .fd-value{font-size:24px;font-weight:750;color:#17243A;margin-top:8px}
    .fd-small{font-size:12px;color:#64748B;margin-top:5px}
    .fd-badge{display:inline-block;padding:6px 11px;border-radius:20px;font-size:12px;font-weight:700}
    .fd-notes{background:#F8FAFD;border:1px solid #E2E8F0;border-radius:10px;padding:16px;color:#475569;font-size:13px}
    .fd-alert{border-radius:11px;border:1px solid;padding:17px 19px;margin:14px 0 20px;line-height:1.6;font-size:14px}
    .fd-alert strong{display:block;font-size:14px;margin-bottom:4px}
    .fd-alert-warning{background:#FFFBEB;border-color:#F4D58A;color:#854D0E}
    .fd-alert-info{background:#EFF6FF;border-color:#BFDBFE;color:#1E40AF}
    .fd-alert-success{background:#ECFDF5;border-color:#A7F3D0;color:#065F46}
    .fd-report-intro{background:#F8FAFD;border:1px solid #E2E8F0;border-radius:12px;padding:16px 18px;color:#475569;font-size:13px;margin-bottom:12px}
    .fd-report-preview{border:1px solid #E2E8F0;border-radius:12px;padding:20px 22px;background:white;margin:12px 0}
    .fd-report-preview h1{font-size:23px!important;line-height:1.35!important;margin:0 0 12px!important}
    .fd-report-preview h2{font-size:16px!important;margin:22px 0 10px!important;padding-top:13px;border-top:1px solid #E2E8F0}
    .fd-report-preview p,.fd-report-preview li{font-size:13px!important;line-height:1.75!important;color:#334155}
    .fd-report-preview ul{padding-left:20px}
    [data-testid="stAlert"]{border-radius:11px}
    [data-testid="stAlert"] p{color:#334155!important}
    [data-testid="stPlotlyChart"]{background:#FFFFFF!important;border:1px solid #E2E8F0;border-radius:12px;padding:6px}
    [data-testid="stButton"] button{color:#2457C5!important;background:#FFFFFF!important;border:1px solid #D6E2F6!important;border-radius:8px!important}
    [data-testid="stButton"] button:hover{background:#EDF3FF!important;border-color:#2457C5!important}
    [data-testid="stButton"] button[kind="primary"]{background:#2457C5!important;color:#FFFFFF!important;border-color:#2457C5!important}
    </style>''', unsafe_allow_html=True)


def get_service_data(method_name, *args, **kwargs):
    """Call the original service without changing its interface."""
    try:
        return getattr(machines_service, method_name)(*args, **kwargs)
    except (ServiceException, Exception) as exc:
        logger.exception('Machine service call failed: %s', method_name)
        st.error(f'Unable to retrieve {method_name.replace("_", " ")}: {exc}')
        return None


def show_custom_loader(message='Loading Machine Details', submessage='Fetching machine data'):
    st.info(f'{message} · {submessage}')


def _fmt(value, digits=1):
    try:
        number = float(value)
        return f'{number:.{digits}f}' if pd.notna(number) else '—'
    except (ValueError, TypeError):
        return '—'


def _date(value):
    try:
        return pd.to_datetime(value).strftime('%d %b %Y, %I:%M %p')
    except Exception:
        return str(value or '—')


def _metric(label, value, detail):
    st.markdown(f'<div class="fd-card"><div class="fd-label">{escape(label)}</div>'
                f'<div class="fd-value">{escape(str(value))}</div>'
                f'<div class="fd-small">{escape(detail)}</div></div>', unsafe_allow_html=True)


def _chart(history, column, title, unit, color):
    if column not in history.columns or history[column].dropna().empty:
        st.markdown(f'<div class="fd-card"><div class="fd-label">{escape(title)}</div><div class="fd-small">No sensor readings available.</div></div>', unsafe_allow_html=True)
        return
    history = history.dropna(subset=[column])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history['timestamp'], y=history[column],
                             mode='lines+markers', name=title,
                             line=dict(color=color, width=2.5),
                             marker=dict(size=7, color=color),
                             hovertemplate=f'%{{x|%d %b %Y, %H:%M}}<br>{title}: %{{y:.2f}} {unit}<extra></extra>'))
    fig.update_layout(template='plotly_white', height=305,
                      title=dict(text=title, font=dict(size=16, color=DARK), x=.035),
                      paper_bgcolor='#FFFFFF', plot_bgcolor='#FFFFFF',
                      font=dict(color=DARK, size=11), showlegend=False,
                      margin=dict(l=52, r=24, t=57, b=55),
                      xaxis=dict(title='Time', gridcolor='#EDF1F7', tickfont=dict(color=MUTED),
                                 title_font=dict(color=MUTED), tickformat='%H:%M\n%d %b'),
                      yaxis=dict(title=unit, gridcolor='#EDF1F7', tickfont=dict(color=MUTED),
                                 title_font=dict(color=MUTED), zeroline=False))
    st.plotly_chart(fig, use_container_width=True)


def _days_text(days):
    """Display an estimate without inventing a value when it is unavailable."""
    if days is None or _fmt(days, 0) == '—':
        return 'Not available'
    number = float(days)
    return f'{number:g} day' if number == 1 else f'{number:g} days'


def _local_report(machine_id, prediction, savings, notes, history):
    """Create a readable Markdown report from the existing rule-based assessment."""
    risk = str(prediction.get('failure_risk') or 'Unknown').title()
    days = prediction.get('predicted_days_to_failure')
    indicator = prediction.get('confidence')
    reason = str(prediction.get('reason') or 'No assessment reason available.')
    actions = prediction.get('recommendations') or []
    if isinstance(actions, str):
        actions = [actions]
    latest = history.sort_values('timestamp').iloc[-1] if not history.empty else {}

    lines = [
        f'# Maintenance Report — {machine_id}',
        f'Generated: {datetime.now().strftime("%d %b %Y, %H:%M")}',
        '', '---', '',
        '## Equipment Assessment', '',
        '| Measure | Result |', '| :--- | :--- |',
        f'| Failure risk | **{risk}** |',
        f'| Estimated time to failure | {_days_text(days)} (rule-based estimate) |',
        f'| Rule-based risk indicator | {_fmt(indicator, 0)} / 100 (heuristic, not ML confidence) |' if indicator is not None else '| Rule-based risk indicator | Not available |',
        '', '**Assessment**', '', reason, '',
        '## Latest Sensor Readings', '',
        '| Sensor | Reading |', '| :--- | ---: |',
        f'| Temperature | {_fmt(latest.get("temperature"))} °C |',
        f'| Vibration | {_fmt(latest.get("vibration"))} g |',
        f'| Current | {_fmt(latest.get("current"))} A |',
        f'| Pressure | {_fmt(latest.get("pressure"))} bar |',
        '', '## Recommended Actions', '',
    ]
    lines.extend(f'- {action}' for action in actions) if actions else lines.append('- No recommendations available.')
    lines.extend(['', '## Maintenance and Cost Outlook', ''])
    if risk == 'Unknown':
        lines.append('Cost savings and downtime estimates are unavailable without a reliable sensor assessment.')
    else:
        lines.extend([
            '| Measure | Estimate |', '| :--- | ---: |',
            f'| Potential cost savings | {_fmt(savings.get("savings"), 2)} (backend currency) |',
            f'| Potential downtime | {_fmt(savings.get("downtime_hours"))} hours |',
        ])
    lines.extend([
        '', '**Service and maintenance notes**', '', str(notes), '',
        '---', '',
        '*This report uses threshold-based rules and available sensor data. Risk indicators are not calibrated probabilities; time-to-failure and cost estimates are illustrative, not validated forecasts.*',
    ])
    return '\n'.join(lines)


def show_machine_details_content(selected_machine):
    """Render sensor history, maintenance assessment, and local report."""
    with st.spinner(f'Loading {selected_machine} information...'):
        details = get_service_data('get_machine_details', selected_machine)
    if details is None:
        return
    try:
        history = data_loader.get_machine_history(selected_machine)
        maintenance = data_loader.get_machine_maintenance_data(selected_machine) or {}
    except Exception as exc:
        logger.exception('Failed to load machine history/maintenance')
        st.error(f'Could not load machine history: {exc}')
        return

    prediction = details.get('current_status') or {}
    savings = details.get('cost_savings') or {}
    risk = str(prediction.get('failure_risk') or 'Unknown').title()
    risk_color, risk_bg = RISK.get(risk, (MUTED, '#F1F5F9'))
    notes = str(maintenance.get('service_notes') or 'No service notes available.')

    top_left, top_right = st.columns([5, 1.5], vertical_alignment='center')
    with top_left:
        st.markdown(f'<div class="fd-title">Machine {escape(str(selected_machine))}</div>'
                    '<div class="fd-subtitle">Equipment health, historical sensor readings and maintenance insights</div>',
                    unsafe_allow_html=True)
    with top_right:
        if st.button('← Back to Machines', key='fd_back', use_container_width=True):
            st.session_state.current_page = 'machines'
            st.session_state.selected_machine = None
            for key in ('page', 'machine_id'):
                if key in st.query_params:
                    del st.query_params[key]
            st.rerun()

    st.markdown(f'<span class="fd-badge" style="color:{risk_color};background:{risk_bg}">'
                f'{escape(risk)} Risk</span> '
                f'<span style="font-size:12px;color:{MUTED};margin-left:10px">'
                f'Last reading: {escape(_date(details.get("latest_reading")))}</span>', unsafe_allow_html=True)

    latest = history.sort_values('timestamp').iloc[-1] if not history.empty else {}
    no_data = risk == 'Unknown'
    if no_data:
        st.markdown(
            '<div class="fd-alert fd-alert-warning"><strong>Sensor readings unavailable</strong>'
            'This machine has incomplete sensor data. Failure risk and time-to-failure '
            'cannot be reliably assessed until readings are restored. Existing service '
            'and maintenance notes remain available.</div>',
            unsafe_allow_html=True,
        )
    st.markdown('<div class="fd-section">Current Sensor Readings</div>', unsafe_allow_html=True)
    cols = st.columns(4, gap='medium')
    metrics = [('Temperature', f'{_fmt(latest.get("temperature"))} °C', 'Thermal sensor'),
               ('Vibration', f'{_fmt(latest.get("vibration"))} g', 'Vibration sensor'),
               ('Current', f'{_fmt(latest.get("current"))} A', 'Electrical load'),
               ('Pressure', f'{_fmt(latest.get("pressure"))} bar', 'Pressure sensor')]
    for col, (label, value, desc) in zip(cols, metrics):
        with col:
            _metric(label, value, desc)

    st.markdown('<div class="fd-section">Sensor History</div>', unsafe_allow_html=True)
    if history.empty or not any(
        name in history.columns and history[name].notna().any()
        for name in ('vibration', 'temperature', 'current', 'pressure')
    ):
        st.markdown(
            '<div class="fd-alert fd-alert-info"><strong>No sensor history to chart</strong>'
            'There are no valid readings for this machine. Charts will appear when '
            'sensor data becomes available.</div>',
            unsafe_allow_html=True,
        )
    else:
        history = history.sort_values('timestamp')
        left, right = st.columns(2, gap='large')
        with left:
            _chart(history, 'vibration', 'Vibration Trend', 'g', '#7856C7')
            _chart(history, 'current', 'Current Trend', 'A', '#D99119')
        with right:
            _chart(history, 'temperature', 'Temperature Trend', '°C', '#D9485F')
            _chart(history, 'pressure', 'Pressure Trend', 'bar', '#159A72')

    st.markdown('<div class="fd-section">Predictive Maintenance</div>', unsafe_allow_html=True)
    pcols = st.columns(3, gap='medium')
    with pcols[0]:
        _metric('Failure Risk', 'Data Unavailable' if no_data else risk, 'Threshold-based assessment')
    with pcols[1]:
        days = prediction.get('predicted_days_to_failure')
        _metric('Estimated Time to Failure', _days_text(days) if days is not None else '—',
                'Model estimate, not a guarantee')
    with pcols[2]:
        confidence = prediction.get('confidence')
        _metric('Rule-Based Risk Indicator', f'{_fmt(confidence, 0)} / 100' if confidence is not None else '—',
                'Heuristic score, not validated ML confidence')

    reason = prediction.get('reason')
    recommendations = prediction.get('recommendations') or []
    if reason:
        st.markdown(f'<div class="fd-card"><div class="fd-label">Assessment</div>'
                    f'<div style="color:#475569;margin-top:8px;font-size:13px">{escape(str(reason))}</div></div>',
                    unsafe_allow_html=True)
    if recommendations:
        st.markdown('**Recommended Actions**')
        if isinstance(recommendations, str):
            recommendations = [recommendations]
        for item in recommendations:
            st.markdown(f'- {escape(str(item))}')

    if savings and not no_data:
        scols = st.columns(2, gap='medium')
        with scols[0]:
            _metric('Estimated Cost Savings', _fmt(savings.get('savings'), 2),
                    'Currency follows backend configuration')
        with scols[1]:
            _metric('Potential Downtime', f'{_fmt(savings.get("downtime_hours"))} hours',
                    'Estimated downtime exposure')

    st.markdown('<div class="fd-section">Service & Maintenance Notes</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="fd-notes">{escape(notes)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="fd-section">ForgeSight Maintenance Report</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="fd-report-intro">Generate a downloadable maintenance summary '
        'using the existing threshold-based assessment, available sensor readings, '
        'and maintenance records. No external API or password is needed. '
        'This is a rule-based report, not a generative AI diagnosis.</div>',
        unsafe_allow_html=True,
    )
    report_key = f'fd_local_report_{selected_machine}'
    if st.button('Generate Maintenance Report', key='fd_generate_report', type='primary'):
        st.session_state[report_key] = _local_report(selected_machine, prediction, savings, notes, history)
    report = st.session_state.get(report_key)
    if report:
        st.markdown(
            '<div class="fd-alert fd-alert-success"><strong>Report ready</strong>'
            'Your maintenance report has been generated. Review it below or download '
            'the Markdown (.md) file.</div>',
            unsafe_allow_html=True,
        )
        st.download_button(
            '↓ Download Maintenance Report (.md)',
            data=report,
            file_name=f'ForgeSight_{selected_machine}_maintenance_report.md',
            mime='text/markdown',
            key='fd_download_report',
        )
        with st.expander('Preview full maintenance report', expanded=True):
            st.markdown(report)

    st.markdown(f'<div style="border-top:1px solid #E2E8F0;margin-top:28px;padding:18px 0;'
                f'text-align:center;color:#64748B;font-size:12px">'
                f'ForgeSight · Manufacturing Predictive Maintenance · Updated '
                f'{datetime.now().strftime("%d %b %Y, %H:%M")}</div>', unsafe_allow_html=True)


def show_machine_details_page():
    """Entry point expected by app/main.py."""
    logger.info('Machine details page started')
    _css()
    selected = st.session_state.get('selected_machine') or st.query_params.get('machine_id')
    if not selected:
        st.warning('No machine selected. Open a machine from the Machines page.')
        if st.button('Go to Machines', key='fd_go_machines'):
            st.session_state.current_page = 'machines'
            st.rerun()
        return
    show_machine_details_content(str(selected))
    