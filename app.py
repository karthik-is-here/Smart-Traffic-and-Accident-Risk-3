import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

import config
import predictor
import maps

st.set_page_config(
    page_title="Kochi Traffic Intelligence",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [("sel_day","Monday"), ("sel_weather","Clear"),
              ("sel_area","Fort Kochi"), ("active_tab","congestion"),
              ("results", None), ("dark_mode", True)]:
    if k not in st.session_state:
        st.session_state[k] = v

dark = st.session_state.dark_mode

# ── Theme tokens ───────────────────────────────────────────────────────────────
if dark:
    BG          = "#0a0a0a"
    SURFACE     = "#111111"
    SURFACE2    = "#161616"
    BORDER      = "#222222"
    BORDER2     = "#2a2a2a"
    TEXT        = "#cccccc"
    TEXT_DIM    = "#555555"
    TEXT_BRIGHT = "#ffffff"
    ACCENT      = "#a3e635"
    ACCENT_DIM  = "#a3e63533"
    BTN_BG      = "#161616"
    BTN_COLOR   = "#666666"
    BTN_BORDER  = "#2a2a2a"
    MAP_TILES   = "CartoDB dark_matter"
else:
    BG          = "#f8f9fa"
    SURFACE     = "#ffffff"
    SURFACE2    = "#f1f3f5"
    BORDER      = "#e0e0e0"
    BORDER2     = "#d0d0d0"
    TEXT        = "#444444"
    TEXT_DIM    = "#999999"
    TEXT_BRIGHT = "#111111"
    ACCENT      = "#4a7c00"
    ACCENT_DIM  = "#4a7c0022"
    BTN_BG      = "#f1f3f5"
    BTN_COLOR   = "#555555"
    BTN_BORDER  = "#ddd"
    MAP_TILES   = "CartoDB positron"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Space Grotesk', sans-serif;
}}

/* ── Hide ALL Streamlit chrome ── */
#MainMenu                              {{ visibility: hidden !important; }}
footer                                 {{ visibility: hidden !important; }}
header                                 {{ visibility: hidden !important; }}
[data-testid="stDecoration"]           {{ display: none !important; }}
[data-testid="stToolbar"]              {{ display: none !important; }}
[data-testid="stStatusWidget"]         {{ display: none !important; }}
[data-testid="stHeader"]               {{ display: none !important; }}
[data-testid="collapsedControl"]       {{ display: none !important; }}

/* ── Base ── */
.stApp {{
    background: {BG} !important;
}}
.block-container {{
    padding-top: 0 !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {SURFACE} !important;
    border-right: 1px solid {BORDER} !important;
}}

/* ── All buttons ── */
.stButton > button {{
    background: {BTN_BG} !important;
    color: {BTN_COLOR} !important;
    border: 1px solid {BTN_BORDER} !important;
    border-radius: 6px !important;
    font-size: 11px !important;
    font-family: 'JetBrains Mono', monospace !important;
    padding: 7px 4px !important;
    transition: all 0.12s !important;
    letter-spacing: 0.3px !important;
}}
.stButton > button:hover {{
    background: {SURFACE2} !important;
    color: {ACCENT} !important;
    border-color: {ACCENT_DIM} !important;
}}

/* ── Slider ── */
[data-testid="stSlider"] [role="slider"] {{
    background: {ACCENT} !important;
    border: 2px solid {TEXT_BRIGHT} !important;
}}
[data-testid="stSlider"] > div > div > div {{
    background: {ACCENT} !important;
}}

