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
st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:center; gap:32px; flex-wrap:wrap; padding:16px 0;">
    <img src="data:image/png;base64,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" style="height:52px; width:auto;" alt="3rd I ProcessFX"/>
    <div style="text-align:center; font-size:12px; color:#5A7A8A;">
      GLOBAL FOOD CHAIN WAR ROOM &nbsp;·&nbsp; ISM World 2026<br>
      Gwen Mitchell &amp; John Atasie &nbsp;·&nbsp; Powered by Claude AI (Anthropic)
    </div>
    <img src="data:image/jpeg;base64,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" style="height:52px; width:auto;" alt="J5 Global Synergy Group"/>
</div>
""", unsafe_allow_html=True)
