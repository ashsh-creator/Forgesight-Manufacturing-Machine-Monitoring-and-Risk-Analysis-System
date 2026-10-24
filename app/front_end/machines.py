
"""ForgeSight Machines Page.

Equipment directory, sensor readings and machine navigation.
Uses the existing machine service and application router.
"""

import os
import sys
import math
from datetime import datetime
from html import escape

import streamlit as st

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from utils.logger_config import get_logger
from config.front_end_config import frontend_config
from services.machines_service import machines_service, ServiceException

logger = get_logger(__name__)

PRIMARY = "#2457C5"
TEXT = "#17243A"
MUTED = "#64748B"

STATUS_COLORS = {
    "High": "#D9485F",
    "Medium": "#D99119",
    "Low": "#159A72",
    "Unknown": "#64748B",
}


@st.cache_data(ttl=frontend_config.CACHE_TTL)
def get_service_data(method_name, *args, **kwargs):
    """Fetch data using the existing service interface."""
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
    """Retain the existing public helper."""
    return STATUS_COLORS.get(
        str(status).title(),
        STATUS_COLORS["Unknown"]
    )


def show_custom_loader(
    message="Loading Machines",
    submessage="Fetching machine data"
):
    """Display a simple loading message."""
    st.info(f"{message} — {submessage}")


def _format_sensor(machine, key, unit=""):
    """Display a real numeric reading or a dash for unavailable data."""
    value = machine.get(key)
    if value is None or isinstance(value, bool):
        return "—"
    try:
        number = float(value)
        if not math.isfinite(number):
            return "—"
        return f"{number:.1f}{unit}"
    except (ValueError, TypeError, OverflowError):
        return "—"


def _status(machine):
    """Normalize machine risk status."""
    value = str(machine.get("status", "Unknown")).strip().title()
    return value if value in STATUS_COLORS else "Unknown"


def _format_reading(value):
    """Format machine timestamps for easier reading."""
    if not value:
        return "Not available"

    try:
        parsed = datetime.fromisoformat(str(value))
        return parsed.strftime("%d %b %Y, %I:%M %p")
    except (ValueError, TypeError):
        return str(value)


