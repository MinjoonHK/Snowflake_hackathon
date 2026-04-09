# Urban Vitality Index — Streamlit Project

## Project Overview
Snowflake Hackathon project. A Streamlit dashboard that visualizes Seoul's urban vitality index using data from Snowflake (SPH/GRANDATA).

## Tech Stack
- **Frontend**: Streamlit (Python)
- **Backend/Data**: Snowflake (via `snowflake.snowpark`)
- **Charts**: Altair, Pydeck (map)
- **Entry point**: `I47AIC5MZ97CF0P5/streamlit_app.py`

## Project Structure
```
I47AIC5MZ97CF0P5/
├── streamlit_app.py          # Entry point
├── .streamlit/config.toml    # Streamlit config + theme
├── vitality_app/
│   ├── data.py               # Snowflake query functions (cached)
│   ├── indices.py            # Custom index computation
│   ├── session.py            # Snowflake session singleton
│   ├── sidebar.py            # Sidebar UI + SidebarState dataclass
│   └── tabs/
│       ├── map_tab.py        # 활력 지도 tab
│       └── trend_tab.py      # 트렌드 분석 tab
```

## Design System

### Color Palette
```python
# Cool Neutral
NEUTRAL = {
    10: "#ffffff", 20: "#f7f7f8", 30: "#dbdcdf",
    40: "#989ba2", 50: "#70737c", 60: "#5a5c63",
    70: "#292a2d", 80: "#171719", 90: "#0f0f10", 100: "#000000"
}

# Primary Blue
PRIMARY = {
    10: "#e3effa", 20: "#cae4fa", 30: "#98ccfa",
    40: "#359efa", 50: "#1a4e7c", 60: "#0f2c45"
}

# Success Green
SECONDARY = {
    10: "#c9e1b6", 20: "#b0e189", 30: "#96e15c",
    40: "#7de12f", 50: "#62ad24", 60: "#457a19"
}

# Error Red
ERROR = {
    10: "#ffebeb", 20: "#ffd1d1", 30: "#ffb8b8",
    40: "#ff8585", 50: "#ff5252", 60: "#993131"
}
```

### Typography
| Token | Value |
|-------|-------|
| heading1 | 28px |
| heading2 | 24px |
| heading3 | 20px |
| body1 | 18px |
| body2 | 16px |
| body3 | 14px |
| caption / action | 12px |
| line-height-heading | 132% |
| line-height-body | 150% |
| font-weight-bold | 700 |
| font-weight-semibold | 600 |
| font-weight-medium | 500 |
| font-weight-regular | 400 |

### Applying the Design System in Streamlit
Use `st.markdown()` with inline CSS or inject via `st.markdown("<style>...</style>", unsafe_allow_html=True)`.

Key mappings:
- Background: `--color-neutral-90` (#0f0f10) for dark mode base
- Surface cards: `--color-neutral-80` (#171719)
- Borders: `--color-neutral-70` (#292a2d)
- Primary text: `--color-neutral-10` (#ffffff)
- Secondary text: `--color-neutral-40` (#989ba2)
- Accent / CTA: `--color-primary-40` (#359efa)
- Positive trend: `--color-secondary-40` (#7de12f)
- Negative trend: `--color-error-50` (#ff5252)

## Coding Conventions
- Use `@st.cache_data(ttl=...)` for all Snowflake queries
- Session is a singleton — always use `get_session()` from `vitality_app.session`
- Each tab is a separate module with a `render(...)` function
- Dataclasses for passing state between components (see `SidebarState`)
- Korean UI labels (app is Korean-facing)

## Snowflake Schema
- Database: `SPH_DATA`
- Schema: `GRANDATA`
- Main view: `V_VITALITY_FINAL`
- Geo table: `M_SCCO_MST`