/* ── Topbar ── */
.topbar {{
    background: {SURFACE};
    border-bottom: 1px solid {BORDER};
    padding: 11px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0;
}}
.topbar-brand {{ display: flex; align-items: center; gap: 12px; }}
.topbar-icon {{
    width: 34px; height: 34px;
    background: {ACCENT};
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; flex-shrink: 0;
}}
.topbar-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 17px; font-weight: 700;
    color: {TEXT_BRIGHT}; letter-spacing: -0.3px; line-height: 1;
}}
.topbar-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; color: {TEXT_DIM};
    letter-spacing: 1.5px; text-transform: uppercase; margin-top: 2px;
}}
.topbar-right {{ display: flex; align-items: center; gap: 12px; }}
.topbar-badge {{
    display: flex; align-items: center; gap: 6px;
    background: {SURFACE2};
    border: 1px solid {BORDER2};
    border-radius: 20px; padding: 5px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: {ACCENT}; letter-spacing: 1px;
}}
.live-dot {{
    width: 6px; height: 6px; background: {ACCENT};
    border-radius: 50%; animation: pulse 2s ease-in-out infinite;
}}
@keyframes pulse {{
    0%,100% {{ opacity:1; box-shadow: 0 0 4px {ACCENT}; }}
    50%      {{ opacity:0.4; }}
}}

/* ── Sidebar labels ── */
.sb-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; letter-spacing: 2px; color: {TEXT_DIM};
    text-transform: uppercase; margin: 0 0 8px 0;
    padding-bottom: 6px; border-bottom: 1px solid {BORDER};
}}
.sb-section {{ padding: 12px 14px; border-bottom: 1px solid {BORDER}; }}
.sel-tag {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; color: {ACCENT};
    text-align: center; padding: 4px 0 6px 0; letter-spacing: 1px;
}}

/* ── Map ── */
.map-header {{
    background: {SURFACE};
    border: 1px solid {BORDER}; border-bottom: none;
    border-radius: 10px 10px 0 0; padding: 10px 16px;
    display: flex; align-items: center; justify-content: space-between;
}}
.map-header-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; letter-spacing: 2px; color: {TEXT_DIM}; text-transform: uppercase;
}}
.map-header-area {{
    font-size: 13px; font-weight: 600; color: {ACCENT};
}}

/* ── Stats panel ── */
.stats-panel {{
    background: {SURFACE}; border: 1px solid {BORDER};
    border-radius: 10px; padding: 14px;
}}
.stats-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; letter-spacing: 2px; color: {TEXT_DIM};
    text-transform: uppercase; margin-bottom: 12px;
    padding-bottom: 8px; border-bottom: 1px solid {BORDER};
}}

/* ── Metric cards ── */
.metric-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; }}
.metric-card {{
    background: {SURFACE2}; border: 1px solid {BORDER2};
    border-radius: 8px; padding: 10px 12px;
}}
.metric-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 8px; letter-spacing: 1.5px; color: {TEXT_DIM};
    text-transform: uppercase; margin-bottom: 5px;
}}
.metric-val {{ font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; line-height: 1; }}
.metric-unit {{ font-family: 'JetBrains Mono', monospace; font-size: 9px; color: {TEXT_DIM}; margin-top: 2px; }}

.c-green  {{ color: {'#a3e635' if dark else '#3a7500'}; }}
.c-yellow {{ color: {'#facc15' if dark else '#a16207'}; }}
.c-orange {{ color: {'#fb923c' if dark else '#c2410c'}; }}
.c-red    {{ color: {'#f87171' if dark else '#dc2626'}; }}
.c-white  {{ color: {TEXT_BRIGHT}; }}

/* ── Weather strip ── */
.wx-strip {{
    background: {SURFACE2}; border: 1px solid {BORDER2};
    border-radius: 8px; padding: 10px 12px; margin-bottom: 10px;
    display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
}}
.wx-key {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 8px; letter-spacing: 1px; color: {TEXT_DIM};
    text-transform: uppercase; margin-bottom: 2px;
}}
.wx-val {{ font-size: 15px; font-weight: 600; color: {TEXT_BRIGHT}; }}
.wx-val small {{ font-size: 10px; color: {TEXT_DIM}; font-weight: 400; }}

