"""
🏟️ نظام محاكاة إدارة الحشود - كأس العالم 2034
Crowd Management Simulation System - FIFA World Cup 2034 KSA
Team: [your name], ريماس، لمياء، لانا
Hackathon: #هاكاثون_صناع - Mega Future
"""

import streamlit as st
import numpy as np
import time
import random
from simulation import StadiumSimulation
from ai_engine import CrowdAIEngine
from ui_components import render_header, render_metrics, render_alerts, render_controls

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="WCSAC 2034 | نظام إدارة الحشود",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ──────────────────────────────────────────────
# Custom CSS – Saudi Green + Dark Dashboard
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Tajawal:wght@300;400;700&display=swap');

:root {
    --saudi-green:   #006C35;
    --saudi-light:   #00A550;
    --saudi-glow:    #00FF7F;
    --bg-primary:    #050D0A;
    --bg-secondary:  #0A1A12;
    --bg-card:       #0D2118;
    --bg-card2:      #071610;
    --border-green:  #006C35;
    --text-primary:  #E8F5E9;
    --text-muted:    #5A8A6A;
    --danger:        #FF3B30;
    --warning:       #FF9500;
    --white:         #FFFFFF;
}

/* Global Reset */
html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    direction: rtl;
}

.stApp { background-color: var(--bg-primary) !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 2rem 2rem 2rem !important; max-width: 100% !important; }

/* ── HEADER ── */
.header-banner {
    background: linear-gradient(135deg, #020D07 0%, #0A2015 50%, #020D07 100%);
    border: 1px solid var(--saudi-green);
    border-radius: 12px;
    padding: 1.2rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 0 40px rgba(0,108,53,0.3), inset 0 0 60px rgba(0,108,53,0.05);
    position: relative;
    overflow: hidden;
}

.header-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--saudi-light), var(--saudi-glow), var(--saudi-light), transparent);
    animation: scanline 3s linear infinite;
}

@keyframes scanline {
    0% { opacity: 0.4; }
    50% { opacity: 1; }
    100% { opacity: 0.4; }
}

.header-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.4rem;
    font-weight: 900;
    color: var(--saudi-light);
    letter-spacing: 2px;
    text-shadow: 0 0 20px rgba(0,165,80,0.8);
    margin: 0;
}

.header-subtitle {
    font-family: 'Tajawal', sans-serif;
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 4px;
}

.header-badge {
    background: var(--saudi-green);
    color: white;
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid var(--saudi-glow);
    box-shadow: 0 0 15px rgba(0,255,127,0.3);
    letter-spacing: 1px;
}

/* ── METRIC CARDS ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-green);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 20px rgba(0,108,53,0.15);
    transition: box-shadow 0.3s;
}

.metric-card:hover {
    box-shadow: 0 0 30px rgba(0,165,80,0.35);
}

.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--saudi-green), var(--saudi-glow), var(--saudi-green));
}

.metric-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.4rem;
    font-family: 'Orbitron', monospace;
}

.metric-value {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 900;
    color: var(--saudi-glow);
    text-shadow: 0 0 15px rgba(0,255,127,0.5);
    line-height: 1;
}

.metric-unit {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 3px;
}

.metric-danger .metric-value { color: var(--danger); text-shadow: 0 0 15px rgba(255,59,48,0.5); }
.metric-warning .metric-value { color: var(--warning); text-shadow: 0 0 15px rgba(255,149,0,0.5); }

/* ── MAIN PANELS ── */
.panel {
    background: var(--bg-card);
    border: 1px solid var(--border-green);
    border-radius: 10px;
    padding: 1.2rem;
    box-shadow: 0 0 20px rgba(0,108,53,0.1);
    height: 100%;
}

.panel-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    color: var(--saudi-light);
    letter-spacing: 2px;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border-green);
    padding-bottom: 0.6rem;
    margin-bottom: 1rem;
}

