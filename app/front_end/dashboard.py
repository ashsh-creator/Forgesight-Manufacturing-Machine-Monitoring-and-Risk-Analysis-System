"""ForgeSight manufacturing predictive maintenance dashboard.

Presentation-only redesign. Existing service and navigation interfaces are retained.
"""
import os
import math
import sys
from datetime import datetime
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger_config import get_logger
from config.front_end_config import frontend_config
from services.machines_service import machines_service, ServiceException

logger = get_logger(__name__)
PRIMARY = "#2457C5"
TEXT = "#17243A"
MUTED = "#64748B"
BORDER = "#E2E8F0"
GRID = "#EDF1F7"
COLORS = {"Low": "#159A72", "Medium": "#D99119", "High": "#D9485F", "Unknown": "#64748B"}
CHART_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Arial, sans-serif", color=TEXT, size=12),
    margin=dict(l=48, r=18, t=62, b=62),
    height=350,
)


@st.cache_data(ttl=frontend_config.CACHE_TTL)
def get_service_data(method_name, *args, **kwargs):
    """Fetch data through the existing machine service."""
    logger.debug("Calling service method: %s", method_name)
    try:
        method = getattr(machines_service, method_name)
        return method(*args, **kwargs)
    except ServiceException as exc:
        logger.error("Service error in %s: %s", method_name, exc)
        return None
    except Exception:
        logger.exception("Unexpected error in %s", method_name)
        return None


def get_machine_status_color(status):
    """Retain the existing public helper for other modules."""
    return frontend_config.get_status_colors().get(status, COLORS.get(status, MUTED))


def show_custom_loader(message="Loading Dashboard", submessage="Fetching machine data and analytics"):
    st.markdown(
        f'<div class="fs-loader"><span class="fs-loader-dot"></span><div>'
        f'<div class="fs-loader-title">{escape(str(message))}</div>'
        f'<div class="fs-muted">{escape(str(submessage))}</div></div></div>',
        unsafe_allow_html=True,
    )


