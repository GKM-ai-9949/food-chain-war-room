import streamlit as st
from anthropic import Anthropic
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Food Chain War Room | ISM World 2026",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Crisis Scenarios ────────────────────────────────────────────────────────────
SCENARIOS = {
    "ukraine_wheat": {
        "key": "ukraine_wheat",
        "headline": "Ukraine Port Blockade — Wheat Shipments Halted",
        "region": "Ukraine / Black Sea",
        "commodity": "Wheat",
        "icon": "🌾",
        "label": "Ukraine Wheat Crisis",
        "context": (
            "Military escalation has blocked all Black Sea shipping lanes. "
            "Ukraine and Russia together supply approximately 30% of global wheat exports. "
            "Port operations in Odessa and Mykolaiv suspended indefinitely. "
            "Global wheat futures surged 28% at market open."
        ),
        "supply_pct": 30,
        "categories": ["Bread", "Pasta", "Flour", "Animal Feed", "Breakfast Cereals"],
    },
    "brazil_coffee": {
        "key": "brazil_coffee",
        "headline": "Brazil Drought — Coffee Crop Fails, Arabica Futures +65%",
        "region": "Brazil (Minas Gerais / São Paulo)",
        "commodity": "Coffee",
        "icon": "☕",
        "label": "Brazil Coffee Drought",
        "context": (
            "Catastrophic drought across Brazil's coffee belt has caused a 40% crop failure. "
            "Brazil supplies approximately 40% of the world's coffee — the largest single origin. "
            "Arabica futures surged 65% overnight. Colombian and Vietnamese supply "
            "cannot compensate at scale. Roasters and distributors face immediate shortfall."
        ),
        "supply_pct": 40,
        "categories": ["Roasted Coffee", "Instant Coffee", "Coffee Pods", "Café Chains", "Food Service"],
    },
    "westafrica_cocoa": {
        "key": "westafrica_cocoa",
        "headline": "West Africa Coup — Cocoa Exports Suspended, Ports Closed",
        "region": "Côte d'Ivoire / Ghana",
        "commodity": "Cocoa",
        "icon": "🍫",
        "label": "West Africa Cocoa Crisis",
        "context": (
            "A military coup in Côte d'Ivoire, combined with political unrest in Ghana, "
            "has suspended all cocoa exports. These two nations supply approximately 65% of "
            "global cocoa. Export licenses revoked, ports closed to commercial shipping. "
            "Chocolate manufacturers and confectionery brands face critical shortfall."
        ),
        "supply_pct": 65,
        "categories": ["Chocolate", "Confectionery", "Baking Products", "Beverages", "Cosmetics"],
    },
}