/* ── Alert box ── */
.alert-box {{
    background: {'#1a0a0a' if dark else '#fff5f5'};
    border: 1px solid {'#f8717133' if dark else '#fecaca'};
    border-left: 3px solid {'#f87171' if dark else '#ef4444'};
    border-radius: 8px; padding: 10px 12px; margin-bottom: 10px;
}}
.alert-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; letter-spacing: 1.5px;
    color: {'#f87171' if dark else '#dc2626'};
    text-transform: uppercase; margin-bottom: 6px;
}}
.alert-road {{
    font-size: 11px; color: {'#fca5a5' if dark else '#ef4444'};
    padding: 2px 0; border-bottom: 1px solid {'#2a1010' if dark else '#fee2e2'};
}}
.alert-road:last-child {{ border-bottom: none; }}

/* ── Info table ── */
.info-table {{
    background: {SURFACE2}; border: 1px solid {BORDER2}; border-radius: 8px; overflow: hidden;
}}
.info-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 7px 12px; border-bottom: 1px solid {BORDER}; font-size: 11px;
}}
.info-row:last-child {{ border-bottom: none; }}
.info-key {{ color: {TEXT_DIM}; font-family: 'JetBrains Mono', monospace; font-size: 10px; }}
.info-val {{ color: {TEXT}; font-weight: 500; }}
.info-val-accent {{ color: {ACCENT}; font-family: 'JetBrains Mono', monospace; }}

/* ── Road table ── */
.road-table {{ width: 100%; border-collapse: collapse; font-size: 11px; }}
.road-table th {{
    font-family: 'JetBrains Mono', monospace; font-size: 8px;
    letter-spacing: 1.5px; color: {TEXT_DIM}; text-transform: uppercase;
    padding: 6px 8px; border-bottom: 1px solid {BORDER}; text-align: left;
    background: {SURFACE};
}}
.road-table td {{
    padding: 6px 8px; border-bottom: 1px solid {BORDER};
    color: {TEXT}; font-family: 'Space Grotesk', sans-serif;
}}
.road-table tr:hover td {{ background: {SURFACE2}; color: {TEXT_BRIGHT}; }}

.badge {{
    display: inline-block; border-radius: 4px; padding: 2px 7px;
    font-size: 9px; font-weight: 600; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.5px;
}}
.badge-low      {{ background: {'#0f1f09' if dark else '#f0fdf4'}; color: {'#a3e635' if dark else '#166534'}; border: 1px solid {'#a3e63533' if dark else '#bbf7d0'}; }}
.badge-moderate {{ background: {'#1f1a09' if dark else '#fefce8'}; color: {'#facc15' if dark else '#854d0e'}; border: 1px solid {'#facc1533' if dark else '#fef08a'}; }}
.badge-high     {{ background: {'#1f0f09' if dark else '#fff7ed'}; color: {'#fb923c' if dark else '#c2410c'}; border: 1px solid {'#fb923c33' if dark else '#fed7aa'}; }}
.badge-veryhigh {{ background: {'#1f0909' if dark else '#fef2f2'}; color: {'#f87171' if dark else '#dc2626'}; border: 1px solid {'#f87171' if dark else '#fecaca'}; }}