def _inject_machines_css():
    """ForgeSight Machines page styling."""

    st.markdown(
        """
        <style>

        .fs-machines-title {
            font-size: 29px;
            font-weight: 750;
            color: #17243A !important;
            margin: 0 0 5px;
            line-height: 1.3;
        }

        .fs-machines-subtitle {
            color: #64748B !important;
            font-size: 14px;
            margin-bottom: 31px;
        }

        .fs-machines-section {
            font-size: 19px;
            font-weight: 700;
            color: #17243A !important;
            margin: 22px 0 14px;
        }

        .fs-machine-stat {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 23px 21px;
            min-height: 132px;
            margin-bottom: 10px;
            box-shadow: 0 2px 8px rgba(23,36,58,.035);
        }

        .fs-machine-stat-label {
            color: #64748B !important;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: .05em;
            text-transform: uppercase;
        }

        .fs-machine-stat-value {
            font-size: 29px;
            font-weight: 750;
            margin-top: 17px;
            color: #17243A !important;
        }

        .fs-equipment-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 15px 17px;
            margin-bottom: 8px;
            min-height: 119px;
        }

        .fs-machine-name {
            font-size: 15px;
            font-weight: 750;
            color: #17243A !important;
        }

        .fs-machine-date {
            font-size: 11px;
            color: #64748B !important;
            margin-top: 8px;
            line-height: 1.5;
        }

        .fs-status {
            display: inline-block;
            padding: 7px 13px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
        }

        .fs-sensor-label {
            color: #64748B !important;
            font-size: 10px;
            text-transform: uppercase;
            font-weight: 650;
            letter-spacing: .04em;
            margin-bottom: 9px;
        }

        .fs-sensor-value {
            color: #17243A !important;
            font-size: 14px;
            font-weight: 700;
        }

        /* Only equipment directory cards; leave header and page containers alone. */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.fs-machine-name) {
            padding: 22px 24px !important;
            border-radius: 13px !important;
        }
        .fs-machine-card-spacer { height: 10px; }
        .fs-sensor-row-spacer { height: 16px; }
        @media (max-width: 700px) {
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.fs-machine-name) {
                padding: 16px !important;
            }
        }

        .fs-machine-footer {
            color: #64748B !important;
            font-size: 12px;
            text-align: center;
            padding: 18px 0;
            border-top: 1px solid #E2E8F0;
            margin-top: 25px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


def _summary_card(label, value, color=TEXT):
    """Render a compact overview card."""

    st.markdown(
        f'<div class="fs-machine-stat">'
        f'<div class="fs-machine-stat-label">{escape(str(label))}</div>'
        f'<div class="fs-machine-stat-value" style="color:{color}!important">'
        f'{escape(str(value))}</div>'
        '</div>',
        unsafe_allow_html=True
    )


def _open_machine(machine_id):
    """Open the existing machine details page."""

    st.session_state.selected_machine = machine_id
    st.session_state.current_page = "machine_details"

    # Remove stale URL navigation parameters.
    for key in ("page", "machine_id"):
        if key in st.query_params:
            del st.query_params[key]

    st.rerun()


def _render_machine_card(machine, index):
    """Render an equipment card with sensor readings."""

    machine_id = str(machine.get("machine_id", "Unknown"))
    status = _status(machine)
    color = get_machine_status_color(status)

    status_backgrounds = {
        "High": "#FFF1F2",
        "Medium": "#FFF8E8",
        "Low": "#ECFDF5",
        "Unknown": "#F1F5F9",
    }

    background = status_backgrounds.get(status, "#F1F5F9")

    # Top section
    name_col, status_col, action_col = st.columns(
        [4, 2, 2],
        gap="small",
        vertical_alignment="center"
    )

    with name_col:
        st.markdown(
            '<div class="fs-machine-name">'
            f'{escape(machine_id)}</div>'
            '<div class="fs-machine-date">'
            f'Last reading: {escape(_format_reading(machine.get("last_reading")))}'
            '</div>',
            unsafe_allow_html=True
        )

    with status_col:
        st.markdown(
            f'<span class="fs-status" style="background:{background};'
            f'color:{color}">{escape("Data Unavailable" if status == "Unknown" else status + " Risk")}</span>',
            unsafe_allow_html=True
        )

    with action_col:
        if st.button(
            "View Details →",
            key=f"fs_machine_details_{index}",
            use_container_width=True
        ):
            _open_machine(machine_id)

    st.markdown('<div class="fs-sensor-row-spacer"></div>', unsafe_allow_html=True)

    # Sensor readings
    sensor_cols = st.columns(4, gap="medium")

    readings = [
        ("Temperature", _format_sensor(machine, "temperature", " °C")),
        ("Vibration", _format_sensor(machine, "vibration")),
        ("Current", _format_sensor(machine, "current", " A")),
        ("Pressure", _format_sensor(machine, "pressure", " bar")),
    ]

    for col, (label, value) in zip(sensor_cols, readings):
        with col:
            st.markdown(
                f'<div class="fs-sensor-label">{escape(label)}</div>'
                f'<div class="fs-sensor-value">{escape(value)}</div>',
                unsafe_allow_html=True
            )


def show_machines_page():
    """Display the redesigned ForgeSight equipment directory."""

    logger.info("Machines page started")

    _inject_machines_css()

    # Page heading
    st.markdown(
        '<div class="fs-machines-title">Machines Overview</div>'
        '<div class="fs-machines-subtitle">'
        'Monitor equipment health, sensor readings and maintenance status.'
        '</div>',
        unsafe_allow_html=True
    )

    # Fetch machine data
    with st.spinner("Loading equipment data..."):
        machines_data = get_service_data("get_machines")

    if machines_data is None:
        st.error("Unable to load machine data.")

        if st.button("Retry", key="fs_machines_retry"):
            get_service_data.clear()
            st.rerun()

        return

    machines = machines_data.get("machines", [])

    if not isinstance(machines, list):
        st.error("The machine service returned an unexpected data format.")
        return

    # Overview metrics
    total = len(machines)

    high = sum(1 for m in machines if _status(m) == "High")
    medium = sum(1 for m in machines if _status(m) == "Medium")
    low = sum(1 for m in machines if _status(m) == "Low")

    summary_cols = st.columns(5, gap="medium")

    summaries = [
        ("Total Machines", total, TEXT),
        ("High Risk", high, STATUS_COLORS["High"]),
        ("Medium Risk", medium, STATUS_COLORS["Medium"]),
        ("Low Risk", low, STATUS_COLORS["Low"]),
        ("Data Unavailable", sum(1 for m in machines if _status(m) == "Unknown"), STATUS_COLORS["Unknown"]),
    ]

    for col, item in zip(summary_cols, summaries):
        with col:
            _summary_card(*item)

    # Equipment directory
    st.markdown(
        '<div class="fs-machines-section">Equipment Directory</div>',
        unsafe_allow_html=True
    )

    search_col, filter_col, refresh_col = st.columns(
        [4, 2, 1.3],
        gap="medium",
        vertical_alignment="bottom"
    )

    with search_col:
        search = st.text_input(
            "Search machines",
            placeholder="Search by Machine ID...",
            key="fs_machine_search"
        )

    with filter_col:
        risk_filter = st.selectbox(
            "Risk level",
            ["All", "High", "Medium", "Low", "Unknown"],
            key="fs_machine_risk_filter"
        )

    with refresh_col:
        if st.button(
            "Refresh",
            key="fs_machine_refresh",
            use_container_width=True
        ):
            get_service_data.clear()
            st.rerun()

    # Apply filters
    filtered = [
        machine
        for machine in machines
        if search.lower().strip() in str(
            machine.get("machine_id", "")
        ).lower()
        and (
            risk_filter == "All"
            or _status(machine) == risk_filter
        )
    ]

    st.caption(
        f"Showing {len(filtered)} of {total} machines"
    )

    if not filtered:
        st.info("No machines match your search or selected risk level.")

    # Render equipment cards
    for index, machine in enumerate(filtered):

        with st.container(border=True):
            _render_machine_card(machine, index)
        st.markdown('<div class="fs-machine-card-spacer"></div>', unsafe_allow_html=True)

    # Footer
    try:
        footer = frontend_config.get_footer_config()
        version = footer.get("app_version", "")
    except Exception:
        version = ""

    st.markdown(
        '<div class="fs-machine-footer">'
        f'ForgeSight · Manufacturing Predictive Maintenance '
        f'{escape(str(version))}'
        f' · Updated {datetime.now().strftime("%d %b %Y, %H:%M")}'
        '</div>',
        unsafe_allow_html=True
    )