# ─── Session State ───────────────────────────────────────────────────────────────
for key, default in {
    "selected_scenario": None,
    "briefing": None,
    "run_count": 0,
    "company_name": "MidWest Foods Corp",
    "revenue": 450,
    "exposure_pct": 35,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

MAX_FREE_RUNS = 4

# ─── API Client ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    api_key = None
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY not configured.")
        st.stop()
    return Anthropic(api_key=api_key)

# ─── CSS ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Light conference theme — ISM White + Blue */
    .stApp { background-color: #FFFFFF; color: #1A2B3C; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Breaking news ticker — keep red for urgency */
    .ticker-wrap {
        background: #E63946;
        padding: 10px 0;
        margin-bottom: 24px;
        border-bottom: 3px solid #C1121F;
    }
    .ticker-label {
        color: white;
        font-weight: 900;
        font-size: 13px;
        letter-spacing: 2px;
        text-align: center;
    }

    /* Header */
    .war-room-title {
        font-size: 40px;
        font-weight: 900;
        color: #1A2B3C;
        text-align: center;
        margin: 0;
        letter-spacing: -1px;
    }
    .war-room-subtitle {
        font-size: 13px;
        color: #39A2CE;
        letter-spacing: 3px;
        text-transform: uppercase;
        text-align: center;
        margin-top: 6px;
        margin-bottom: 20px;
    }

    /* Divider */
    .war-divider {
        border: none;
        border-top: 1px solid #C8E4F0;
        margin: 18px 0;
    }

    /* Section labels */
    .section-label {
        color: #39A2CE;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    /* Breaking headline */
    .breaking-headline {
        background: #FFF0F1;
        border-left: 4px solid #E63946;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        margin: 12px 0;
    }
    .breaking-label {
        color: #E63946;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    .breaking-text {
        color: #1A2B3C;
        font-size: 18px;
        font-weight: 700;
        margin-top: 4px;
        line-height: 1.3;
    }

    /* Metric boxes */
    .metric-box {
        background: #EBF7FC;
        border: 1px solid #C8E4F0;
        border-radius: 8px;
        padding: 14px 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 900;
        color: #39A2CE;
    }
    .metric-label {
        font-size: 10px;
        color: #5A8AA0;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 4px;
    }

    /* Context card */
    .context-card {
        background: #F4FAFE;
        border: 1px solid #C8E4F0;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 10px 0;
        color: #2C4A5C;
        font-size: 14px;
        line-height: 1.7;
    }

    /* Briefing output */
    .briefing-container {
        background: #F4FAFE;
        border: 2px solid #39A2CE;
        border-radius: 12px;
        padding: 26px;
        margin-top: 16px;
    }
    .briefing-header {
        color: #39A2CE;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 16px;
        border-bottom: 1px solid #C8E4F0;
        padding-bottom: 10px;
    }
    .briefing-content {
        color: #1A2B3C;
        font-size: 15px;
        line-height: 1.85;
        white-space: pre-wrap;
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #8899BB;
    }

    /* Run button — ISM Blue */
    .stButton > button {
        background: #39A2CE !important;
        color: white !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px 24px !important;
        width: 100% !important;
        margin-top: 6px !important;
        transition: background 0.2s !important;
    }
    .stButton > button:hover {
        background: #2A7FA8 !important;
    }

    /* Input overrides for light theme */
    .stTextInput > div > div > input {
        background: #F4FAFE !important;
        color: #1A2B3C !important;
        border-color: #C8E4F0 !important;
    }
    .stNumberInput > div > div > input {
        background: #F4FAFE !important;
        color: #1A2B3C !important;
        border-color: #C8E4F0 !important;
    }
    label {
        color: #39A2CE !important;
        font-size: 11px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }

    /* Footer */
    .war-footer {
        text-align: center;
        padding: 18px 0;
        color: #8AABBB;
        font-size: 12px;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Breaking News Ticker ────────────────────────────────────────────────────────
st.markdown("""
<div class="ticker-wrap">
    <div class="ticker-label">
        ⚡&nbsp; LIVE INTELLIGENCE SYSTEM &nbsp;|&nbsp;
        GLOBAL FOOD SUPPLY CHAIN WAR ROOM &nbsp;|&nbsp;
        POWERED BY CLAUDE AI &nbsp;|&nbsp;
        ISM WORLD 2026 &nbsp;|&nbsp; ⚡
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="war-room-title">🌍 Global Food Chain War Room</div>
<div class="war-room-subtitle">Geopolitical Disruption Intelligence &nbsp;·&nbsp; Powered by Claude AI</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="war-divider">', unsafe_allow_html=True)

# ─── Two-Column Layout ───────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1.6])

# ════════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN — Controls
# ════════════════════════════════════════════════════════════════════════════════
with left_col:

    # Scenario buttons
    st.markdown('<div class="section-label">⚡ Select Crisis Scenario</div>', unsafe_allow_html=True)

    for key, scenario in SCENARIOS.items():
        is_selected = st.session_state.selected_scenario == key
        prefix = "✅ " if is_selected else ""
        label = f"{prefix}{scenario['icon']}  {scenario['label']}"
        if st.button(label, key=f"btn_{key}", use_container_width=True):
            st.session_state.selected_scenario = key
            st.session_state.briefing = None
            st.rerun()

    st.markdown('<hr class="war-divider">', unsafe_allow_html=True)

    # Company Profile
    st.markdown('<div class="section-label">🏢 Your Company Profile</div>', unsafe_allow_html=True)

    company_name = st.text_input(
        "Company Name",
        value=st.session_state.company_name,
        key="company_input"
    )
    st.session_state.company_name = company_name

    revenue = st.number_input(
        "Annual Revenue ($M)",
        min_value=10,
        max_value=50000,
        value=st.session_state.revenue,
        step=10,
        key="revenue_input"
    )
    st.session_state.revenue = revenue

    exposure_pct = st.slider(
        "COGS Exposure to Affected Region (%)",
        min_value=0,
        max_value=100,
        value=st.session_state.exposure_pct,
        step=5,
        key="exposure_input"
    )
    st.session_state.exposure_pct = exposure_pct

    st.markdown('<hr class="war-divider">', unsafe_allow_html=True)

    # Run Button
    runs_remaining = MAX_FREE_RUNS - st.session_state.run_count
    run_disabled = st.session_state.selected_scenario is None or runs_remaining <= 0

    if runs_remaining > 0:
        if st.button(
            "🚨 ACTIVATE WAR ROOM ANALYSIS",
            disabled=run_disabled,
            key="run_btn"
        ):
            scenario = SCENARIOS[st.session_state.selected_scenario]
            client = get_client()
            exposure_m = revenue * exposure_pct / 100

            system_prompt = """You are a senior supply chain intelligence analyst briefing the C-suite \
during a global food supply disruption. Your briefings are urgent, quantified, and action-oriented. \
No corporate fluff — every sentence drives a decision.

Format your response EXACTLY with these headers and icons:

🚨 SITUATION ASSESSMENT
[2-3 sentences: what happened, scale of disruption, immediate market signal.]

📊 IMPACT ON [COMPANY NAME]
Risk Level: [CRITICAL / HIGH / ELEVATED / MODERATE]
Annual Exposure: $[X]M
Estimated Weeks to Stockout: [X] weeks
[1-2 sentences on specific business consequence.]

⚡ IMMEDIATE ACTIONS — NEXT 72 HOURS
1. [Specific action — who owns it]
2. [Specific action — who owns it]
3. [Specific action — who owns it]

🗺️ STRATEGIC OPTIONS
Option 1: [Name] — [2-sentence description] | Cost Premium: [X]% | Timeline: [X] weeks
Option 2: [Name] — [2-sentence description] | Cost Premium: [X]% | Timeline: [X] weeks
Option 3: [Name] — [2-sentence description] | Cost Premium: [X]% | Timeline: [X] weeks

🔭 WATCH NEXT 7 DAYS
[2-3 sentences: intelligence signals to monitor — price indices, political developments, logistics data.]"""

            user_message = f"""CRISIS ALERT — {scenario['commodity'].upper()} DISRUPTION

SCENARIO: {scenario['headline']}
REGION: {scenario['region']}
GLOBAL SUPPLY AT RISK: ~{scenario['supply_pct']}%
CONTEXT: {scenario['context']}

COMPANY PROFILE:
- Company: {st.session_state.company_name}
- Annual Revenue: ${revenue}M
- COGS Exposure to Affected Region: {exposure_pct}% (~${exposure_m:.0f}M annual exposure)
- Affected Categories: {', '.join(scenario['categories'])}

Generate the war room briefing now."""

            try:
                with st.spinner("🛰️ Intelligence system processing..."):
                    response = client.messages.create(
                        model="claude-opus-4-6",
                        max_tokens=1200,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_message}]
                    )
                st.session_state.briefing = response.content[0].text
                st.session_state.run_count += 1
                st.rerun()
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

        if run_disabled and st.session_state.selected_scenario is None:
            st.caption("⬆️ Select a crisis scenario to activate")
        else:
            st.caption(f"🔋 {runs_remaining} analysis runs remaining this session")
    else:
        st.warning("⚠️ Session limit reached. Reload to reset.")

# ════════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN — Output
# ════════════════════════════════════════════════════════════════════════════════
with right_col:

    selected = st.session_state.selected_scenario

    if selected:
        scenario = SCENARIOS[selected]

        # Breaking headline
        now_utc = datetime.utcnow().strftime("%H:%M UTC")
        st.markdown(f"""
        <div class="breaking-headline">
            <div class="breaking-label">🔴 BREAKING &nbsp;|&nbsp; {now_utc}</div>
            <div class="breaking-text">{scenario['headline']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Quick metrics
        exposure_m = st.session_state.revenue * st.session_state.exposure_pct / 100
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{scenario['supply_pct']}%</div>
                <div class="metric-label">Global Supply at Risk</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">${exposure_m:.0f}M</div>
                <div class="metric-label">Your Exposure</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{scenario['icon']}</div>
                <div class="metric-label">{scenario['commodity']}</div>
            </div>""", unsafe_allow_html=True)

        # Context
        st.markdown(f"""
        <div class="context-card">{scenario['context']}</div>
        """, unsafe_allow_html=True)

        # Affected categories
        cats = " &nbsp;·&nbsp; ".join(
            [f"<span style='color:#F4A261; font-weight:600'>{c}</span>"
             for c in scenario['categories']]
        )
        st.markdown(f"""
        <div style="font-size:12px; color:#8899BB; letter-spacing:1px; margin:6px 0 10px 0;">
        AFFECTED CATEGORIES: {cats}
        </div>
        """, unsafe_allow_html=True)

        # Briefing
        if st.session_state.briefing:
            st.markdown(f"""
            <div class="briefing-container">
                <div class="briefing-header">🛰️ WAR ROOM INTELLIGENCE BRIEFING — CLAUDE AI</div>
                <div class="briefing-content">{st.session_state.briefing}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:40px; color:#4A5568; border:1px dashed #2D3A5C; border-radius:12px; margin-top:16px;">
                <div style="font-size:32px; margin-bottom:12px;">🛰️</div>
                <div style="font-size:15px; color:#8899BB; font-weight:600;">Intelligence system standing by</div>
                <div style="font-size:13px; margin-top:6px;">Click ACTIVATE WAR ROOM ANALYSIS to generate briefing</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        # Empty state
        st.markdown("""
        <div class="empty-state">
            <div style="font-size:52px; margin-bottom:16px;">🌍</div>
            <div style="font-size:16px; font-weight:700; color:#8899BB;">Select a crisis scenario</div>
            <div style="font-size:14px; margin-top:8px;">
                Choose a geopolitical disruption event on the left<br>to begin intelligence analysis
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────────────
st.markdown('<hr class="war-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="war-footer">
    GLOBAL FOOD CHAIN WAR ROOM &nbsp;|&nbsp; ISM World 2026 &nbsp;|&nbsp;
    Gwen Mitchell · 3rd I ProcessFX &nbsp;|&nbsp; Powered by Claude AI (Anthropic)
</div>
""", unsafe_allow_html=True)
