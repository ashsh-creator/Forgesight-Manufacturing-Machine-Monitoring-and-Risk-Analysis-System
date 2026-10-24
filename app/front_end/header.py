"""ForgeSight header and session-state navigation."""
import streamlit as st


def _navigate(page):
    st.session_state.current_page = page
    for key in ('page', 'machine_id'):
        if key in st.query_params:
            del st.query_params[key]
    st.rerun()


def create_header():
    requested_page = st.query_params.get('page')
    allowed_pages = ('dashboard', 'machines', 'machine_details', 'ml_prediction')
    if requested_page in allowed_pages:
        if requested_page == 'machine_details':
            machine_id = st.query_params.get('machine_id')
            if machine_id is not None:
                st.session_state.selected_machine = machine_id
        if st.session_state.get('current_page') != requested_page:
            st.session_state.current_page = requested_page
            st.rerun()

    current_page = st.session_state.get('current_page', 'dashboard')
    st.markdown('''<style>
    .fs-header-brand{display:flex;align-items:center;gap:12px;min-height:48px}
    .fs-header-mark{width:42px;height:42px;flex:0 0 42px;border-radius:11px;
      display:flex;align-items:center;justify-content:center;background:#2457C5;
      color:white;font-size:25px;font-weight:800;line-height:1}
    .fs-header-name{font-size:21px;font-weight:800;color:#17243A!important;
      line-height:1.2;letter-spacing:-.03em}
    .fs-header-tagline{font-size:11px;color:#64748B!important;margin-top:3px}
    div[data-testid="stButton"] button[kind="primary"]{
      background:#EDF3FF!important;color:#2457C5!important;border:1px solid #C8D8FC!important}
    div[data-testid="stButton"] button[kind="primary"]:hover{
      background:#DCE8FF!important;color:#1945A5!important}
    </style>''', unsafe_allow_html=True)

    with st.container(border=True):
        brand, dashboard_col, machines_col, ml_col = st.columns(
            [5, 1.4, 1.4, 1.7], gap='small', vertical_alignment='center'
        )
        with brand:
            st.markdown(
                '<div class="fs-header-brand"><div class="fs-header-mark">⌁</div>'
                '<div><div class="fs-header-name">ForgeSight</div>'
                '<div class="fs-header-tagline">Manufacturing Intelligence</div>'
                '</div></div>', unsafe_allow_html=True
            )
        items = (
            (dashboard_col, 'Dashboard', 'dashboard', current_page == 'dashboard'),
            (machines_col, 'Machines', 'machines', current_page in ('machines', 'machine_details')),
            (ml_col, 'ML Prediction', 'ml_prediction', current_page == 'ml_prediction'),
        )
        for column, label, target, active in items:
            with column:
                if st.button(label, key=f'fs_header_{target}',
                             type='primary' if active else 'secondary',
                             use_container_width=True):
                    if not active:
                        _navigate(target)