def _inject_dashboard_css():
    """Inject one self-contained dashboard stylesheet without printing CSS as text."""
    st.markdown("""<style>
    .fs-page-title { color:#17243A !important; font-size:29px; line-height:1.3; font-weight:750; margin:0 0 5px; }
    .fs-page-subtitle { color:#64748B !important; font-size:14px; margin:0 0 30px; }
    .fs-section-title { color:#17243A !important; font-size:19px; font-weight:700; margin:28px 0 14px; }
    .fs-metric { box-sizing:border-box; min-width:0; background:#FFFFFF !important; border:1px solid #E2E8F0;
        border-radius:12px; padding:20px 18px; min-height:148px; margin:0;
        box-shadow:0 2px 8px rgba(23,36,58,.04); overflow:hidden; }
    .fs-metric-top { display:flex; align-items:center; justify-content:space-between; gap:8px; }
    .fs-metric-label { color:#64748B !important; font-size:11px; font-weight:700; text-transform:uppercase;
        letter-spacing:.05em; line-height:1.4; }
    .fs-metric-value { color:#17243A !important; font-size:clamp(23px,2vw,29px); line-height:1.25;
        font-weight:750; margin:20px 0 9px; overflow-wrap:anywhere; }
    .fs-metric-note { color:#64748B !important; font-size:12px; line-height:1.4; }
    .fs-metric-icon { width:34px; height:34px; flex:0 0 34px; border-radius:9px;
        display:flex; align-items:center; justify-content:center; font-size:17px; font-weight:700; }
    .fs-risk-card { box-sizing:border-box; background:#FFFFFF !important; border:1px solid #E2E8F0;
        border-top:3px solid #2457C5; border-radius:12px; padding:24px; min-height:156px; margin-bottom:18px; }
    .fs-risk-card h4 { color:#17243A !important; font-size:16px; font-weight:700; margin:0 0 12px; }
    .fs-risk-count { font-size:27px; font-weight:750; margin-bottom:8px; }
    .fs-muted { color:#64748B !important; font-size:13px; }
    .fs-risk-machine { color:#475569 !important; font-size:13px; padding:10px 0;
        border-top:1px solid #EDF1F7; overflow-wrap:anywhere; }
    .fs-risk-machine strong { color:#17243A !important; }
    .fs-loader { display:flex; align-items:center; gap:12px; background:#FFFFFF;
        border:1px solid #E2E8F0; border-radius:10px; padding:14px 18px; margin-bottom:16px; }
    .fs-loader-dot { width:10px; height:10px; border-radius:50%; background:#2457C5; }
    .fs-loader-title { color:#17243A !important; font-weight:650; font-size:14px; }
    /* A single CSS grid owns metric sizing: no mismatched Streamlit columns. */
    .fs-metric-grid { display:grid; grid-template-columns:repeat(5,minmax(0,1fr));
        gap:16px; width:100%; margin:0 0 16px; align-items:stretch; }
    .fs-sensor-grid { grid-template-columns:repeat(4,minmax(0,1fr)); margin-top:0; }
    .fs-metric-label { overflow-wrap:anywhere; }
    /* Plotly already provides its own internal margins; padding its outer box
       makes the plot wider than the available column on some screen widths. */
    [data-testid="stPlotlyChart"] { box-sizing:border-box !important; width:100% !important;
        max-width:100% !important; min-width:0 !important; overflow:hidden !important;
        background:#FFFFFF; border:1px solid #E2E8F0;
        border-radius:12px; padding:8px !important; margin-bottom:8px; }
    [data-testid="stPlotlyChart"] > div { max-width:100% !important; }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { min-width:0; }
    @media (max-width:1050px) {
        .fs-metric-grid { grid-template-columns:repeat(3,minmax(0,1fr)); }
        .fs-sensor-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
    }
    @media (max-width:600px) {
        .fs-metric-grid, .fs-sensor-grid { grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }
        .fs-metric { padding:16px 12px; min-height:132px; }
        .fs-metric-value { font-size:23px; }
    }
    @media (max-width:800px) {
        .fs-page-title { font-size:24px; }
        .fs-metric { min-height:132px; padding:12px; }
        .fs-metric-value { font-size:24px; }
    }
    </style>""", unsafe_allow_html=True)


def _number(machine, key):
    """Return a finite reading or None when a sensor has no data."""
    try:
        raw = machine.get(key)
        if raw is None or raw == "":
            return None
        value = float(raw)
        return value if pd.notna(value) and math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def _status(machine):
    """Never classify missing/unknown risk as Low."""
    value = str(machine.get("status", "Unknown")).strip().title()
    return value if value in COLORS else "Unknown"


def _sensor_text(machine, key, unit=""):
    value = _number(machine, key)
    return f"{value:.1f}{unit}" if value is not None else "—"


def _metric_html(label, value, note, icon, accent):
    """Return one card for a responsive HTML grid."""
    return (
        f'<div class="fs-metric"><div class="fs-metric-top">'
        f'<div class="fs-metric-label">{escape(str(label))}</div>'
        f'<div class="fs-metric-icon" style="background:{accent}16;color:{accent}">{escape(str(icon))}</div>'
        f'</div><div class="fs-metric-value">{escape(str(value))}</div>'
        f'<div class="fs-metric-note">{escape(str(note))}</div></div>'
    )


def _render_metric(label, value, note, icon, accent):
    """Preserve the original helper for compatibility."""
    st.markdown(_metric_html(label, value, note, icon, accent), unsafe_allow_html=True)


def _render_metric_grid(items, sensor=False):
    """Render cards in one contiguous grid, independent of Streamlit column gaps."""
    grid_class = "fs-metric-grid fs-sensor-grid" if sensor else "fs-metric-grid"
    html = f'<div class="{grid_class}">' + ''.join(_metric_html(*item) for item in items) + '</div>'
    st.markdown(html, unsafe_allow_html=True)