/* ── CONTROL BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #004D27, var(--saudi-green)) !important;
    color: white !important;
    border: 1px solid var(--saudi-light) !important;
    border-radius: 8px !important;
    font-family: 'Tajawal', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    padding: 0.5rem 1rem !important;
    width: 100% !important;
    transition: all 0.3s !important;
    box-shadow: 0 0 10px rgba(0,108,53,0.3) !important;
    letter-spacing: 0.5px !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, var(--saudi-green), var(--saudi-light)) !important;
    box-shadow: 0 0 25px rgba(0,165,80,0.6) !important;
    transform: translateY(-1px) !important;
}

/* Emergency button */
.emergency-btn > button {
    background: linear-gradient(135deg, #8B0000, var(--danger)) !important;
    border-color: #FF6B6B !important;
    box-shadow: 0 0 15px rgba(255,59,48,0.4) !important;
    animation: pulse-danger 2s infinite !important;
}

@keyframes pulse-danger {
    0%, 100% { box-shadow: 0 0 10px rgba(255,59,48,0.3); }
    50% { box-shadow: 0 0 30px rgba(255,59,48,0.7); }
}

/* ── ALERT BOX ── */
.alert-critical {
    background: linear-gradient(135deg, rgba(139,0,0,0.3), rgba(255,59,48,0.1));
    border: 1px solid var(--danger);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    color: #FF8A80;
    font-family: 'Tajawal', sans-serif;
    box-shadow: 0 0 20px rgba(255,59,48,0.2);
}

.alert-warning {
    background: linear-gradient(135deg, rgba(100,60,0,0.3), rgba(255,149,0,0.1));
    border: 1px solid var(--warning);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    color: #FFD180;
}

.alert-ok {
    background: linear-gradient(135deg, rgba(0,60,20,0.3), rgba(0,165,80,0.1));
    border: 1px solid var(--saudi-green);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    color: #A5D6A7;
}

.alert-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    letter-spacing: 1px;
    margin-bottom: 0.4rem;
}

/* ── SLIDER ── */
.stSlider > div > div > div { background: var(--saudi-green) !important; }
.stSlider > div > div > div > div { background: var(--saudi-glow) !important; box-shadow: 0 0 10px rgba(0,255,127,0.5); }

/* ── SELECTBOX ── */
.stSelectbox > div > div {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border-green) !important;
    color: var(--text-primary) !important;
    border-radius: 6px !important;
}

/* ── STATUS INDICATOR ── */
.status-dot {
    display: inline-block;
    width: 10px; height: 10px;
    border-radius: 50%;
    margin-left: 8px;
    animation: blink 1.5s ease-in-out infinite;
}

.dot-green { background: var(--saudi-glow); box-shadow: 0 0 8px var(--saudi-glow); }
.dot-red   { background: var(--danger); box-shadow: 0 0 8px var(--danger); animation-duration: 0.5s; }
.dot-amber { background: var(--warning); box-shadow: 0 0 8px var(--warning); animation-duration: 1s; }

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── GRID VISUALIZATION ── */
.grid-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: 0.5rem;
    background: #020D07;
    border-radius: 8px;
    border: 1px solid #003D1F;
}

/* Streamlit image */
.stImage > img {
    border-radius: 6px;
    border: 1px solid #003D1F;
}

/* Section labels */
.zone-label {
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    color: var(--text-muted);
    letter-spacing: 1px;
    text-align: center;
    margin-top: 0.3rem;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--saudi-green); border-radius: 3px; }

