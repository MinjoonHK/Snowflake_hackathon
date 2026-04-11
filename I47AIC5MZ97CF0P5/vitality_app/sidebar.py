from __future__ import annotations

import streamlit as st

from vitality_app.i18n import nav_label, t

TAB_KEYS = ["visitor", "consumer", "asset", "report", "backtest", "diagnostic"]

_SIDEBAR_CSS = """
<style>
/* ── shrink sidebar top padding so title sits close to header ── */
div[data-testid="stSidebarHeader"] {
    padding: 0.25rem 1rem !important;
}
[data-testid="stSidebarUserContent"] {
    padding-top: 0.5rem !important;
}

/* ── theme + locale row: even spacing between moon / En / Ko ── */
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type {
    gap: 0.5rem !important;
}

/* ── sidebar nav: full-width row highlight + full-row click (label fills container) ── */
section[data-testid="stSidebar"] .block-container {
    max-width: 100% !important;
}
section[data-testid="stSidebar"] div[data-testid="element-container"]:has([data-testid="stRadio"]) {
    width: 100% !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stRadio"]),
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"]:has([data-testid="stRadio"]) {
    width: 100% !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] {
    width: 100% !important;
    max-width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
    width: 100% !important;
    max-width: 100% !important;
    align-self: stretch !important;
}
/* RadioGroup: modern Streamlit uses data-testid="stRadioGroup" (Base Web); older builds use role="radiogroup" */
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"],
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {
    gap: 4px !important;
    width: 100% !important;
    max-width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: stretch !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] label,
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label {
    background-color: transparent;
    border-radius: 8px;
    padding: 10px 14px !important;
    margin: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
    align-self: stretch !important;
    display: flex !important;
    flex: 1 1 auto !important;
    box-sizing: border-box !important;
    cursor: pointer;
    transition: background-color 0.15s ease;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
    position: relative !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] label:hover,
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
    background-color: rgba(53, 158, 250, 0.10);
}
/* Selected row: Base Web does not set data-checked; use :has(input:checked) */
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] label:has(input[type="radio"]:checked),
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"],
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input[type="radio"]:checked) {
    background-color: #359efa !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] label:has(input[type="radio"]:checked) p,
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] label:has(input[type="radio"]:checked) span,
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p,
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] span,
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input[type="radio"]:checked) p,
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input[type="radio"]:checked) span {
    color: #ffffff !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] label p,
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label p {
    font-size: 15px !important;
    color: #989ba2 !important;
    font-weight: 500 !important;
    text-align: center !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
/* Hide default radio knob; row background shows selection (input stays for :checked / a11y) */
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] label input[type="radio"] + div,
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] label > div,
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label > div {
    flex: 0 1 auto !important;
    width: auto !important;
    max-width: 100% !important;
    min-width: 0 !important;
    text-align: center !important;
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 0.35em !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] label input[type="radio"],
section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label input[type="radio"] {
    position: absolute !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    pointer-events: none !important;
}
</style>
"""


def render_sidebar() -> str:
    st.session_state.setdefault("locale", "ko")
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    st.sidebar.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)

    icon = "\u2600\ufe0f" if st.session_state.dark_mode else "\U0001f319"
    loc = st.session_state.get("locale", "ko")

    c_theme, c_en, c_ko = st.sidebar.columns(3)
    with c_theme:
        if st.button(
            icon,
            key="theme_toggle",
            use_container_width=True,
        ):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    with c_en:
        if st.button(
            "En",
            key="locale_en",
            use_container_width=True,
            type="primary" if loc == "en" else "secondary",
        ):
            if loc != "en":
                st.session_state.locale = "en"
                st.rerun()
    with c_ko:
        if st.button(
            "Ko",
            key="locale_ko",
            use_container_width=True,
            type="primary" if loc == "ko" else "secondary",
        ):
            if loc != "ko":
                st.session_state.locale = "ko"
                st.rerun()

    st.sidebar.markdown(t("sidebar.title"))
    st.sidebar.markdown(
        f"<p style='margin-top:-8px;font-size:12px;color:var(--color-neutral-40)'>{t('sidebar.tagline')}</p>",
        unsafe_allow_html=True,
    )
    st.sidebar.divider()

    selected_key = st.sidebar.radio(
        "menu",
        TAB_KEYS,
        format_func=nav_label,
        label_visibility="collapsed",
    )

    return selected_key


def render_footer() -> None:
    st.sidebar.divider()
    st.sidebar.caption(t("footer.built"))
    st.sidebar.caption(t("footer.data"))