def _style_chart(fig):
    """Apply readable axis, title, and legend colours after each chart's layout."""
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Arial, sans-serif", color=TEXT, size=12),
        title_font=dict(color=TEXT, size=17),
        legend=dict(font=dict(color=TEXT, size=11)),
    )
    fig.update_xaxes(color=MUTED, tickfont=dict(color=MUTED), title_font=dict(color="#475569"))
    fig.update_yaxes(color=MUTED, tickfont=dict(color=MUTED), title_font=dict(color="#475569"))
    return fig


def show_dashboard_page():
    """Render the ForgeSight dashboard."""
    logger.info("Dashboard page started")
    _inject_dashboard_css()
    st.markdown(
        '<div class="fs-page-title">Manufacturing Overview</div>'
        '<div class="fs-page-subtitle">Monitor equipment health, sensor readings and maintenance risk.</div>',
        unsafe_allow_html=True,
    )
    with st.spinner("Loading machine data..."):
        machines_data = get_service_data("get_machines")
    if machines_data is None:
        st.error("Unable to load machine data. Check the service connection and try refreshing the page.")
        if st.button("Retry", type="primary"):
            get_service_data.clear()
            st.rerun()
        return
    machines = machines_data.get("machines", [])
    if not isinstance(machines, list):
        st.error("The machine service returned data in an unexpected format.")
        return
    show_system_overview_cards(machines)
    show_machine_analytics_charts(machines)
    show_risk_analysis(machines)
    try:
        footer = frontend_config.get_footer_config()
        version = footer.get("app_version", "")
        powered_by = footer.get("powered_by", "ForgeSight")
    except Exception:
        version, powered_by = "", "ForgeSight"
    st.markdown(
        f'<div style="text-align:center;color:#64748B;font-size:12px;'
        f'border-top:1px solid #E2E8F0;padding-top:18px;margin-top:28px;">'
        f'ForgeSight · Manufacturing Predictive Maintenance {escape(str(version))}'
        f'<div>{escape(str(powered_by))} · Updated {datetime.now().strftime("%d %b %Y, %H:%M:%S")}</div></div>',
        unsafe_allow_html=True,
    )