/* Divider */
hr { border-color: var(--border-green) !important; opacity: 0.4; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Session State – initialize simulation
# ──────────────────────────────────────────────
def init_session():
    if "sim" not in st.session_state:
        st.session_state.sim = StadiumSimulation(rows=30, cols=40)
    if "ai" not in st.session_state:
        st.session_state.ai = CrowdAIEngine()
    if "running" not in st.session_state:
        st.session_state.running = False
    if "emergency" not in st.session_state:
        st.session_state.emergency = False
    if "gates_open" not in st.session_state:
        st.session_state.gates_open = True
    if "routing_mode" not in st.session_state:
        st.session_state.routing_mode = "normal"
    if "tick" not in st.session_state:
        st.session_state.tick = 0
    if "alerts" not in st.session_state:
        st.session_state.alerts = []

init_session()
sim: StadiumSimulation = st.session_state.sim
ai: CrowdAIEngine = st.session_state.ai


# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <div>
    <p class="header-title">🏟️ نظام محاكاة إدارة حشود كأس العالم 2034</p>
    <p class="header-subtitle">
        World Cup 2034 KSA · Crowd Intelligence Operations Center · مركز عمليات ذكاء الحشود
    </p>
  </div>
  <div style="text-align:left;">
    <div class="header-badge">LIVE SIM</div>
    <div style="margin-top:6px; font-family:'Orbitron',monospace; font-size:0.65rem; color:#5A8A6A;">
        الرياض الدولي · RIYADH INTL
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# METRICS ROW
# ──────────────────────────────────────────────
metrics = sim.get_metrics()
crowd_count = metrics["crowd_count"]
density_pct = metrics["avg_density"]
evac_eff    = metrics["evac_efficiency"]
hotspot_ct  = metrics["hotspots"]

density_class = "metric-danger" if density_pct > 75 else ("metric-warning" if density_pct > 50 else "")

st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-label">إجمالي الجماهير · Fans</div>
    <div class="metric-value">{crowd_count:,}</div>
    <div class="metric-unit">مشجع داخل الاستاد</div>
  </div>
  <div class="metric-card {density_class}">
    <div class="metric-label">مؤشر الازدحام · Density</div>
    <div class="metric-value">{density_pct:.0f}%</div>
    <div class="metric-unit">متوسط كثافة المناطق</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">كفاءة الإخلاء · Evac</div>
    <div class="metric-value">{evac_eff:.0f}%</div>
    <div class="metric-unit">معدل تدفق بوابات الخروج</div>
  </div>
  <div class="metric-card {'metric-danger' if hotspot_ct > 2 else ''}">
    <div class="metric-label">بؤر الازدحام · Hotspots</div>
    <div class="metric-value">{hotspot_ct}</div>
    <div class="metric-unit">منطقة تحتاج تدخلاً</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# MAIN LAYOUT – 3 Columns
# ──────────────────────────────────────────────
col_controls, col_map, col_alerts = st.columns([1.3, 2.8, 1.5])


# ──────── LEFT: Controls ────────────────────────
with col_controls:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🎛️ لوحة التحكم · Controls</div>', unsafe_allow_html=True)

    # Simulation controls
    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶ تشغيل" if not st.session_state.running else "⏸ إيقاف"):
            st.session_state.running = not st.session_state.running

    with c2:
        if st.button("🔄 إعادة"):
            st.session_state.sim = StadiumSimulation(rows=30, cols=40)
            st.session_state.tick = 0
            st.session_state.alerts = []
            st.session_state.emergency = False
            st.rerun()

    st.markdown("---")

    # Gate control
    st.markdown("**🚪 بوابات الاستاد · Gates**")
    gate_cols = st.columns(2)
    with gate_cols[0]:
        if st.button("✅ فتح الكل"):
            sim.set_gates(open_all=True)
            st.session_state.gates_open = True

    with gate_cols[1]:
        if st.button("🔒 إغلاق جزئي"):
            sim.set_gates(open_all=False)
            st.session_state.gates_open = False

    gate_speed = st.slider("سرعة تدفق الجماهير", 1, 10, 5, key="gate_speed")
    sim.set_flow_speed(gate_speed)

    st.markdown("---")

    # Routing
    st.markdown("**🧭 توجيه الحشود · Routing**")
    routing = st.selectbox("وضع التوجيه", [
        "توجيه طبيعي", "توجيه لمخارج الشمال",
        "توجيه لمخارج الجنوب", "توزيع متوازن"
    ], key="routing_sel")

    routing_map = {
        "توجيه طبيعي": "normal",
        "توجيه لمخارج الشمال": "north",
        "توجيه لمخارج الجنوب": "south",
        "توزيع متوازن": "balanced"
    }
    sim.set_routing(routing_map[routing])

    if st.button("🗺️ تطبيق مسارات جديدة"):
        sim.reroute_agents(routing_map[routing])

    st.markdown("---")

    # Emergency
    st.markdown("**🚨 نظام الطوارئ · Emergency**")
    st.markdown('<div class="emergency-btn">', unsafe_allow_html=True)
    if st.button("🚨 تفعيل بروتوكول الطوارئ"):
        st.session_state.emergency = not st.session_state.emergency
        sim.set_emergency(st.session_state.emergency)
        if st.session_state.emergency:
            st.session_state.alerts.insert(0, {
                "level": "critical",
                "title": "🚨 بروتوكول الطوارئ مُفعَّل",
                "msg": "تم تفعيل مسارات الإخلاء الكاملة. فتح جميع البوابات. إرسال تنبيهات للفِرَق الميدانية."
            })
    st.markdown('</div>', unsafe_allow_html=True)

    emergency_icon = "🔴 مُفعَّل" if st.session_state.emergency else "🟢 جاهز"
    status_dot = "dot-red" if st.session_state.emergency else "dot-green"
    st.markdown(f"""
    <div style="text-align:center; margin-top:0.5rem; font-family:'Orbitron',monospace; font-size:0.75rem; color:#888;">
        حالة الطوارئ: {emergency_icon}
        <span class="status-dot {status_dot}"></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Add fans
    st.markdown("**➕ إضافة جماهير · Add Fans**")
    fan_count = st.slider("عدد المشجعين", 10, 500, 100, step=10)
    zone = st.selectbox("المنطقة", ["مدخل شمالي", "مدخل جنوبي", "مدخل شرقي", "مدخل غربي", "عشوائي"])
    zone_map = {"مدخل شمالي": "north", "مدخل جنوبي": "south", "مدخل شرقي": "east", "مدخل غربي": "west", "عشوائي": "random"}
    if st.button("✚ أضف الجماهير"):
        sim.add_agents(fan_count, zone_map[zone])

    st.markdown('</div>', unsafe_allow_html=True)


# ──────── CENTER: Stadium Grid ──────────────────
with col_map:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🗺️ خريطة الاستاد الحية · Live Stadium Map</div>', unsafe_allow_html=True)

    # Step simulation
    if st.session_state.running:
        sim.step()
        st.session_state.tick += 1

    # Render grid
    grid_image = sim.render_grid_image()
    st.image(grid_image, use_container_width=True, caption="")

    # Zone labels
    st.markdown("""
    <div style="display:flex; justify-content:space-around; margin-top:0.3rem;">
        <span class="zone-label">⬆️ مدخل شمالي</span>
        <span class="zone-label">⚽ الملعب</span>
        <span class="zone-label">⬇️ مدخل جنوبي</span>
    </div>
    """, unsafe_allow_html=True)

    # Legend
    st.markdown("""
    <div style="display:flex; gap:1rem; justify-content:center; margin-top:0.8rem; flex-wrap:wrap;">
        <span style="font-size:0.7rem; color:#5A8A6A; font-family:'Orbitron',monospace;">
            <span style="color:#00FF7F;">█</span> مشجع عادي &nbsp;
            <span style="color:#FF9500;">█</span> كثافة متوسطة &nbsp;
            <span style="color:#FF3B30;">█</span> ازدحام حرج &nbsp;
            <span style="color:#006C35;">█</span> مجال الملعب &nbsp;
            <span style="color:#FFFFFF;">▪</span> بوابة
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Density chart
    st.markdown('<div class="panel" style="margin-top:1rem;">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📊 توزيع الكثافة حسب المنطقة · Zone Density</div>', unsafe_allow_html=True)

    density_data = sim.get_zone_densities()
    import plotly.graph_objects as go

    zone_names = ["شمال", "جنوب", "شرق", "غرب", "وسط"]
    zone_vals  = [density_data.get(z, 0) for z in ["north", "south", "east", "west", "center"]]
    bar_colors = ["#FF3B30" if v > 75 else ("#FF9500" if v > 50 else "#006C35") for v in zone_vals]

    fig = go.Figure(go.Bar(
        x=zone_names, y=zone_vals,
        marker_color=bar_colors,
        text=[f"{v:.0f}%" for v in zone_vals],
        textposition="outside",
        textfont=dict(color="#A5D6A7", size=11, family="Orbitron"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#5A8A6A", family="Tajawal"),
        yaxis=dict(range=[0, 110], gridcolor="#0A2018", tickformat=".0f", ticksuffix="%"),
        xaxis=dict(gridcolor="#0A2018"),
        margin=dict(t=10, b=10, l=10, r=10),
        height=160,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('</div>', unsafe_allow_html=True)


# ──────── RIGHT: Alerts & AI ─────────────────────
with col_alerts:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🤖 تنبيهات الذكاء الاصطناعي · AI Alerts</div>', unsafe_allow_html=True)

    # AI Analysis
    ai_alerts = ai.analyze(sim)
    all_alerts = ai_alerts + st.session_state.alerts[:3]  # AI + manual

    if not all_alerts:
        st.markdown("""
        <div class="alert-ok">
            <div class="alert-title">✅ الأوضاع مستقرة</div>
            <div style="font-size:0.85rem; margin-top:4px;">
                جميع المناطق ضمن الحدود الآمنة. لا توجد بؤر ازدحام.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for alert in all_alerts[:5]:
            level_class = {
                "critical": "alert-critical",
                "warning":  "alert-warning",
                "ok":       "alert-ok"
            }.get(alert["level"], "alert-ok")
            st.markdown(f"""
            <div class="{level_class}">
                <div class="alert-title">{alert['title']}</div>
                <div style="font-size:0.82rem; margin-top:5px; line-height:1.5;">{alert['msg']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # System status
    st.markdown('<div class="panel-title">📡 حالة الأنظمة · System Status</div>', unsafe_allow_html=True)

    systems = [
        ("كاميرات الذكاء الاصطناعي", "dot-green", "فعّال"),
        ("أجهزة الاستشعار", "dot-green", "فعّال"),
        ("نظام الاتصالات", "dot-green", "فعّال"),
        ("بروتوكول الطوارئ", "dot-red" if st.session_state.emergency else "dot-green",
         "مُفعَّل" if st.session_state.emergency else "جاهز"),
        ("إدارة البوابات", "dot-green" if st.session_state.gates_open else "dot-amber",
         "مفتوحة" if st.session_state.gates_open else "جزئي"),
    ]

    for name, dot, status in systems:
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    padding:6px 0; border-bottom:1px solid #0A2018; font-size:0.8rem;">
            <span style="color:#8ABFA0;">{name}</span>
            <span style="font-family:'Orbitron',monospace; font-size:0.7rem; color:#5A8A6A;">
                {status}<span class="status-dot {dot}"></span>
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Sim stats
    st.markdown(f"""
    <div style="font-family:'Orbitron',monospace; font-size:0.65rem; color:#3A6A4A; text-align:center;">
        TICK #{st.session_state.tick:05d} &nbsp;|&nbsp;
        {'▶ RUNNING' if st.session_state.running else '⏸ PAUSED'}<br>
        RIYADH INT'L STADIUM · WC2034<br>
        <span style="color:#006C35;">▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Auto-refresh when running
# ──────────────────────────────────────────────
if st.session_state.running:
    time.sleep(0.4)
    st.rerun()
