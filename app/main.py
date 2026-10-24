
"""ForgeSight application entry point."""

import os
import sys
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), 'front_end'))

from front_end.dashboard import show_dashboard_page
from front_end.machines import show_machines_page
from front_end.machine_details import show_machine_details_page
from front_end.ml_prediction import show_ml_prediction_page
from front_end.header import create_header
from utils.css_styles import get_common_styles, get_dashboard_styles
from utils.logger_config import get_logger

logger = get_logger(__name__)

# Browser tab configuration
st.set_page_config(
    page_title="ForgeSight",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def main():
    """Main application entry point."""
    logger.info("ForgeSight application started")

    try:
        st.markdown(get_common_styles(), unsafe_allow_html=True)
        st.markdown(get_dashboard_styles(), unsafe_allow_html=True)

        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"

        if "selected_machine" not in st.session_state:
            st.session_state.selected_machine = None

        create_header()

        page = st.session_state.current_page
        logger.info("Routing to page: %s", page)

        if page == "dashboard":
            show_dashboard_page()

        elif page == "machines":
            show_machines_page()

        elif page == "machine_details":
            show_machine_details_page()

        elif page == "ml_prediction":
            show_ml_prediction_page()

        else:
            logger.warning(
                "Unknown page %s; showing dashboard", page
            )
            st.session_state.current_page = "dashboard"
            show_dashboard_page()

    except Exception as exc:
        logger.exception("Application error")
        st.error(f"Application error: {exc}")
        raise


if __name__ == "__main__":
    main()