def show_system_overview_cards(machines):
    """Render overview metrics and risk distribution charts."""
    total = len(machines)
    high = sum(1 for m in machines if _status(m) == "High")
    medium = sum(1 for m in machines if _status(m) == "Medium")
    low = sum(1 for m in machines if _status(m) == "Low")

    unknown = sum(1 for m in machines if _status(m) == "Unknown")

    def average(key):
        values = [_number(m, key) for m in machines]
        valid = [value for value in values if value is not None]
        return sum(valid) / len(valid) if valid else None

    def avg_text(key, unit=""):
        value = average(key)
        return f"{value:.1f}{unit}" if value is not None else "—"

    st.markdown('<div class="fs-section-title">System Overview</div>', unsafe_allow_html=True)
    risk_items = [
        ("Total Machines", total, "Registered equipment", "▤", PRIMARY),
        ("High Risk", high, "Requires attention", "!", COLORS["High"]),
        ("Medium Risk", medium, "Maintenance recommended", "↗", COLORS["Medium"]),
        ("Low Risk", low, "Operating normally", "✓", COLORS["Low"]),
        ("Data Unavailable", unknown, "Missing sensor readings", "—", COLORS["Unknown"]),
    ]
    _render_metric_grid(risk_items)

    sensor_items = [
        ("Avg Temperature", avg_text("temperature", " °C"), "Available readings only", "°", "#D9485F"),
        ("Avg Vibration", avg_text("vibration"), "Available readings only", "∿", "#7856C7"),
        ("Avg Current", avg_text("current", " A"), "Available readings only", "ϟ", "#B7791F"),
        ("Avg Pressure", avg_text("pressure", " bar"), "Available readings only", "◉", "#159A72"),
    ]
    _render_metric_grid(sensor_items, sensor=True)

    st.markdown('<div class="fs-section-title">Risk Distribution</div>', unsafe_allow_html=True)
    left, right = st.columns(2, gap="small")
    with left:
        if total:
            risk_df = pd.DataFrame({
                "Risk Level": ["Low Risk", "Medium Risk", "High Risk", "Data Unavailable"],
                "Machines": [low, medium, high, unknown],
            })
            fig = px.pie(
                risk_df, values="Machines", names="Risk Level", hole=0.62,
                color="Risk Level",
                color_discrete_map={
                    "Low Risk": COLORS["Low"],
                    "Medium Risk": COLORS["Medium"],
                    "High Risk": COLORS["High"],
                    "Data Unavailable": COLORS["Unknown"],
                },
            )
            fig.update_traces(
                textposition="inside", textinfo="percent",
                marker=dict(line=dict(color="#FFFFFF", width=3)),
                hovertemplate="%{label}<br>Machines: %{value}<br>%{percent}<extra></extra>",
            )
            fig.update_layout(
                **CHART_LAYOUT,
                title=dict(text="Equipment Risk Mix", x=0.02, font=dict(size=17, color=TEXT)),
                showlegend=True,
                legend=dict(orientation="h", y=-0.08, x=0),
            )
            st.plotly_chart(_style_chart(fig), use_container_width=True)
        else:
            st.info("No machine data is available to display.")
    with right:
        status_df = pd.DataFrame({
            "Risk Status": ["Low", "Medium", "High", "Unknown"],
            "Machines": [low, medium, high, unknown],
        })
        fig = px.bar(
            status_df, x="Risk Status", y="Machines", color="Risk Status",
            color_discrete_map=COLORS,
            category_orders={"Risk Status": ["Low", "Medium", "High", "Unknown"]},
        )
        fig.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Machine Count by Status", x=0.02, font=dict(size=17, color=TEXT)),
            showlegend=False,
            xaxis_title="Risk Status", yaxis_title="Number of Machines",
            yaxis=dict(gridcolor=GRID, rangemode="tozero", dtick=1),
            xaxis=dict(showgrid=False),
        )
        fig.update_traces(marker_line_width=0, hovertemplate="%{x}<br>Machines: %{y}<extra></extra>")
        st.plotly_chart(_style_chart(fig), use_container_width=True)


def show_machine_analytics_charts(machines):
    """Display sensor reading distributions."""
    st.markdown('<div class="fs-section-title">Sensor Data Trends</div>', unsafe_allow_html=True)
    if not machines:
        st.info("Sensor charts will appear when machine readings are available.")
        return
    left, right = st.columns(2, gap="small")
    chart_specs = [
        (left, "temperature", "Temperature Distribution", "Temperature (°C)", "#D9485F"),
        (right, "vibration", "Vibration Distribution", "Vibration Level", "#7856C7"),
    ]
    for col, key, title, axis_label, color in chart_specs:
        with col:
            values = [_number(m, key) for m in machines]
            values = [value for value in values if value is not None]
            if not values:
                st.info(f"No available {key} readings to chart.")
                continue
            df = pd.DataFrame({axis_label: values})
            fig = px.histogram(df, x=axis_label, nbins=16, color_discrete_sequence=[color])
            fig.update_layout(
                **CHART_LAYOUT,
                title=dict(text=title, x=0.02, font=dict(size=17, color=TEXT)),
                xaxis_title=axis_label, yaxis_title="Machine Count",
                showlegend=False, bargap=0.12,
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor=GRID, rangemode="tozero"),
            )
            fig.update_traces(
                marker_line_color="#FFFFFF", marker_line_width=1,
                hovertemplate=f"{axis_label}: %{{x}}<br>Count: %{{y}}<extra></extra>",
            )
            st.plotly_chart(_style_chart(fig), use_container_width=True)