.empty-state {{
    height: 420px; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background: {SURFACE2}; border-radius: 0 0 10px 10px; gap: 12px;
}}
.empty-icon {{ font-size: 40px; opacity: 0.3; }}
.empty-text {{
    font-family: 'JetBrains Mono', monospace; font-size: 10px;
    letter-spacing: 2px; color: {TEXT_DIM}; text-transform: uppercase;
    text-align: center; line-height: 2;
}}
</style>
""", unsafe_allow_html=True)

# ── Topbar ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
    <div class="topbar-brand">
        <div class="topbar-icon">🚦</div>
        <div>
            <div class="topbar-title">Kochi Traffic Intelligence</div>
            <div class="topbar-sub">ML-Powered Urban Mobility System · Kerala</div>
        </div>
    </div>
    <div class="topbar-right">
        <div class="topbar-badge">
            <div class="live-dot"></div>
            MODEL ACTIVE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # ── Dark / Light toggle ────────────────────────────────────────────────────
    st.markdown('<div class="sb-section"><div class="sb-label">Appearance</div>', unsafe_allow_html=True)
    toggle_label = "☀  Switch to Light Mode" if dark else "🌙  Switch to Dark Mode"
    if st.button(toggle_label, key="theme_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Day
    st.markdown('<div class="sb-section"><div class="sb-label">Day of Week</div>', unsafe_allow_html=True)
    days_short = ["MON","TUE","WED","THU","FRI","SAT","SUN"]
    cols_d = st.columns(3)
    for i, (short, full) in enumerate(zip(days_short, config.DAYS_OF_WEEK)):
        lbl = f"› {short}" if st.session_state.sel_day == full else short
        with cols_d[i % 3]:
            if st.button(lbl, key=f"day_{full}", use_container_width=True):
                st.session_state.sel_day = full
                st.rerun()
    st.markdown(f'<div class="sel-tag">› {st.session_state.sel_day.upper()}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Hour
    st.markdown('<div class="sb-section"><div class="sb-label">Hour of Day</div>', unsafe_allow_html=True)
    hour = st.slider("Hour", 0, 23, value=8, key="hour_slider", format="%d:00", label_visibility="collapsed")
    period = "NIGHT" if (hour >= 22 or hour <= 5) else "RUSH HOUR" if (7 <= hour <= 9 or 17 <= hour <= 20) else "OFF-PEAK"
    st.markdown(f'<div class="sel-tag">{hour:02d}:00 · {period}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Weather
    st.markdown('<div class="sb-section"><div class="sb-label">Weather</div>', unsafe_allow_html=True)
    wx_icons = {"Clear":"☀","Cloudy":"☁","Light Rain":"🌦","Heavy Rain":"🌧","Fog":"🌫"}
    cols_w = st.columns(2)
    for i, w in enumerate(config.WEATHER_OPTIONS):
        lbl = f"› {wx_icons[w]} {w}" if st.session_state.sel_weather == w else f"{wx_icons[w]} {w}"
        with cols_w[i % 2]:
            if st.button(lbl, key=f"wx_{w}", use_container_width=True):
                st.session_state.sel_weather = w
                st.rerun()
    st.markdown(f'<div class="sel-tag">› {st.session_state.sel_weather.upper()}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Location
    st.markdown('<div class="sb-section"><div class="sb-label">Location</div>', unsafe_allow_html=True)
    cols_a = st.columns(2)
    for i, area_opt in enumerate(config.AREA_ROADS.keys()):
        lbl = f"› {area_opt}" if st.session_state.sel_area == area_opt else area_opt
        with cols_a[i % 2]:
            if st.button(lbl, key=f"area_{area_opt}", use_container_width=True):
                st.session_state.sel_area = area_opt
                st.rerun()
    st.markdown(f'<div class="sel-tag">› {st.session_state.sel_area.upper()}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="padding:14px;">', unsafe_allow_html=True)
    predict_clicked = st.button("⚡  ANALYSE TRAFFIC", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Prediction ─────────────────────────────────────────────────────────────────
if predict_clicked:
    with st.spinner("Running ML models..."):
        try:
            results = predictor.predict_all_roads(
                st.session_state.sel_area,
                st.session_state.sel_day,
                st.session_state.get("hour_slider", 8),
                st.session_state.sel_weather
            )
            st.session_state.results = results
        except FileNotFoundError:
            st.error("❌ models/ folder not found. Train the model first.")
            st.stop()
        except Exception as e:
            st.error(f"❌ {e}")
            st.stop()
    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════
results = st.session_state.results
area    = st.session_state.sel_area

center_col, right_col = st.columns([3.2, 1.4], gap="medium")

# ── Center ─────────────────────────────────────────────────────────────────────
with center_col:
    st.markdown('<div style="padding:10px 4px 0 4px;">', unsafe_allow_html=True)

    tc, tr, _ = st.columns([1, 1, 3])
    with tc:
        if st.button("▣  CONGESTION", key="tab_cong", use_container_width=True):
            st.session_state.active_tab = "congestion"
            st.rerun()
    with tr:
        if st.button("⚠  RISK", key="tab_risk", use_container_width=True):
            st.session_state.active_tab = "risk"
            st.rerun()

    tab_label = "CONGESTION MAP" if st.session_state.active_tab == "congestion" else "ACCIDENT RISK MAP"
    st.markdown(f"""
    <div class="map-header" style="margin-top:8px;">
        <span class="map-header-label">{tab_label} · KOCHI DISTRICT</span>
        <span class="map-header-area">📍 {area}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div style="border:1px solid {BORDER};border-top:none;border-radius:0 0 10px 10px;overflow:hidden;">', unsafe_allow_html=True)
    if results:
        # Pass the current tile style to maps
        if st.session_state.active_tab == "congestion":
            m = maps.create_congestion_map(results, area, MAP_TILES)
        else:
            m = maps.create_risk_map(results, area, MAP_TILES)
        components.html(maps.map_to_html(m), height=440)
    else:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon">🗺</div>
            <div class="empty-text">Select parameters<br>and analyse traffic</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if results:
        df_key    = "congestion_level"  if st.session_state.active_tab == "congestion" else "accident_risk_level"
        score_key = "congestion_score"  if st.session_state.active_tab == "congestion" else "accident_risk_score"
        label     = "Congestion"        if st.session_state.active_tab == "congestion" else "Accident Risk"

        def badge(level):
            slug = level.lower().replace(" ", "")
            return f'<span class="badge badge-{slug}">{level}</span>'

        rows_html = "".join(
            f'<tr>'
            f'<td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{r["road_name"]}</td>'
            f'<td>{badge(r[df_key])}</td>'
            f'<td style="font-family:\'JetBrains Mono\',monospace;color:{ACCENT};font-size:11px">{r[score_key]}%</td>'
            f'<td style="color:{TEXT_DIM};font-family:\'JetBrains Mono\',monospace;font-size:10px">{r["current_speed_kmph"]} km/h</td>'
            f'</tr>'
            for r in sorted(results, key=lambda x: x[score_key], reverse=True)
        )

        st.markdown(f"""
        <div style="margin-top:10px;background:{SURFACE};border:1px solid {BORDER};border-radius:10px;
                    padding:10px 14px;max-height:170px;overflow-y:auto;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:2px;
                        color:{ACCENT};margin-bottom:8px;text-transform:uppercase;">
                {label} · {area}
            </div>
            <table class="road-table">
                <thead><tr><th>Road</th><th>Level</th><th>Score</th><th>Speed</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Right stats ────────────────────────────────────────────────────────────────
with right_col:
    st.markdown('<div style="padding:10px 4px 0 0;">', unsafe_allow_html=True)

    if results:
        high_cong = [r for r in results if r["congestion_level"]    in ["High","Very High"]]
        high_risk = [r for r in results if r["accident_risk_level"] in ["High","Very High"]]
        avg_cong  = round(sum(r["congestion_score"]    for r in results) / len(results), 1)
        avg_risk  = round(sum(r["accident_risk_score"] for r in results) / len(results), 1)
        avg_temp  = round(sum(r["temperature_c"]       for r in results) / len(results), 1)
        avg_rain  = round(sum(r["rainfall_mm"]         for r in results) / len(results), 1)
        avg_vis   = int(sum(r["visibility_m"]          for r in results) / len(results))
        avg_hum   = int(sum(r["humidity_pct"]          for r in results) / len(results))

        cc = "c-red" if len(high_cong) >= 3 else "c-yellow" if len(high_cong) >= 1 else "c-green"
        rc = "c-red" if len(high_risk) >= 3 else "c-yellow" if len(high_risk) >= 1 else "c-green"
        risk_css  = "c-red" if avg_risk > 50 else "c-yellow" if avg_risk > 30 else "c-green"
        risk_bar  = "#f87171" if avg_risk > 50 else "#facc15" if avg_risk > 30 else ACCENT

        st.markdown(f"""
        <div class="stats-panel">
            <div class="stats-title">Traffic Summary</div>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">High Cong.</div>
                    <div class="metric-val {cc}">{len(high_cong)}</div>
                    <div class="metric-unit">roads</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Avg Cong.</div>
                    <div class="metric-val c-yellow">{avg_cong}%</div>
                    <div class="metric-unit">score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Roads</div>
                    <div class="metric-val c-white">{len(results)}</div>
                    <div class="metric-unit">checked</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">High Risk</div>
                    <div class="metric-val {rc}">{len(high_risk)}</div>
                    <div class="metric-unit">roads</div>
                </div>
            </div>
        </div>

        <div style="margin-top:8px;">
        <div class="stats-panel">
            <div class="stats-title">Weather Conditions</div>
            <div class="wx-strip">
                <div>
                    <div class="wx-key">Temp</div>
                    <div class="wx-val">{avg_temp}°<small>C</small></div>
                </div>
                <div>
                    <div class="wx-key">Rain</div>
                    <div class="wx-val">{avg_rain}<small>mm</small></div>
                </div>
                <div>
                    <div class="wx-key">Visibility</div>
                    <div class="wx-val">{avg_vis}<small>m</small></div>
                </div>
                <div>
                    <div class="wx-key">Humidity</div>
                    <div class="wx-val">{avg_hum}<small>%</small></div>
                </div>
            </div>
            <div style="background:{SURFACE2};border:1px solid {BORDER2};border-radius:6px;padding:8px 12px;margin-top:4px;">
                <div class="wx-key" style="margin-bottom:4px;">Avg Risk Score</div>
                <div style="background:{BORDER};border-radius:3px;height:4px;">
                    <div style="width:{min(avg_risk,100)}%;height:4px;border-radius:3px;background:{risk_bar};"></div>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:4px;">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:{TEXT_DIM};">RISK</span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:{risk_bar};">{avg_risk}%</span>
                </div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        all_danger = list({{r["road_name"] for r in high_cong + high_risk}})
        if all_danger:
            road_rows = "".join(f'<div class="alert-road">▸ {r}</div>' for r in all_danger)
            st.markdown(f"""
            <div style="margin-top:8px;">
            <div class="alert-box">
                <div class="alert-title">⚠ Dangerous Roads</div>
                {road_rows}
            </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-top:8px;">
        <div class="stats-panel">
            <div class="stats-title">Session</div>
            <div class="info-table">
                <div class="info-row"><span class="info-key">AREA</span><span class="info-val">{st.session_state.sel_area}</span></div>
                <div class="info-row"><span class="info-key">DAY</span><span class="info-val">{st.session_state.sel_day}</span></div>
                <div class="info-row"><span class="info-key">TIME</span><span class="info-val-accent">{st.session_state.get('hour_slider',8):02d}:00</span></div>
                <div class="info-row"><span class="info-key">WEATHER</span><span class="info-val">{st.session_state.sel_weather}</span></div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="stats-panel" style="height:380px;display:flex;align-items:center;
             justify-content:center;flex-direction:column;gap:10px;">
            <div style="font-size:32px;opacity:0.2;">📊</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                        letter-spacing:2px;color:{TEXT_DIM};text-align:center;line-height:2;text-transform:uppercase;">
                Run analysis<br>to see stats
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