def show_risk_analysis(machines):
    """Show machine summaries and an expandable list of remaining machines."""
    st.markdown(
        '<div class="fs-section-title">Maintenance Risk Analysis</div>',
        unsafe_allow_html=True,
    )
    groups = [
        ("High Risk", "High", COLORS["High"], "Prioritize inspection"),
        ("Medium Risk", "Medium", COLORS["Medium"], "Schedule maintenance"),
        ("Low Risk", "Low", COLORS["Low"], "Continue monitoring"),
    ]
    columns = st.columns(3, gap="small")
    for col, (title, status, color, description) in zip(columns, groups):
        matching = [m for m in machines if _status(m) == status]
        with col:
            st.markdown(
                f'<div class="fs-risk-card" style="border-top-color:{color}">'
                f'<h4 style="font-size:15px;margin-bottom:8px">{escape(title)}</h4>'
                f'<div class="fs-risk-count" style="color:{color};font-size:30px">{len(matching)}</div>'
                f'<div class="fs-muted" style="font-size:12px">{escape(description)}</div></div>',
                unsafe_allow_html=True,
            )
            if not matching:
                st.markdown(
                    '<div style="color:#64748B;font-size:12px;margin-top:10px">'
                    'No machines in this category.</div>',
                    unsafe_allow_html=True,
                )
                continue

            for machine in matching[:5]:
                machine_id = escape(str(machine.get("machine_id", "Unknown machine")))
                temperature = _sensor_text(machine, "temperature", " °C")
                vibration = _sensor_text(machine, "vibration")
                st.markdown(
                    '<div style="background:#FFFFFF;border:1px solid #E2E8F0;'
                    'border-radius:9px;padding:12px;margin:0 0 8px">'
                    f'<div style="color:#17243A;font-size:13px;font-weight:700">{machine_id}</div>'
                    '<div style="color:#64748B;font-size:12px;margin-top:10px">'
                    f'Temperature: {temperature} &nbsp; | &nbsp; '
                    f'Vibration: {vibration}</div></div>',
                    unsafe_allow_html=True,
                )

            remaining = len(matching) - 5
            if remaining > 0:
                with st.expander(f"View {remaining} more machines"):
                    for machine in matching[5:]:
                        machine_id = escape(str(machine.get("machine_id", "Unknown machine")))
                        temperature = _sensor_text(machine, "temperature", " °C")
                        vibration = _sensor_text(machine, "vibration")
                        st.markdown(
                            '<div style="background:#FFFFFF;border:1px solid #E2E8F0;'
                            'border-radius:9px;padding:12px;margin-bottom:8px">'
                            f'<div style="color:#17243A;font-size:13px;font-weight:700">{machine_id}</div>'
                            '<div style="color:#64748B;font-size:12px;margin-top:10px">'
                            f'Temperature: {temperature} &nbsp; | &nbsp; '
                            f'Vibration: {vibration}</div></div>',
                            unsafe_allow_html=True,
                        )

    unavailable = [m for m in machines if _status(m) == "Unknown"]
    if unavailable:
        st.markdown('<div class="fs-section-title">Machines Requiring Sensor Data</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="fs-muted" style="margin-bottom:18px">'
            'These machines cannot receive a reliable risk assessment until sensor readings are available.'
            '</div>', unsafe_allow_html=True,
        )
        for machine in unavailable:
            machine_id = escape(str(machine.get("machine_id", "Unknown machine")))
            st.markdown(
                '<div style="background:#FFFFFF;border:1px solid #E2E8F0;'
                'border-left:3px solid #64748B;border-radius:10px;padding:18px 21px;margin-bottom:12px">'
                f'<div style="color:#17243A;font-weight:700">{machine_id}</div>'
                '<div style="color:#64748B;font-size:12px;margin-top:7px">'
                'Data unavailable · Sensor readings required before prediction</div></div>',
                unsafe_allow_html=True,
            )
