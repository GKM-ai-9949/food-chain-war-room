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
    <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAACUCAYAAADWFGYSAAAMTWlDQ1BJQ0MgUHJvZmlsZQAAeJyVVwdYU8kWnltSIQQIREBK6E0QkRJASggtgPQuKiEJEEqMCUHFji4quHYRwYqugii6utIWG+qqK4tidy2LBRVlXSzYlTchgC77yvfm++bOf/8588855869dwYAeidfKs1FNQHIk+TLYoL9WUnJKSzSU4ABEqABD2DKF8ilnKiocADLUPv38uYaQJTtZQel1j/7/2vREorkAgCQKIjThXJBHsQ/AYC3CKSyfACIUsibz8iXKvE6iHVk0EGIq5U4U4VblDhdhS8O2MTFcCF+CABZnc+XZQKg0Qt5VoEgE+rQYbTASSIUSyD2g9gnL2+aEOIFENtAGzgnXanPTv9GJ/NvmunDmnx+5jBWxTJQyAFiuTSXP+v/TMf/Lnm5iqE5rGFVz5KFxChjhnl7mDMtTInVIX4nSY+IhFgbABQXCwfslZiZpQiJV9mjNgI5F+YMMCGeIM+N5Q3yMUJ+QBjEhhBnSHIjwgdtijLEQUobmD+0XJzPi4NYD+JqkTwwdtDmuGxazNC81zJkXM4g/4QvG/BBqf9FkRPPUelj2lki3qA+5liYFZcIMRXigAJxQgTEGhBHyHNiwwZtUguzuBFDNjJFjDIWC4hlIkmwv0ofK8uQBcUM2u/Jkw/Fjh3PEvMiBvGl/Ky4EFWusIcC/oD/MBasVyThxA/piORJ4UOxCEUBgarYcbJIEh+r4nE9ab5/jGosbifNjRq0x/1FucFK3gziOHlB7NDYgny4OFX6eLE0PypO5Sdekc0PjVL5gx8A4YALAgALKGBNB9NANhC39zT0wDtVTxDgAxnIBCLgMMgMjUgc6JHAaywoBH9CJALy4XH+A70iUAD5zyNYJSce5lRXB5Ax2KdUyQGPIM4DYSAX3isGlCTDHiSAh5AR/8MjPqwCGEMurMr+f88PsV8ZDmTCBxnF0Iws+pAlMZAYQAwhBhFtcQPcB/fCw+HVD1ZnnI17DMXx1Z7wiNBBuE+4Sugk3JwqLpKN8HIi6IT6QYP5Sf82P7gV1HTF/XFvqA6VcSZuABxwFzgPB/eFM7tCljvotzIrrBHaf4vgmyc0aEdxoqCUURQ/is3IkRp2Gq7DKspcf5sfla/pw/nmDveMnJ/7TfaFsA0baYktxQ5hZ7AT2DmsBWsALOwY1oi1YUeUeHjFPRxYcUOzxQz4kwN1Rq6Zr09WmUm5U61Tt9MnVV++aGa+8mXkTpPOkokzs/JZHPjHELF4EoHjGJazk7MbAMr/j+rz9ip64L+CMNu+cov+AMD7WH9//89fudBjAPzoDj8JTV85Gzb8tagBcLZJoJAVqDhceSHALwcdvn36wBiYAxsYjzNwA17ADwSCUBAJ4kAymAK9z4LrXAZmgDlgISgGpWAVWA8qwFawA1SDfeAgaAAt4AT4BZwHF8FVcAuuni7wDPSCN+AjgiAkhIYwEH3EBLFE7BFnhI34IIFIOBKDJCNpSCYiQRTIHGQRUoqsQSqQ7UgN8iPShJxAziEdyE3kHtKNvEQ+oBiqjuqgRqgVOhZloxw0DI1DJ6OZ6HS0EF2MrkDL0Sp0L1qPnkDPo1fRTvQZ2ocBTA1jYqaYA8bGuFgkloJlYDJsHlaClWFVWB3WDJ/zZawT68He40ScgbNwB7iCQ/B4XIBPx+fhy/EKvBqvx0/hl/F7eC/+hUAjGBLsCZ4EHiGJkEmYQSgmlBF2EQ4TTsN3qYvwhkgkMonWRHf4LiYTs4mzicuJm4n7iceJHcQHxD4SiaRPsid5kyJJfFI+qZi0kbSXdIx0idRFekdWI5uQnclB5BSyhFxELiPvIR8lXyI/Jn+kaFIsKZ6USIqQMouykrKT0ky5QOmifKRqUa2p3tQ4ajZ1IbWcWkc9Tb1NfaWmpmam5qEWrSZWW6BWrnZA7azaPbX36trqdupc9VR1hfoK9d3qx9Vvqr+i0WhWND9aCi2ftoJWQztJu0t7p8HQcNTgaQg15mtUatRrXNJ4TqfQLekc+hR6Ib2Mfoh+gd6jSdG00uRq8jXnaVZqNmle1+zTYmiN04rUytNarrVH65zWE22StpV2oLZQe7H2Du2T2g8YGMOcwWUIGIsYOxmnGV06RB1rHZ5Otk6pzj6ddp1eXW1dF90E3Zm6lbpHdDuZGNOKyWPmMlcyDzKvMT+MMhrFGSUatWxU3ahLo97qjdbz0xPplejt17uq90GfpR+on6O/Wr9B/44BbmBnEG0ww2CLwWmDntE6o71GC0aXjD44+ndD1NDOMMZwtuEOwzbDPiNjo2AjqdFGo5NGPcZMYz/jbON1xkeNu00YJj4mYpN1JsdMnrJ0WRxWLqucdYrVa2poGmKqMN1u2m760czaLN6syGy/2R1zqjnbPMN8nXmrea+FicVEizkWtRa/W1Is2ZZZlhssz1i+tbK2SrRaYtVg9cRaz5pnXWhda33bhmbjazPdpsrmii3Rlm2bY7vZ9qIdaudql2VXaXfBHrV3sxfbb7bvGEMY4zFGMqZqzHUHdQeOQ4FDrcM9R6ZjuGORY4Pj87EWY1PGrh57ZuwXJ1enXKedTrfGaY8LHVc0rnncS2c7Z4FzpfOV8bTxQePnj28c/8LF3kXkssXlhivDdaLrEtdW189u7m4ytzq3bncL9zT3Te7X2TrsKPZy9lkPgoe/x3yPFo/3nm6e+Z4HPf/ycvDK8drj9WSC9QTRhJ0THnibefO9t3t3+rB80ny2+XT6mvryfat87/uZ+wn9dvk95thysjl7Oc/9nfxl/of933I9uXO5xwOwgOCAkoD2QO3A+MCKwLtBZkGZQbVBvcGuwbODj4cQQsJCVodc5xnxBLwaXm+oe+jc0FNh6mGxYRVh98PtwmXhzRPRiaET1068HWEZIYloiASRvMi1kXeirKOmR/0cTYyOiq6MfhQzLmZOzJlYRuzU2D2xb+L841bG3Yq3iVfEtybQE1ITahLeJgYkrknsTBqbNDfpfLJBsji5MYWUkpCyK6VvUuCk9ZO6Ul1Ti1OvTbaePHPyuSkGU3KnHJlKn8qfeiiNkJaYtiftEz+SX8XvS+elb0rvFXAFGwTPhH7CdcJukbdojehxhnfGmownmd6ZazO7s3yzyrJ6xFxxhfhFdkj21uy3OZE5u3P6cxNz9+eR89LymiTakhzJqWnG02ZO65DaS4ulndM9p6+f3isLk+2SI/LJ8sZ8HbjRb1PYKL5T3CvwKagseDcjYcahmVozJTPbZtnNWjbrcWFQ4Q+z8dmC2a1zTOcsnHNvLmfu9nnIvPR5rfPN5y+e37UgeEH1QurCnIW/FTkVrSl6vShxUfNio8ULFj/4Lvi72mKNYlnx9SVeS7YuxZeKl7YvG79s47IvJcKSX0udSstKPy0XLP/1+3Hfl3/fvyJjRftKt5VbVhFXSVZdW+27unqN1prCNQ/WTlxbv461rmTd6/VT158rcynbuoG6QbGhszy8vHGjxcZVGz9VZFVcrfSv3L/JcNOyTW83Czdf2uK3pW6r0dbSrR+2ibfd2B68vb7KqqpsB3FHwY5HOxN2nvmB/UPNLoNdpbs+75bs7qyOqT5V415Ts8dwz8patFZR2703de/FfQH7Gusc6rbvZ+4vPQAOKA48/THtx2sHww62HmIfqvvJ8qdNhxmHS+qR+ln1vQ1ZDZ2NyY0dTaFNrc1ezYd/dvx5d4tpS+UR3SMrj1KPLj7af6zwWN9x6fGeE5knHrRObb11MunklVPRp9pPh50++0vQLyfPcM4cO+t9tuWc57mmX9m/Npx3O1/f5tp2+DfX3w63u7XXX3C/0HjR42Jzx4SOo5d8L524HHD5lyu8K+evRlztuBZ/7cb11OudN4Q3ntzMvfni94LfP95acJtwu+SO5p2yu4Z3q/6w/WN/p1vnkXsB99rux96/9UDw4NlD+cNPXYsf0R6VPTZ5XPPE+UlLd1D3xaeTnnY9kz772FP8p9afm57bPP/pL7+/2nqTerteyF70v1z+Sv/V7tcur1v7ovruvsl78/FtyTv9d9Xv2e/PfEj88PjjjE+kT+WfbT83fwn7crs/r79fypfxB7YCGFAebTIAeLkbAFoyAAx4bqROUp0PBwqiOtMOIPCfsOoMOVDgzqUO7umje+Du5joAB3YCYAX16akARNEAiPMA6Pjxw3XoLDdw7lQWIjwbbJv8OT0vHfybojqTfuP3yBYoVV3AyPZfu+qDNHkyIuIAAJEfSURBVHja7L13mKXJXd/7qao3ntg5TU/OuzObs6TdVQIFUEIGARdsbNCDDQan6wvYFwdsC4RxwHBtQCAySGAULKGcpZVWYnOa2dnJ0zMdptPJb6iq+0e953TPJu2uVhLY8z7PPDPTfc57zumuX9UvfIPIs54FsNai8wyLBYu7BBv/vnxdvv4aXEIIRH9dim/gRsXzrXVrf/O9BAKpPKRUeP0v5nmGwCDFxiOt+Mbew+Xr8vXiXRYhJHmuMca8aHeVUuJ5CmvNpohzh4XwhQsQaw1Yg5DShVRxeojLp8fl669DaFiL73tcvLjGiRNz1GoVtNGIb2D7toCSkvVGm927tzA2WifLtTudEAhrMEZvnCDfzA8nxOVz6IX//KD/4+v/WwxSg43v/e/0OZ8ptUqSlJmZcbbtnCFP0kvWlRBisNZssclv3POptYK1Fi8MOH3iPEmvuJct8q5N78N7SlwVN7TWuttai7UWKeWmN7PxoZ5L5GttBm/68vXsi8BaizEWz5No7f42xv0OlCcx2qC1RSmJUoI8N885SIQQWGMREoyxKKU2LSb7LaofBNYahJCXLFohBFmmBzXG022sQgiMMZgsJ8/1YE1KKcmyDKUUeZ6jlERKiVL9lEw/7dqUMi9eRz6plrDPFCAuiiwuOLAWz/NQgU/a6RXftmhdvPlBsPWjl0t+2MrzWFhcoVYtEwT+C/ol9AN7887Q/2E9l1/s5l23/25d0Lv/CfnUneeF7epulxpkqAKMASnd1435ejsk5Npw+tQipVKAEIKtW8d4+OEzjI3VOHfuIiMjVZSSrK93qNdLdLsJu3ZNPbcUJfA4dXKBNM2J45AkyQBoNDpceWg7npLf1CCx1vLgg6colyPa7YTR0QrGWKIoIEkycq2RQqC1oZdk7Ng+QakcYo192kCT0i3+L37xASYnR+h0esxsGef8+SUmxodptbo0Gm22bZtky5YJtNZPCbhL6m27aeffdOLIp/zm+9+2FuX7nDkzzwff9xmsAOUpPv7xuzlxYo7fetf7iUoxvu+hlCCKQ4LAJwwDonKJqByjteaB+4+hlHoBxZPbbbQ2KCXJsvySXSXLcrJMf93g8n2FlBKtDVmmSVN3H8+TKE+SJFmxe+WXnI7Ptgu6ewqkdP/uvx+z6ZfZ3/3zXJPnBs+TRbA8833zLCdJMoLA4+LFBsvLTebn11hYWKPTSWg2uwgB9XqJMPTIMk0QeM9pYbsUJSeKAnq9FAusrbVpt5NvycmR5wZjLOVyRKPRGbzumTNLtNs9zs+t4HmKOA5pNbtFyvPMWYpbG5qVlXWWllZpt7u0W1163ZSjR0/T6yUsLq5w8uR5vMDjece+eNoT5NJL+Yp2u8tX7n6YN7z5lXRbLaIopFotsbLS4O67HmDLlgnq9QqP3HOEqclROp0ec0UU1+sV6vUynW6ParXsjnfx9XeaIPR54P6TjI3VmJtbZmiojJSCXBviKCAIPJaWGtTrJbZtGy+O5qfe4/jxeRrrncEpNDMzwvz8KrVaiTTNB7u7RZAmGVEcsH37xNPmq0opWq0ux4/P43mKLNdIAUopsiynViuR55pekhFHAUIKwsAjSXM8JWk0uvi+YufOSaLIvySYwKU8URywdesY1lp27pxEa8PLXnaQNM3xlCLXGs9Tgw1kaKhMluVft8brB9/27ePEcUCz2SVJcnZsH0drgxRPfxJLKQZt0H56ZIwZpEGbP8OzncDu5ye56qodeJ5kbKw6SCPHx+t4nmTvnmmyXBMEPqVSgOfJS+qtJ1/GGMIw4I47rqNUiuh2E2q1MrVamSgKKJUiDh/e4zbSJHvWzekpgWE3esje18slgsCjXq8ChrhS5qtfe4Tx8SFqtTK+7/Pnf/4p6vUKQ8NVlpYadDsdllfWKZcjPvOZe9i1ewvpg09w+503keTtIvd89rZbr5uy3uggpctL2+2EcjkC63Y931eMjFSIouBZ37vvKdbW2gwPl+n10sHzjLG02z08T1EqhW5HNZYszZ9xyxKCQSCuNzqU4hBtDJ1OShT5xWlm0bkepEG6FLrPYDTKkywurbNt2/gzDpissZRK4eDE9DxFnmvC0CfPNaVSSJrmaG3wfX9wUj2XGsRaCAKPtfUOtUpMEGiUUqSpy9kHRW6xSNzPKCUIPHzfPS7LNHEckOeaLHOpWn+xZlmO7z/zcpJKIHAB54JDuVO8qIPy3N27202p1UpYa0nTHN9XaG2f8TNNz4xhtBm89sTEMFJKOp0eURQQhj5amxfQ5XI/C+/r5ShpltNqtsmzjLNnit2zSG9q9TIWmF9YYf/+7dx82/X88R98gB07Zrju2oO85z2f5Eff/ias1uRp75JC/9n73XDLzfuw1tLtZpRKIe1OjzDwipmNIYp8rIU8109ZIP2Cb3JyiC1bRjHG0OkkeJ5ygQZs2TKCtS4Hny2P0u26hf50O2E/1avVYg4cmCUM/UGweJ6i18tI04w4DgBBmuZMTQ0Txz7tdoIQglIpLN6reMY+vrXw0EOnqdViOp2E0dEaF5cbVMoR3W5KuRwWi8Zjda0FFvbunaFWi5+1WO83S86du0i7nTDPKktL60xODtPtJkxMDrG4sEalErG83KRcjopaocfwcIVzc8tMTQ6xutqiVivR7aYEoUdjvYO1llqtxHqjw+FD2592p7bWEgQuKyiVwiKgNH7guTpQCJrNLrVayZ1oUrC01KBadWn6xESdLdsmLtm7pJR0uz2++tWH8XyfZqPFjp0zPPzQcaamR8nSnFtvPfyCgmPz9awBonNDGARcffVeHj9ymrX1JldesYtKJea2Ww9xcWmNN7/pTsDymc/cw86dM+zYOeN26zDkNd95C5/+1Fe54/brnnMRbC0oJbHWHfG1WozWhnqtNDjSw9DtQl9v51RqYzFWKvGgI7e5Azc87E6Uer006BY9e/3hFXWR2w21NgSBV6RNBmuhVAoGaVOlEhdFui0GUvZZj3ffV3Q6KQiBHyjyorOTZTla+wjpgrVaibl4sfGcUqynu8IocHWeFJyfWwEs7XZCqRSyvt4ZnFpgSdMMrQ0Tk0P0uqn7PNpQLoesrLbcIrTucS4AnrrBpElOmro6z/MkcRzQ62UoJSmV3MnR6SbEUYDF/RzK5XBQt/AMm4oQG9MQKQSlcoSSioz8xamf8qxnrTXkWXpJVd/vdilPogKfrEhRkBKTa6RS6Dwf5KZCSrI0Gxx1SZISliJMlrvWnLHflP74N3qf/te/0dd5sd5nmubFKa0HQSilC/Qg8MmynDw3g534+cyZhBC0Wj0qldAVwAJ63RSlVJGKbHR6jLEkSYbnSaIocCdm0fXT2pCmOeVyODjF+xvFs9WW/Qyi00kIQw+l1KCmSdOcIPDo9dxrBsHG++mfQHNzi+S5Ztu2KdI0AwRK9e/pMhT3XnOSJCWOw2f82VhrCQOfU6fn8X2PmS3jxWbj1r3BIqX3dQLkSXOQQXv0aRZU/xfZ3yEvLeguDwqfT/duo+389EPXJxfIzxdasTnF21yIP7nm6r8HYyyXgCye9B6ea8v9yZ/x0pRJFK/z1PezOUCEEGzZNo3JssFjAYRyb9A1ggRI12d/prdkrUX6PudOXwB4xgDxnutw5xKg2NO0Qze+Li75ZVy+nt/VX3TP1hH6RsYVT65/ninQNi/SJ3eSnvwenu/85Oles/+1rxf48/PLgCDL828Yqxh4HvPzy0xPj77AFOvydfn6a4Qy0Fpz8eL6Bvr2G5lrFs8XQjA2VnfdtH7oPF2KlaUJ8nJ8XL7+eofJYDD7Yl79Fv0gv7JgAKX8J6VYl0+Qy9df8yvN8m/K6bQBxiogVEXa6D1drXH5unz9dU61vqVNk8s/8svX5etygFy+Ll+XA+Tydfm6HCCXr8vX5QC5fF2+LgfI5evydTlALl+Xr8sBcvm6fP1venmXfwT8jdOI4umwSOIpghzPqvq3WVziUjEL+1zp2k9z/xdniPfNEfS0z/hqzwaqvRwgf8OuIAgLgb8nrUe7IdnEJtDdsypaFM/r80qUHzzHJWGfZtE929eeU7jxFF3QFy3cnv3Kks4zbgyXA+RvFFdEceLYIzSbayjPwxqLKTgiUqoCom4G7DohnT6ULRiNWIEQEmMNSZogrCEulYjLFcIw5vSJo5w5eRKlJN0kQ0mFVzxfKYmnFEJKPM/D8xTK81BSDMQrlOchhERIiZLusYKCIjFQuzMDHSZRKHoW4tADjSrHPdqkpWbde7cWLGZT7AmcSNWlX7v0RHVkPa118br9vcSdxNLzOHz97YRhPPjZXQ6Qv6GplVSKY4/ey+mTjxOVymjDgHPthzEW0DpBWoEUCqEEXuBjsejcAAqlArI8p9FagzxjZHyMiZmtDI2M85lPfpCPf/D9KN9nZb1N6PkEvgcCwiAgigKCICCKIkrlmDgKCTzH6gvDGD8MkZ6H77nHKaUQKIQUG3whcvd14WGtxuoEawxWG4zWCE/hBQE2z4tFDcJYrHZELys0WIGxDnJrrcGgwW7S9RJ2U9qo0Tqn3eqQ5ClSeQjh4XkChcWPYvZdeQNxXB5oBlwOkL/BVxhGRGFIGMTgexgNaIsMPMCS5wox2IkF0vcAifYMUiiU9JFZTtmUMXlKFEUEvo/v+dTrwwwPjyGVhxUlPCUJfIlQgsD3icOIMAqJotDpoHk+yleEQUAYRSil8DyPwI9RngQMnhc4bi8GqSQCiyqU06UAkydokxfsP4tQ7pSzWrsAKU5Dre1AIdHmoI1GIhHKBYTR7pQxGIS0CNxzsKBNhvQCvHaXXOf4kU8UV536ouc9q8bv5QD5m6ZwLqU7HfqZuiwE1ozBWA0IjDUIYbBGYLV1ulfaYCQo6W2iprrnYY1LVoyrR5AGbTU21yihEFZgCnkeay3aaHSeY5Xn0inPL9Q1naSoHWhhuX3cGINQtiDkubTIvVeJtgJtQAqFLJ5gtZNhchJVAotEiIJiawRWFEEmBEJaEBaBQWcWaw2qSAutNWAEFqc+o5RC6xxPSJRwgfj1BNovB8jfrPgA6SE8D5RE2EJ9UmRgVeFsYTaEreWGFu5Gjm6wwmKERSFBepjiW+5xLj1RRV4vZIASbh7Ql/z0lBPFi0oRYRgRhiGe5w1qIaGKBSldPSKVQSkP3w9QnirqIfc6Uik8EwyUNAUWjF9w4TVFJgU2QBpTBGKhQaZ1QdG1A+lXdD8ldTJInu/hC5+etUjVoVQuIf0QKSw6T0F6z1rHey8GFn+zUMNmMn9fIODJnGapnAjz0xH0nywq8GROdJ/cv5n8v7lNuVleaLN+7ubnXSpKcCm/erMgxZN1mPrv69mUBTf+hm+W1K0VcrBjS+Wh8FwRKwQmc6eBznKMlAghB+ohG4IQhcS/FEWR7R4nPA8rXCHsAsGJu/VFzYVycjzGWM7PLxMELYLAIwwCPM9JvAosSgo85eNJgZJOGFpIt1gDz8dsENHd+5ESib2UCuuWfaGIU4gvWIOxwhX6uAWea4MQXvE4je2nWYOegEUiqNRK+EGA58UYYdF5TtLtIpX/rM027/nYF2zWYHI/cFnoHKmBZI3WmjAMEALa7R5xHBQaVhvCD61mt1A0zJBSEgSq0KSCVst9z6miuN3BmiKojKHTcQJt1tqBRExfec/zpBMk89UlC18IUUjN+ANimNaGPM+LX6y4RFO3/9r9Xc0YQ7vTo1QoCWaFunhfA8paS5bpwev3pWg2RK15cRXSEVgDRhqUFGAVVlgEEiUUSIGVErRBJykyDotOUl8VRW5oSUlQQiCFcKdAoWDieRLf84rdxQ5kWqUSNBodHnv0CacTFoYEnsKXBj9wp4ZnwRNF8LnlCkhE8S9brF6rDdoaBKZIDftrzhXhshBHTwrpKFu8YZc6uXWtrXVpmDVYrXF3s4NTxBoN1nDzLdezY9c2F0wItDV4vsL3g2cl0npf75dx9uxFpqeHWV5usrrSwgJh4FGuRDSbXdI0Z3p6mLNnL7J16ziNRptqNSZJctbW2oyNVTl3bplyKeLKw9uZv7DCykqL6elhzs+tOAVv60TLhofLA4nLkycXmJioEwQe58+vEAQ+IyMVLlxYZe/eaarVEo89epKduyZZWmrgKQlCsDC/xi237idJMh54wLUst20bZ2FhjdHRKouL63Q6CbOzYzSbXWZmhnnwwdNcccVWJqeGefzoHGfPXuTAgS001jsgnOjcynKTrdvGGB6ucPToAqOjVdrthHPnltm2dYyjj59n795pHj96nisPbeX06SUOH97+op8eQimEpzA6QUgfgSLXacEUNQhPgXHLsV/sXnokFu1U+oEmsC6xKQLLLUJRnCqerzBGI101DFYUSx3OrzRItMD3FEoYBMKdGkIghKs5ZHEcSClcSthvsQ4OC4sQtqhdrEvwiqzAFdtOM84aM2gZu33TNXdtoStsDehBm9sFidaWii+YqEaYXBfyVRZP+kgZooRwsx8hXniASCkK2csIrV1POQg8lJIMDVUK9T2o1UrEsU8Y1rHGSV32ehlRFDA9PUKSZBhjilahwvcVcSkgDD36KXJftTAIPMbHa5RKIVJKpqacRGYch8UR747m6ZkRqtUSzWYXpeRAq9dJbSpGR12nolwOiaKAOA6YmKiTJBmVSkSea6IoYGpqaLB+arWYiYnitYUYqPzFpWCgpN6XL5VSUK+VUJ5kZmaYKPKZmh6iFIfMTI8gpXjO2rnPzw/C4NpXAVb0B4QuVRFCIEw/bbXIYuOQRe7en8QPLCFEYbUn+wV7YQshQEkIfJ88F4PZhqeU8/ATgm6iaXb0xhOECzWJm43Y4gSVWKRwrynZmGcq4U6N/nM2aomi3CpsO0wxwlC44OhbA5pLJIpcgGR9mxvpfkxBxcNXLv3rp1JSSSQBVijE13Ee8L6ehtLEhFs8Sjm5yChyerNh6A9qCCkF4+M18tzluU7q3rBnj/OuGBoqDxTGq9XIKfsh2L59fPD8gTlKkY5Vq/Eg9xweLg/SosOHtxcmM4bp6WGMsYUiurvP2FhtELR7984MPsfu3VMI4aRG++9xeLiMMZaDB2ddypWmjI/XmZoaIs8N9XppEHDDw5UiBTNs3To2SDEnJurkuWFkpOokUuuunz4xWUdr86LrYAgEVms8z3cTdWNwS3CTpKrdEMO2uHaokj55UeQWzgJu1Un3RwiF7AeWNIUsqWvVimIxBwiUAJQuFq+7kVT9e+BqHmHxCllTWTRRpbCoIiIlFqlcaqSNIfQEoZJkuUuZEBaJRUmFxPmmaGOJfYkBcu1Oj8wYvH6jwkJuLR7WBaGxWGEJAwlSoZSPVAorpJuzaINGuhSr6Kw9rwBxu7DPqVOLAx1VpwkbsXSxweTEEFNbRnjogVOsrrbYtnUMYy1h6NNsdhkacunS0uI6Bw7OEoYeiM2F8kaNkOf20t2jyOn7i2vz9/Pcbvr6pQ2AJ99nw/NDPEkM7VLlwjQtaqsiSPt1iLvfU0/gfrG++bH9+qz/9/Nxfnp+Fbpx6utCgM5QynOniHYFqlCeCwKtXbtXSaTwQEiU9JBCYfutnqLyFlYihXTOrkoMMKxSCqQVblFJifL9gXuTFILQh7gckOSZK+wRBJ7CU85SwS/a0aKoR1TRGLBoAiWxGlJtqISKaqjoZoZEW4S1KGkJfImPoJ0atNHUY5/MCpLMdbd6WUagFEoIuklKZop0zsLwSBVPFslg4W2jhMIIgfR8hAJhDMr7BrpY1hrGxqp4nofRLYxniGInKR+EHta4XVgpQX2ozMLCGrVaTJY5h6Q4DgbeHs8GQRPiqZiZzYtr8/ef+vVnvs/TFchP/1pP///nssA3Nx+e73NfqDSpKIDYShRQDjdSHqQWoujYuVRIOSF/C/TriEF4SKTFtXtdoYCSEmlF8VzpvieMg3NIge+HeNJp8u6anWRkcop7Hj7O6nqDShyRZAkY50zmSeXSmSLF86TAk6CtIlQCLZxxbCn0iQOJRbv0yboTLFICX0kyo9FGEvgeSgusLnb8QrhaCcOVV+7FGsPJU+cIwojvet0rmZ2e4N67vsLp06ec6ZFS7gcELmXsW3G8kC5WP6WpVl2aEW8ZGXy9Wo1dmpJqZmZGmJ0dI881tVpcpFQVjDEopQYpz2WPwhdnEKI8D6Ek1mRuz9YKicJgi4I1d7Zlrl+LMaBsAb8QrhUs7IaqoCzauhu2e3LwvX5RrITTZu6XO55y//f8kInhYSbGRqnVh7jpmgMsLy3w6NETtLsJXuDhC+n8xqXEkwbpDBLxPIXROZ62xGFAOfKxKsckGmktnjDEQYCSgkwnaCMJfR/rWURRc4RSkOWaSq3Md7/h9WRJl2NHjrBlZpbp7TsYqlU5/cRxzp09S+AH+HHZQXOM68wJaxBSfWNzkCcv7P7/TXGc5bkB9FPElsUgXbmsR/dizgkFEs8LEECW9JCyUE0vOlO2aGBgB9M/rNUOE1V0jfpnqBgU+Gag3E4/UDaZulpc69d1kMzAwyVNE5QnmRit0TWKvXv2cMeNh4g8xWfvfgBBiFRu51bStYK9wg7P9z2slAipCZQi9j1XZGuL1ZrQ9ylFAVIIEuPU48tRQC/LCUOJkoLcGrQn2DI9wfDICMtLF5jdOs3OHTvBjxwaAIOSCuX7BKELEG0yTJ4WJkvBs5o6eS9GU+XZQvBycHwzhuk+VhuEKeYZUroWLf3ZgcSKjYIca9zJ4RJv+vgKS7/eEAMDV4oJtEPLF5thMaOwxhXLBoUUkl6WozxJtRLRazj/jyAuM1SJMVlKkvvOPgODpO88q1BSEAaSNBNoIZBK4iuolSO0tYRhxcFDyPCVRKXKFf/So1wOaaeaRicjCgNa3R5L7RRrIUtTpOdjlER6CuG7A9F1sVTRNFBgU5IscY2dsHQZavK/G6pXCInyFNbP0VYjhOd2f+MSpT5Q0TVECpdda5DWugWC3UDYClu0it0UwgqBlWJwUlhZDOLow+eL9EsKkjwnt8KZZMqUzIL0AuJSjLGQ5Clh7oFS0H+ekAhh8aQhLEkyG1KplBgZG+Grj51kanSISrXM4nqDamWIEjndTJPmFhGX0UHIStLkxPI6CoMXKs6fmufXf/fPsHnK+EiN7922i3qlgiF3tVTRUeuPLXSB/O136Z4t/fe+1b9c1x5Vz3qybJ7SX76e7C9Z8D88D89G2DzFmLzgXrgptKM6FLgm7MB3vO+aYzfp0fZHGFjt0jMBtggaAeS44FFCFt0okEIjFXTSjFa3R5ZpemlOu9tDKEW1XscLVOHwm6M9D6PcCSaEwGhLvVri0L4dPHp6kbWu4ej8OufXeyx1F1hrtKnUKqyPWEaigOHaCCOlMkuJZu7iCu1uysT4GGvNJquNdZRUfOmehxgaqhKdW6DV/QC7d2/nO+68jVIQDvgoxro5j7Yptj/I/DqK7d5z9XPoO5X2je77cIrnY8EUhgHIkDztYLR5xswsKpXI0/QZvfy+3uymb+O2+Wv/e2gPC3SWYo3GUwFGSZQIimm5AOVhdI61eWEgU6RIdkOYeZCGCTHYPd2EW/RnfY5IJAQaizSb2uQYbIGAFULQTbPCujpldaXJ+loLKRXlaoXQV7STHGsNWudYI9F5TigNV+6b5YoDezh1/iK9zNnJPXpintXVNkHk0eqltDvrXFxqIpRgamyI2alpOknKeqvrTESlLTp5IXmaU6nWi7TJct9jxzhx9jyryytMRW5GIq2b5SRJgkm1g6oIwHyDAWKtJYpDEB5pt00Q+Ajlk3Q7z3nBWeu6Lw89dJyHHnqCV77yRsbGhwr/vUvrFa0t9/7VI+zePUupHLvp7vPI0KNSGWDj/VlLVCphcvfL/JteFFmtHbGogF9Ia7FKgbbu//QBrXZAshJ4g9K8P5dgE+CyX9ML3NxDGjcGt0Yg9KbWsgVrJVa6bpjOjQMDCo9Wq8PqeoNcGyrlCtUootVrDrpj0gqmhivccu0eLIJHnziHkB7awJFjZ9FW0Wv3iCs1Z3mdgPB9rNYsrjRoJwaTG/zQp93tkCU5JjeAJAg9tLG0mwlZ6IAmXpDxlfsexaY9to+WCKMAJUFY99NR0sNT/tdFlMpn99wTdHs57/6d/8W/+7e/wQMPnuBDH/oiH/vIFwmCcNBA7kM/+n8/eTfvDweHhyu8851/wIULF1Geg5X0v6+1wfM8VlbW+YEf+HkefPAJ/MC5um6+/8a/7SUOpkIIkkTzy7/0u/zyL/0u8wurIBRzF5b5xf/wbu6660GkHxSvaQenk7UONt1/3w5OYwYn5+bHv5AT7UU/Q6TCWEOmM9fD1aBQoNwAThTzD4xFWolAOjhF0dIVwnWrpFQbFNWB97Pqs1sdOclupGiy4KEoqRwXA0maGtJUEwYx2hpWmuukGqq1EeIoQmeWNHMOwKEvueW6fezdvZVGO+X8whpLyw1aPXhibpkz5xYIKzHCC8m6FqEkWa5JM9cabjZbrKys02y0ybsZJsnRSTaAvGedLtJA1stJe5alpXVybTDC49zFJsuNppvzIFBIpPDBSIQ2zzoIkc/WfcpzzdDwCEpJPve5+7jx5iu5484b+c3ffD9//McfJQgdFisqxfi+R1QqFchet3tFpVIBUQkRwNTUGNu3T22kUpGPUoKoFBKXIrI0Y3p6jC9/+be58caD5FlCpVYv7u8TlUpEpci9VhwSlyuDU0xrTbVeZ3Skxgc+8Hm2zE5iTc62bVNMTY2wZ88snucRxyFhGBCV4oExZlyuF3wGiMsVolKpOHki4nJ18NmiUvzNw7A/10GhclNvt7E4lp6SxUDPWqzsH5J2UGsMeBpCDTjfssBUbXQhC7BTES9C9gd80uG4jHUZm7DuYdZS9gVZt4U0CZNVH5I2axfnSZprjFZidoyWmaqVmRmp8KZX30jgCU6eXqBUKlOrV/nig8f52sMn8KVHaWgI6fs0Vlsuk0gSApExM+wzU1EM+YbIM3Q7HfJME8ZhgQo2pEkKVhBGEZ7vrKXJLXMXLtJud7BC8Scf/gIf/+K9lCo1pPALRymzqen9gmsQS7VaYmJiGNDU6sNcc81ePv/5e/nBH3oTURTylbsepNPpsbbW5M47b6BSLeH7ik9/8m6CwCcIfPbv304UBaRpXuzWktOn52m2Ojx+9DQHDuzg4BV7ePjhY9xzzxFe85pbCYKA//W/Psru3VsYHanx2c/dx003XcnMzBh33fUgnU7C97z1FfieK/7SXou/+2Pfwwc++AX+4s8/yfe+7bs58cQT3HjDQaZmtvLQAw9x7pwzgpycHOHa66/ksUeO8YUv3M9rXnMrI6ND/MVf/CXVapnv+M7b+MLn7+XkifPceed1fOlLDzIzM8ZLb7+ePE2+ffWMEC53pr94bV+LwH1v8AuXCApnWuG6T1JJ91gjUEJu8Er6fHFp3XOM70QgcNwKYwye9R0JSlis0Uhg+/gwpt2gl3XZMRQRyIyHvvA5PJuzpR6xdWgb5VLM1m3jjFV91tczLqx2We3kNLsJPWNJc+2CXkqyJENnCVZbdo1XueXANFvqZdI0Y3G1yfxak1OrbS60Nb0kRfkeJs8wuXHweE9htMZqB0XxvIBGovE9zVjZ5+jjJ9k9M8mu2S30eh3X9vbENy4c54zfc8Cj02ly6tQF3vzmOwH45Ke+ynve8wle/sqXsLy8zs/+7K8RhBXe9Vvv5wtfuJ+bb72B3/iNv+AP/uAvCeMqea5RSpF0e3zf9/0LPKXYt28b/+//+xtYY5iZGedXf/W9HDt2lvrwKF/+8kP85//8p8xum+Xw4T385E/+MsePz/HKV7+M973vs3zso1/BD8tFOuSWx0/91Pfym7/5ftKkw/nzS+zcvZVjR4/xr//1u7j22v3cdPMh/v2/fzcPPfA4W7Zu4bd+6wMcOXKaUnmIxx8/w+///ofx/JhatcQv/MJvc+7cIktLq/z5n38apYIX7DD74pClGEwvlOcPBHKk5xDWWNeqlaKYjRSDwL7KSR8+KCRumiwoIOl2sBikFEhjsTpzdtBZRm70gJZrcRyaTrfDqbPzrCycR3WWCXsr5BfP0Vu+gGivEfZW2Tbss23LCFmakhnBucUGR05d4NiZC6hAonxJGPl0Gq1iDGO4etsQP/KKq7jj4C72zoyyb6bOvokh9owOc+XUCFsqEmE1URwX8F6QQUBWYOqEkqCkq8WMYHGpTavdYXyoyl898AjnFxeQgQ+eRBaZwzd0giglWV9vcdeXHuFTn/wir3/9S3nN6+4Act77nk+yd+9WTp6YY2pqlEajQ7ezzp//+af5pV/6CXwffvqnv496vUqadPA81wnzA4//9J9+mh07t/DYI8dpNNp0Om1Gx4fZsWPaFVJKsX37NNVqmWqtzrZtk/i+x549swwN1diyZZzFxeViuViUUvQ6LV756tv44z/+GO/8pXfzAz/wnZTKdf7iL/6ULVvGmZqZBWDv3q382Z99gn/77/4R27ZNDXrku3dv4cyZBQBmZsaZnZ1ky5ZxbrnlMN1ujzRpP/8O3oueZjmBhjRL8AoWoCiUPKwxWKUGp0w/g7IFbqk/YO+zIl1XuEjDkMWAUJAbjZHgSQ+MJctz0jxDGzdo9BRMBq4xcNOuMe64cTvDo3WMFaSZJk1ySqUINTTB4/NthPJZbrYIo4jzF0+x1u5ihED5PngK00vQSc7O8RI//OqbueLQ1XTX10haq7SbUI5T6qUAIwzrnYCVXpd2kiCVKiDzBiMsnu+BBJ3lbi4kQIUeZxbWmFhc5ordW3n02AlePTtN3tH9tsU3coI4TFatVubW267iDW94GX/0Rx9lZXkZaw2Li6ts3TrJ8HCFG244yO///r9ifa1Jt9ujWi1jTcrhw3vYvnManWcDt1KpIkZG6nzso3cxd/6igx5Y16VxJvHuSpKUUinCWjvghHieYwzmuX7KvKRfIvzIj3w3f/mXd7nU0MLy8jq1WrngRGhqtQrLyw3YhPrtGzr2i/FeL8X3Fb7voP1B4H2baxBb0GMLYQaTYHROrjVZmg3qi3471w0OASEHu6QUcvBHDIiuAtEnIBV/G2PJtYOxK6FcDaIzBLp4loOnhL5iebXDqVPLnDm5yJlTC8yfX2NlpcNqM6XbzciSnKWVNs12SqvdJreGJMvIUo2vfGxmMHlGKYQ7r5jlisPXMbHvaoamZikP1QjjiCgKqJYDyrFPPQ4YDsBmXYI4dJuCAakgS7pIaRDkjjFSDEGlJ7n3wWNcWF4hDBWtZoNAeQ6L9SyAxec0B/E8RRj4CGG56up9tNtd7r/vKK941cuIQp9Op8fwyDCYyBXL1ZKj1rY6CFlCZ2267Q5h6Iqjer3Cow8f4Wd+5tf40/e8k/W1VcARk4RSBIE/oPEGgT/QK/I8VahTuEUSBB6+7z0NulYzMlJjZKTulDQEjI7UOH9h2eWdQLPZZni4Onhe/z69XorneYPP7XleEbwuhZPfRitgW3DjlZQInbn2OQajM4xxvt+26HIJXMuq34HrI1etIw4W5CqJshbP4iDvyiuGi9rtxqJAphQUXWMMwrjWea4tK70c00mYW0s4stBipBoT+Ipa5CSCJreMMJ36PHpyiUR7rKy3OLO4RhCEhGFK0svJel3XUNCG6/ZOcO3erVRGxpzWVqVM2iw50KPvEXo+JT+lFoRMxD6tLKdVzOis1khPgfBAKzffMAJr1YC/oo3gnvuPc9X+PcRxCW3s17U+l89lSDg/v8y5uSW6nRZCRhw8uIMPfvALrK2t87f/znfzh3/4UR595Ajnzi3y0Y9+hVKlypvedAe//ut/zvyFJb569yM8+thJur2EM2fmWVlp0Gq1abW6LK80ueeeI6ysNLh4cZ1WozXI+bMsZ25uiQsXLmKMYW3NfW9trUWea+bmljh/fqlo926C2FnBhQsXOXNmnvVGG2zKG950J+fOLbC0cIG11Ys8/vhZ3vKWlwNQLkecPn2BTqfDY4+d5OzZBdI0ZX29xZkz85w9u+CO8b8GI5T+NFqbHKMtaa9H1mujrBNq6A/5+mxIjAWj2TBy1QUKSwyaV0YKl+6owIEajUtXPSXxilaALBRNhBQF/VYig5DacIVyrYwOS8w1e8y1Mo6vpjStYnxqjE43o16rsrLepZMZuqmmmyTkWhN4HqU4IEtTSqHi4JY6kxPjoCQm7yGFQQmB5wcEcUAQBUSeohp4DAchdWXJuh0njmddvaGkJO318H1/Q3ACibUC6UtWlpv81QNH3WYsBP4mXayn+/Wqn//5f/mvwYlybe7M9KfRrWaT1dUGBw5sp1KJGR6qcuDANk6fvsDkeJ2X3nE9W2fH+dxn/opWu8vNNx8iCgNuvfUQ3W7CV75yP9VqiVtuuZonjp1h+/Ypoijkttuuol4vc+TRJ7jplquYnR0fEI6mpkaZmBghChVKCXbunGFmeoSVlXW2b59meLiGpyAMfWZmxpmaHCIuuaNWKUnSSzl3boGDB3dQqcSMjdWYnBpj//7tHH3sFHPnFviO77yF6284iM5TDh3axWOPnSIKJYcO7aZSiZmeGmJ1tcnu3bMIIZiYGCYMg02qIN+O2kNx7uxJOq0GJk1Iup1C3MApkOQ6QUjpTpGik9Mnhynlg1T0ASjagslTwigkLg9RKlVYuHCSR+6/Bynd4E0pie87xRDP8yjHMXEckuqMpYU1cm3Yt2c7t9x6HQf3bePC0gqNrkaGAQd3TTJcr6K8gMgPOHHhIicurNDuJTQ6PdJMU69WybOUbithcrjEq6/azZXX38bUrkOUwxCTNGguL5J0O06rK0nxpEeOYKWX0koSciHRUpH1UoR1G4M2BuU7PJrO80LLWLpBoXJp9LbpCSbGR3nkiVNce8NLqFQq6AJxsbEZSUSe9ay1hjxLnzF9CKIQUORpjzzP8X0f5QdYnZH0UqJyiT5L2Bb5MEIQROXBXDdLem7WoCIgI+0lBFHJRbjJQAZgc0fOLx6TpxleEAGWpNsppvghJu+R57q4vyFLek8BnLn37INJSNMMayxhKYJCa0kUnTQBBFEAQmHyzB3TBOisg1IKZAjkZEnybeW0WGvxPJ+vfvmTXFw6T9pco9dpIwBtDJ4fghCEURkjFVmvR6/XwqII4zJRqYz0lCNQWUGW55i0S61eZ3himvrIOPff/Rne+9u/QRBEdLIMTylKYeBosb5PrVqhXq/S6bY4+uhJVlptDh3cxQ03XkcgFQ8/cZbPf/VhIi/l1Ye2MVqvMjI6yom5FT77V0dpG8GRs4u0kpxcG8ZH6ghpWZi7yEsPTPL9t18NE/tJVQi9FUaCjJrQpJ0OSdLlzPwqdx89w6mLTULfw1rD6ZUu6xp0agAPoZywXOAr8ixDZxbhWaxxg9JSFBEEiluvOcBVV+3mzz/zeT7+/k+zfXYbSZJcwmoV0vt6NYgd5OMmT/B8z3UJijw1TXOicoTVOUkvHcAX+i/SbTc3ikMpSdMMY5IB2rTbbm3Suko36U0lA+Rn3mkRRQFhHIPR6KzrsP1K0m03BmJmT756nS7WdlxaUKBPe53eJq2sdPC8XjfdoOGmOdZ2kVKS5xpjes/4Gt+eSboky1K8ICICep0WebfjGIS+j03aGCuwudubhCqQuKLPIXeKg0ZnGJ06FK8xA8E52VcXMZkbQgqJFjmi0OC1RZZm+z8vYch0giAkqg5hg4C1ZgOES9FWml0uXFyjUgqZX1rHKoXOEzeoM4ZOtwdKMFENqdbq1KqCo4/9FXPz55nzPa45uI/Q5pw6c4Gj55eZX1pla73KxFCJzGg6Sc7acg/lBxgtXCYkccqNYoPaLXDQGClhdnqc+x49wuNzx9GhcnXI8y3SrXXtxIWFFY4fn2NsrE6WOR2pPNe0Wh1uvuVa/vXP/w+shX/zb3+CbqcxIJ9s1pXqQ0OkFG5X3tRv7xfWSm2cXv3HuGk+PPDAE2RZThSFBIHP2lqDoaEqO3fNOglMu6Fl1Q/Q/oLe8LwQA5EJsIWCuN0kQLdZUE5uoGaLANsgiwm+jTPC4sS1eNIjK6RCM2uJinTIGgvaIJSHR1i8Z8dPtzpzcp+5JteZQ/Bag7E5WI2wOU78Q5DlhtB33R+yohkqXdVqpVNENNIWuCZJah1dthR67B6ZZHiozMLqOlFVstZsEcQBa+0uQgqiKCBLM6xxMBSspVwpMzZc5eziIus25viFNnsnq5TKJerDw5z64r0sLbe44Yp9rBvJ3UdP0Mtz6p5hOFas57YQsbaFrpxy7x3QmZNTFQpaSQ8jDENDQ7SyJnE1emFFujEGP4j5/Ofv4/Ofv49afZR/9a9+i09/+h7K1Tq/+7sfZn1tlRtvvILDh3dhTE4QBPi+k6CMShFB4GOMKaAd0VNYiWEUEkbBM6YuxliCKOTs2QV+9Ef/PcYYqrUKKysN3ve+z+IHIb7vORKOkkSleNAC7n+GIPAJ4wilxEAOKAicgFwYBoMOlecpwjgcSPtHpTK+7+EVA7j+4/vdtW8XmtcUg1aLHujP+gXEIvSDwWdzLU5d8Dk2MFFpmpDnmZt3SOFYdwUM3GoHPhTWwd0za0hNjjaFyYAuFBcLemFucGANYUkLW4O4VMWTsLC0Qlyvk/a6ZHnK3OIqBksUeugsY2ZqiCxLneq8gahUodHucu+xOZKwxGq3y/nlFtorMzY1gcbQMzA8NkE0NITwJI2uQwuPlFxl5XsCoZxekaGPPi/mQBKkJ9A9zepam727t/PDb30ju2e3PCvGznt2MYKM2dkJXvrSa5jZMkG5HDM8XGXXrm388A+/nqWlVe688zqUUuRZj6WldTxPUa2WePTRE4yM1Nm6fYZTJ86yttbi0KHdTi6z6D0fecwJu+3Zu83VLU9ziikl2bt3K5OTI+zfv40wjpiavIWx8WG67SZLS2vU644D/8QTR9mzZ5Z6vUqWpkSlmHNn5lldbbBz5wylcomLSytkWc7ISI25uSWq1RKjo0OsrTWYm1tkamoMIeCxxx5m796thVQ/xHHIhQsXKZUi6vXKt60e0cags6xo7eZIz0duUmsxxs0nTF6kQcpRn0WeI5VTJdHW8TSEzQf8c7fgczQarxg65nlOp9N1EkNWFqJxCk86/asky0nTQoHdOJkhZMBdx5bQ21NetW2GJ5bWGC6XWWkbjJVYYxgdqdLu9FjvJIP2c0lJdu3aTTg8ztnTJ6ldv5eJyVlmprfRXu1S8QNGaoaQLpOmwzWTFVYqPtiM+dUuJk3RRevapY2Q9nKMLuSLBNgCabG+1mLblklKfsArbryZ0PedncLzOUGkFGRpyuHDu6nXywPRMQePNlxxxQ7GJyf5Z//3r/LzP/8bBFGVu+56kO///n/J1772KK1Wxs/93H/nj//oI6yvd/nwh77EO97xe/hBmV6S8Yu/+HukmeGrX32UX/mPf0QQxs8YyUmSkucOoHbk0RPMzS1x3XX7Mdbj137tz/ipn/oVLly4yPz8Mj/xE7/MykqDMK7wZ+/5BJ/61NdQXsA//+e/xsWL66ytd/jBH/xXfOhDX+Kzn72HH//xX+TYE+f4mZ/5dZQX8Yu/+Pv80R99jN///Y/wa7/2Z/zET7zTpYeez/vf/zkee+wkfvDtg5u4QWvu/uQZxmjypEfa6dLt9MgLmU6ts0K/12K0Jul1izF6Ae7MdXFaFBD2AoKi+kK6VmC1O4hkYYRjCriJkO7UzXKD+5W5elEb6zgbiUZLj1BoJoYqpEbw0MkFstzQbHZYb3dZb/eQvnLTPQu1SpnayCgz27Zx8NBhrrv1lVx/+2uoj0+TpwI0+CbHdruMVSrcuHcb122fpuyFeELge07v2WiD1QJjJBbnkeIKW4kQHn7oo23Oo0+c5GNfuouHjj1eMAvt85+DWGMplaKiZ3yp6HMQ+AwPD3PlFbvo9RJActNNV9BqdZmdneAlL7uBKPJ55OHjXH3tIV7+iuv50pceAKF4//s+w/Hjcxy8Yh/XX3+AP/zDjzB/YWHQRn1qsLqC+d6/eox3v/tDbpFkOeVKlSuv3MXaWpMrDh3gu9/4CpaX1zl96jytVovf/M33ccsth9i3fw8XLlzkz977cfbt30sQuNblG954Bz/xk2/jk5/4Mp1OjwMH91AqhZw5M89v/Na/4Ud/9A1cvLjuFDRCj9tuu4qbbrrScZ+/XQND42oQJ7CgCqMcRRBG+H6A5/mu4aAEVhVuT0ohlIexxs1PjMVJ1vaV0jfUDYVQGCGdxYE1bgZRSOTIolZ0HHUnLaJzg8wN0qSgczKTktuURqvLymqT8XoJXzpRBqMzwJLl2vVbjVdQgKHRTfAExNUpysM7KIc1TLeJH5eojIxSKUU02j2azQ6xdNYMWTdFp7rQv9u0QAuefR/2b7UZSMMJ5YTovvTVh7jn0SN87AtfJk3TZ2zCyOfGJnz6tuNgSltgkzqdhOHhGiMjtQG1dvfuLQ7wlmSDafV99z3OyEiN40+cpdPp8Y53/ARhGBRdI/uMAtqzsxNceeUu0jTDD9xCSJKU2dlJQNLrtJyBSxhw/InTpGlOmmYcefQI/+AfvJU77rgeqx1cZXp6nJHRUe58+S1cccVujLFcXFphfn6Zq6/ei7U523bs4ODBHbzvfZ8h7aVYawkvQSR/ey6d50jpE4QxleoIlfoYlfooQRi5Rez5hEGMpxRhGBNGJXwvKAx2cpI8I9V5kRU4EpHAom3uKpuCfiss+IVonBQbaosSiKRHzQ/IuylzZ85x4thZVubnGbIpu2sVFJJmZgmigLVWi1olIvIDqnHokMRZkQoWAbq4sELeakKnTWBy2hceZ+HRv4IsJW+vEUgwVnKx0UBiSLspva5jnWoDnnDMSPoOb315VlMoD0uDNRk6N4Se61zpXBd8oxeBk+6Ef8VTpID6fIL+InZtWnOJinr/1OmrIKYF7+PAwV2kvXWuu6FOnrYcpCCMnsJWdMW1x/Bwje/6rpcipZuUT89MDWjAm1+/z5QTQnD46n3YPOfQVfsLSEPqilzrhqOd1hp3vPwGOp0u99/3ED/zs3+Hnbt20muvE5bKvO1tr+a//tf3cMsth9i2bRJjDOVqDauTwbznWwk1sVYXAD13inhBiLJOLDpPHb/BGrDSFKdMoYyfGtJuglK+w1nlGVpemhVQgP4EhTCEdKhdp+/LQFwawFOS8XJI3u3y+KPH8YHQg12+x/5tw05VJM9ZWm6ghGB2tIaQ0OhlNDrZ4Hcmi+6lImV9fZnu/Hma603Onz3D7sPXce9nP49pX+TomWXWOobRmmZhpUGaGhpZSu5601TikPVeMjg5bF+kW0mMEXhCYoXGakMp8qjV62zbOUNcKhH4gaufvhGfdCE8Op2kWPwbbVCtDWmaDdCwnU5SFLaimHtsSIF2uylCwMtffj2f+MTdJL0WQVTh4QcfptPpcc/XHuPTn/wyvr851XKt4W7HDQdHxoYZGqnzoQ990cEkDMXrSzxPkSQpvV7KwSv20OslfOoTdyO8MvPn53n04WMIFdNud4tWr+tQ6SzjL//yLo4cOc1dX3qAj33ksyjfI+21ufnWa9Da8IUv3M/k9DS9bspf/PnHOHt2wcnvfAtPElEYeYJyMqLKQwjl7M6UHCj45DolzVJXO+E45LnRZFpjrCXXmjzNsfmGNJDbvLRTVjf9yb3T8cyFg7h4no8UEmPdSWKTLtnqIuM0uXN/iddcNcorrhzhzoN1Xr6vyvahgHMX1hmplti/fQxhDKGSSGkRygm3aZ0xPF7n7Jrh+Pkler0ma2srbDl4FRNXXM+BW25FRGWuP7yHK7aNEKiAUwsNLqy16VmBloJceDRTwVCtPKBoWysGCvEUwMw4ijDGsmvHLD/6Q2/hDa+8k+982UuIwqBQcXmBJ4hSigfvf4g4Djl9ep7zc+cZGamysrzM6qob9p2fu8ATT5xldLTGyZPn2Wbcgr14cY3VlVUuXFhieLjKww89wpve/EqOHDnNv/i5X+P6Gw4xVI85eOV+PvKR9/Cxj93NJz5xNarwA0l6KQ8/fJyJyRHu/srDjIwNc/TISY4dO8v6WovFxRU8T7GyfJGV5RWGh2s8+uhJrr7mCn7xF3+S3/7tD3Lq1CKVSsDtt9/AY48eY3i4xr33HmX/gV2MjNRod3pcf/0BHn7kBKdPL/LVrz7E6dPzvP3Hvx+At73t1UxOjgyQv+985x/yvd/7Sv7JP/sRsjS5ZLbzzT1BLH4YYtHkWY4KItfG3VCJc3x1KQi9wEn4KKdLaxEI5bo1WptBsEjp4sEUbVpRyJOKgploxcCuyhGulCNaWSAxOXmSs9LocW6hwVrYxVfKtc4F1IfHGKsopiaHeWJu2e3GVlMKPHJtwJekqaZSiji22OSJ+XVedmiK8tgQcSWk11phfXmNlcVlWq0uAksjSehZQclT9LIci6WXalIDgSoctNCuOLe49j6WNM+oD9VI04x6fZjZ2VnW1hv4QVAU6c+wKT0XqAlAu92lXI4dbMNaoijcdHJIsiwraLQhvV5amLB45LkzYxRCEoZ+AVmPCKKIc2fOo7Vm27YptDZ0uwmf/ORX+Y7vvJnA9wc1Tq+XUS5HtFrdwWS0UonJ87xoBasBr9z3Pbpdpz4fl8u0my3Ozy0xu3WSKApoNFqUSjHdboIQUK6U+Rc/++v83//8hxgZmwTgA+/7GHNzi7zxza+isbZKkmTs2TNLGPr4QcCDDxxjdbXBS2+/jiz51hTsfajJ1770cc6cfNQJRcc1EG7BSyXRSYdOp+2EFDwPFcROnFl6LK81ybRFYshTTbPdZLTmM7ttluGxWcbHp7j7Cx/lQ3/yJ0g/ZLmxThgFVKtlIuVRDkuU6hWGh4ZorTV4/LFjnDl3jm47wReCOFIEQhJ5ilIcYoGJWpmDB7axbf8u3vvRe1ntdHniwgrNLKOXmaJgN6SJpuKFvPWOq/nbr7uWRqvLyZOLNHqKkpCszC0yN7/AxXaTJ9bWUYHHgek6zU4Xg+HIQo/Ta4k7LRDOI0U4KErgOTRBr5WyZ/dWut0uV+zbwf/1treQpintbsoP/tDbGR4ZI8+y5ws12bhqNSfb2PfgcD4h/iZIfFT04W3hAOVeJI5DpBcXmKiUctm1c3udDrOzE4WSe45Ukm63x0techVRFA3erJSSSsU9p1YrbXKCMvi+v+mUc7uAH/iEcZUsadPrOIj93gPbyRI3KCuXSxhjKJWigajElYd28/nP38eBg64jp5Tix97+Vv74jz7Mgw8+wT/+x99PFIXOViHNqFZjrrhiJ0qFGPWtK9iFKOA51tk+a5s5vSpjybMuWZYO8u8sSx1ZSJWhmLjnudO9zfIcXVhUWGOdq5SQKKfWUBh1ugGe0tK5OhkD2hXzUjkhuiwXJImlo6ArDIEElVtiJJEfkLZSlh44wSvrdcZHYpbWmvhKMR76NLoprSR12GJjWWu2+eS9R/mB192I50m2bZ+mPrKFTjPnYmmIWininiOPUY88wljRTBKsgExLVrqFr4nw3elR8FWsMWQJqNDRQgLP441vfT1z58/z+LHjnDhzlk6m+d7v/7vPCHt/zjVIX0HEGDuo+vuF1obqh930GINUihMn5vh3//Z/cP/9j+P5oRtQFcaSvZ4DAKZphtGGkZE6o6P1SyJ5s92A1mbw59JOWv99CD76kbt45y++iyRxvA6tDUk32QRHMZfeM8/4v3749bzkJVdRKYdsmRnlta+9BaXgyit3EUXOoqvP5zbGsHP3Vubnl3nvn3548Hm+ZXwQ5eYGrvkhB2adOkvJer2BGo2Sqt/Y3KBNFx2sRBfswFy7zo8oXG/7jjW27xxbtE8L5Red5wOnJmMdWy+zlq6GrrZ0DXQR9IwlMdZJhCY5o6NDAFTKIaP1mLKvGC3HSCEJPA8seHHAqfPL/OmnH6RSjolCD6mbNFee4NHHv8ZDJx/BBBkj1QCModvN8KTP/HpGs+dApm5qLgdyq/3GginkibTW3HTdNRzcu5PPfPlunjh3lpmJEaIwdBvCN8JJ3+xN2J9y9x2nNlQT7SXtYZ3n7Ni1lc997l6OHj2NVIWnH5Bm8Bu/8T5+/Md/iQvzK0jp0qQ+OWrz0HCzRE+/m3apxJAt0L0B4+NDvPe9nyzu89SO2obUjxn4GHZabUZGaszMjDE2NuS8FvOc3bu38KlPfY0LF5aRytskAyQ5duwMv/Irf0y3m2wCNm6oGH6zBomepxDCcw39YshHf+cvfMS11s4qLyqhpIcS0knjpJo8t+TakGfZQIXR6e1ad98+Js26esQr/EP6m57RGp05rV0hJBmQGUs3l3RSTZrlZLkht4JEg5UeJ84sEEi49YptTA5VyYxrGkTSI+vlzqtDgQwlf/KRL3Hm3CqB72GQjG/dzU23v4xDh/ZSr1XcCWkhDHy6acpio7NJ2bsgSeUuqEUx1A79gOmpUVq9Lo31dSpRiVuuu4bvuvMODu7c8ay6Js8pxYpKMd22g39HpRJJt+uYfX4JbE7SSwoouiTtJlggLpfptluEns/OnTNFIVt0vnJNfWiYsbEhlpZW2btvD73O+iUAw6gUk/aSgdKig7u79K7d6lCpV9GZ2wWVUoRxTJYmTE6OMDk5spHilSLyzEEr4nKZpNvB9z2kF2Jyd/8wjsjT1PFfWh0qtQomz6lUSoyPDw9MQ8PQuRSlSYeXv+IG7v7a75ElrrNXqlSBnF6n59JQKUm6L676SV+Op+/4pa1GFXZoZrB5uLYm1hYqia7dm+e6GIgJcu0WMtYOBOPoexQK0EYXbV654TQlHV5NeWrDVhrINWQCpDVsnRln1+wEut1m4aLTyEq15e4Hn2CsXuLg9mlslqKARpLRSRLnuWg0SgmyrmFsfIhOL6HZalOpSoTQkLawaUq31UNrTa1aJtWaRrPjLE/6hCfJwNAT2x+IOJ+bK/ZtJyjwdUPDw4xOTNBsNsi1/kZcbi1CKu764gPEccAjj5xgfHyYV3/nS7jvnod53/s+x2tfeyu5tnzus/fwutffxrXXHkQpwUc+/AXW1hpceWgPc3NLBbvrkqTNkXDKsZPK3DS9D+OYL3/pflZW1mm3e4yNDfHyV9zCmTPnOHXyPEp5PPDAUX7gB19LpRzT66X86e9+iF27t7K+1iBJ3FDPCyLuv/cxTp6cKxDDku9+48v57Kfv5tOfvoe3ve3VfP7z9xHHAW/5nlfxwQ98gt27tzE/v8TevVs5eHAn1lpOnZrn4nKTz37mr3jjG+/g0OG9fOh/fZF77jnCP//nP8SJk3P8yR9/nFe96kak8vjiF+7j9a9/KYev2kea9F7UIl5rQ5718MLQTdEL6IhBIL0NTrooTlelJEY4/keSpfhKkWU5WZYXJ44DJ1KoMBrbV2h0NNvcZCjr1Nz7kBKjnEmmsZa04LBHvuDwwd3cfN1h1i7M8cUv3s3Jiy20cRycNIfTF1a4af8M9QsNvvzYGcZGK6y1uhjh0U1Sts6M8jP/7O9SWZ+j02lhbUan2eLIo8dZWW0ThAFVKWh0EjpJAgKG6yXywLC61kXhFSY8bv5R1OwMlQKqvuHmW67FGEOaZwQF4FJ+HX8Q+eyDQUWvm/CP/tGvEEUBL3/5DfzH//hHpL0eV1y5m49//G4eeOAYt99xC1u2jPOf/9OfoLyYz3z6a/zO73yQN735lRy+au/AW/vJ+2G/dtncOfDCgONPnOFXf/U9vPo7buX226/lZ37m12m12vzZez/Fu971AV56+83ce+/jfOD9n8UPK/zCL/w2a2stXvHKl7B9+xR57oxAl5dWecc7fpeXvvRqXv/6l/COd/weRx49zjXX7Oe97/kE8/PLTEyOMDe3zCc+/mW+8pWHueW267HW0YylF9LtJiwurnL7HbcwOlrnv/239+D5MVu2jPOhD32RXi9h//6dfPaz9/DIIye5/Y5buPnmK/nZn/01kl7yoiugSFwBbQvMlC1+wVKB8n3XnqXvVGvxPEdDzfKcPM/IcyfyoPPCaEcIjCOpFxKj0vkVKolS0s1MtHFUX0+hC8dbUUC2tBRk1jI7PsLExBgZiqBUYuuWcaQw9LIMFZYQnsfx+WXCao2Kr9g1WiLSPYZKAb4nmRqp8XP/+O/wijtfhlSCMFQIaYgqMaPjQ8QlSWpzVjtd2oX4hycFk7WQK3cOI4UTfhBCE8fBwB03VorZkYirD1/J1Mw0vV5vMB3t2zHwQoTj+nVAGHp88IO/QlyKuf++Ixhj6Ha7DI8OMTU1yuHDewaU1L46yPvf9zmuv/4AcakKpNTr1eeUkzvYSswnP3k3ACdOLNBpN7n55is5P3eBv/8Tb6Wx1mRp6SJZltHrpRid8MUvPsC73vVzWGsYGqrieYpSKeIzn/kirVaH5ZUWCwsr3HrLIdbWmuzdu5XZ2Qm2zE7wilfdAggee+QY7/gPv8uv/pff46d++vvotLukvTaepzh0aNdAbC5N84GL1vj4EMZYPD9gamqMK67YCVhuuulK2u0ex46d4qpr9tPrvHiniGUw1XMTb+X0jJVUAzSvxSClR99WVueaJNdkubMD0FqTmxxjM6eZJQvLBM9DSkVuxYAvk1mDFYZq6FGOSyipBuLVBeCewBdMjI0wNDTk7hFEzExPMHl6nqNzF7FYapFibVXQTXN2bN3Ca99wI8Mz0/zxe97H6j2P8VM/9la+87veSKfZRshCPDtPieIKo6PDrK2uErV7eEoSKIk0jtOyZazOyPQ45xcaLK51ya2hEnsooBb5TNUC9syMMjwyXHBd7Ka0t9AP4wV7FFr8IOSBB+5jdXWd6ekxp8NUqEj0O0POQFMPntNsddldipwsv3iqZu+TeSH9YtkY155cWFhlfHyYHTtn6bbW+G//7Z9hkZyfW+QDH/wcN914iFIpcvl01itmBB6wod0rhGBhYZWhoSo7dm6l227wH3/lpxDKY+XiKlJJvMLKrNvpcfDKXbz7d/8V//Af/jJ33/0wv/Vb/3IAlHzqZ3T/zjI9gJlr7eY9WDPAp7nHv8gdLikcvbYIEIrfhZASk9tB40QWFtBS+GiTuhMky/GExFj3mCTtsnjhHLXhyaLj4zsZdJ1jTE5uFBiJUs4LfeBZK9wpVnCzKIVOmlV5TkNgpddhvdWhUqmyc98IB/YfYP/+3ezcu4+Z2W1MTs9ipcf5M0d443e1+KEf+mEOHr6SsDpFr3OWi6stZidieu0epVKNUiWmVCmhLjbxcNAX6QvWmoapLbOMj9S45YodaAFnl1d5/NRFqrHPbYe20V1tYPMc31d4XuBg/FqjdO4o4BsV2PMLEGMMUVzmri/dx3/5L3/CRz72G1yYOzvwOhfKSfP0AYhOqseRpcbH6iwsrLhdrEiloih80mIRhKFfdGV8wtCRqx64/2H27NnC1772KFEUEkUjtJtNpBfw//w//403v/kObrjpGn73dz+IEJIgqiEENJsd14UpRNCEUuzcOc0f/MEiURQQRWMk3RZJ0iGOI9dwiJwFcFyK+eLn7+Wqq/bymc+9m9e/9u/zrt/6C37qH/8IUopLPqMjhPX/rS6ZBfm+6y61Wo7qu2PHDPpJLetvvAixKOE0AbTRSO0U3Q0Cm/c90AWeUviej+eHyCR3p0YRxP3UVuealaUFep3OhqaAdbNoYxx/QnrgO39a8jwnDH2E55EZQ66d+EM3yWl2ejQaLTrdDoeuuZWxV7+FsantjE1PEwbBQEE+zzKazXXWludpLs9z4MAV7DxwPRqBxCeu1Dl9oUHNy4lDj26nQ9ZNBr6KEvCFINNO0mffvj2YrMnMuGMfjtQDrrtiG6UgxgfS6REEgrTTpNtYw2iDtoJcGgLfx1Pes/p4ymfrmVhriGOniP7lu+7j3nuP0m53OX58jsX5Rebmljh3bgGtNWfPLjA3t8jq6hrf/wOv5b77jvLQg49w7sw5jh+f48iRk8V8gwKnlXL8+Bxzc0vMXzjPxeUGH/jA5/ngB7/Im7/nO/A8xX/9z+/mkUdO8bGPfYWk22NoqMKRI6c59vgJ1tdbPPHEObqdHm95y8v57d/+IHNzCzz00BOcO7fIg/cf5Y47b2bHzmn+9c//Oo88fIKPfOTLrDe6nD+/xLlzizxw/zF6SYaQIcePz/HBD36eZrPD/v3b2TI7yeLiEufn3GO11pw5M8+ZM/M0Gk3OnXOf/+zZBcedsJZTpy6wttbkz/7sU7zlLXcyMjZWCLq9iGh304d+bPYjVIOmjecVXS7PR3khVlh0rp3urXa21bl2w1nfC5ia3urEM4zzMnczKlkYglpE4RnY6fRI00IcQzMwCA2lJJCSs2fP89WvPURmIt7wfT/K9v2HGBqdpNPqsLiwyPz581w4d5aFC3O0WivopIWHoTY8TZprAj9GSIEfSi62Ux56+ATCQrvVptFo0e70HNMzdJoIJtdUqkNs27uHcrVEvV5maKjGzNgY1+7bxatuv5XDV13BDTdfy82338iWmWGCvEHdyxgOoSQNClMo3z9zhDyj7I9rx+ZsmZ3kyit2cuHCArfddjXXX7/fUVCl5KYbr2B6eoxqJSQIPF760qsJA8nBK3dzzdV7eeSR4wwNVXjFK25gcnKE8bEaQeBUCjvtFkHgc8cd12GMptdN0Vpz3XX7mZkZ47Wvu5W5c4usrqxx081XMj4+wm23HaLR6DAyXOYNb7idMAyYmR7iFa+4EaUEC/OLHDiwg5e+9GpKpYiJ8SFe99rbWF1tsDC/yHXXHWDbtikunF/iFa+4gVLZsQN9TzE5OUytVuLc2fMcPrybV7/6Fs6dPc9LXno1U1Mj1KohURRw221XEYUOjHnHHddSikMmpsZ4//s+yzXX7MNaw+TEEG95yyvI0t4AUftiXEpJzp05Tqvdcq1dkzsPdKMLhcWsCAyPICzh+QEm0zTbLc6dXyRJEjzloY2h22kyNVrnwKGrqdbHCPyAlaXzPHDP1zAacmOQyhX4/WawkoJSKSbXhrnzCwRSMDlUYWZsiKFyTNZt8ZI7X8m1t7yMY4/ch+8HjthlcrTRGKPJ8h550iXrrOF5PvWJ7SjPJwhDt/50yn1338WxRx5harROr5fQarZpNrskSerENzI3/J3dvp07X/96Fs+dJul1GRofZ2RsijQ1TMxswwsiyrUR4nKVUrVGtT5EuVIiDj1KoUe1XKLVWGP/oRuJouiShlFf9sf7etCGNEm5/sYruP7Gw2RJl9teeo0zhTSW3Xu2D47mG2++qjB4yeh1Olx5eDdXHt5fSPq4TsFmeZ5KJeZld9xYuLI4sv0Vh/YAhqTbo1qJ+cEfemMhJZSSpgm1Wpm3fu9rwaYYrXndd91BnvZIkoTXvO52R38zmr37dwKapJvgeYrvfdvriy0vJUlSDh3eU3iG28LJKmN6epQtWycGwLyk22P//h3sP7gHcDvwTbccdn2kPHMCyUIBmlazyblzC/R6CdffcAjInKTQiz5h74MotEPUFv/v9/tlQYySnkdYLmONs3AGS14Utdr4GF3UEFj8IAJRcNOLIZyTOnYcdC0tVmh8Y8gyjQMAS3JjitayhxUKGUQknRZB6DpIedLB2gyNIMt6GOPSPJ320GmHLOkyPLEToRRSFVQI4+Aik+Oj3L3a5sLCGnEc0FhbJ01ylBIMlSIanYRaLNi+fYYgjgnCiKH6ENXaENWhCc6fOoFfLuOVK07l3Q+L2YiD8adJF98PMGmLk4+cfNY02Hsu+J9Oyw3X/DAg7SWFMAJYnbCwsMzy8jrT0+OF9q0bVvU6Cdb2CsUQOyh4NxPjmuvreJt79yIbqJ+4wVZjQP8VYuNr/Y6QSbKBoEKv09rUfUsG8HtjLN32pfdJesmT3pMTrLNpPoBaSClJkvSSe/U63cFr2NQNoDzP5+LSGj/3cz9CEPgszs9TH6p80/DuOs/J05TACwcCb8VUAun7Rcrg4wUxSa+LJzKwhlzn5LktFE0sRhdqL1JgpEULg8Y4lZPcFfnCui6VthZTeKkbK4qNQZBYQyw0nlIk3SbT27dz+6tfR7fbQFjtrAw8hckdbspmPbKkjbA5UalMWK6gdYKUIdYIJwUqoT5cJ9HF5E96LDe6lAKf6fFRrBCcm1tlcmyYw9ddhSF3rEMliUt1hobHWF9ZIkl7DE/M0G23CaIYgUNqOPqSIow8li6eo9FqFkiNF4jFstZSKsWsrbf41Cfu5oEHj3P//Y9z/vwSq6tNhPD4+3//ndxzz2OEcXmTzM6G7M/mOUcfyyWl5K1v/Rn+8A8/ShBVHLKy3RtANaylkAnakBHqD/v699w8Y5BSDjpOSslNkkIuNek/r7/A+4/fvBFIKQYSmxtyRBv32vwafQkjazXbtk3yuu+6g1d9x62MjNQ2bM6+GXgsowdeH07M2vl1GKHw/BghfJQURGFIXCoVautOlT3VGbnOXS2SayfSqzaU3YUYuO8MkAgOdwVGCAy4lMm6cIl9yUi5zFitRqAkf/vvvZ3dew7R6bRRypLrTuGeazBZSpp00NohLWqjM8XqsxswATRZ7hiftUrkIOuAtpagFLFt927K1TpbJoYIoojZfYcc/TsuEVZqxJUqMowo10doNhsEcQU/KqO8CM+PCaIQ6Sv8KKBUrpKmKb1ulxdsf+C8BQPOnFngne/8fX7yH34f27ZOkqSad//O+5iZGeNtP/BGZmfHL7FDc7ATD6sd5dX3faTn5F5UIZtjreVf/IsfYXJyBCEUn/3svXziE1/lV3/tX2LyNtJzSupZmjqijueRp8m31Zvjmbb1LMsxSTawKvtmvpYQyoHvpCgE31xa1PcKsbiZyNDwCFmespw5vQBjDNoacq2xWqCNHii720KuwSu6gFaCkf0WfsEstBKbOzqu1nnRlXKpVpblhH7AzLZdtDrNwurZnUayUFA3eY8s6TA2Nes4/cJxxaUXFOshR+seaZpQqpQYLoWEvken3aUWxfjKp9NLGJ8cxdiUlUaX+sQMWdaiVKmS9LoEcQnrKYanZjh3/EF01qNSG8Joi7DKnUiFTaUUisb6KnlB2bAvJECMsYR+yDve8W5uuOEgBw7uo9NaYXikxmtecysnTswNVM8HhaSnOH3adXv27JllcmqcCxcWOXt2kd27tzA/v4KUgvHx4YECe6vV4tixs8zPL3Pq5FmSXhut3Sxh27Yp1006f5H9+7cXGrx/vYLkycJ331wbaEOWuoaGkxDUZNYQeCHWgDGpm5WEMRnewJHKaItJMnLlYRCOMKWdWrsyro3j/NINWD04La20biKvJJ7vzDsHKAhr8ZRbaC9//Ru59saXsDB/HuUz0NHyhI/UBkuGNhlGg6d8kk4bP1aYQkc4F47CbJGU66OkSHrdHJ1rhmplKqUyutPDeAJpDDt27ac2PMHSQpdqfRxjF/HCEGtyhLQMjc0gZcjy+bPUhseIqiMYrRBpgjCQJm0Wz51zrXBPPaOtxbNCTcLQZ3lpkYceeoKXvvRqrOkipSJLOuzYMc2ttx5GCL2pzlC8/cf+Aw8+eIzxiWH+6T/9r7RbXYIw5md/9v/j93//L1lYWObtb38HQkr+6T/9r7z//Z9FFSw03/cII58ojvnpn/5PfOITd+OHFXq9lC984X43Z/jrdoDwrbQ/sIVKiUCnCVZrdJYjCuMbjJu0Gwvd1NBNskIKxyF4M63RuUbndgBu1H26gDYbdtF9k1Nd2B9Y18Hyfc91zQoUsNGGPE0plUu85Yf/Lt1uu9BK7uJ5nuOYSFXoIWuszsiTNlpr1+HDoKQawOidZ61E+IpO7uD51WoFP/LJrSZJeqwur6NTTX18Gun5Lsg9zzEDTY7ILb4qsffgbQR+mfWlecK4ilQK6XlkvQ5WZyzNn6XdWGN8YmSAgn7+0qMFZVZrQ7VaKroA7ntuQftuRDWoMwzXXbefK6/cxc6dM1y4sMyFCwvsP3iQrVsnieOIV7zqNur1CuMTU+zfvx2tLXEcMzY2RBgGTE87k88f/MHv5KtffXTgz/GmN91BXI5fVNjG38RLKc9x4bVB+AqERhUUAiPAaoFQHmnmunh50kOnmryAoOd6Y/JvCuvozJgB38M1eyTGZBhpkUYiDC6gir6ZKQw9lQxYW1vnu77nb7HvwFWcPXeygKg4DrjUZmDDYLVFGE2etAjDeDDPkcYghV/M6J0MauiHCCvodXuM1KukuauVXOonyLUhrg651Mi4YI/iKsIL8MOYUrmCUJK1ixdQCuJyzeHi/ID22gpSCNaWlhibmKCx7hC94vkSptx6t8SFNGj2JI9xrTVJkg6q/75u7U/99Ns4f2GZj3/87g23o2JHmpwcRkqP667bj7V9sQcGMA5XFOYk3XXe+MbbOXr0NOfPnWFlpeEYjVn2f3Rw9N1v8izH6H6weOD5G4ousjC70W424rrWjhdhtSU3lkwbxwmnOAmsxu3fhcSodWxCARhhyG1OmmuygqwmhedOKm3wwxKv/Z7vJ0l7GGNorK8O5FC1doLk0g+RysMaQ7fdxPP8gX+6YwLawhzIQ6CIvABfKjpphgV85QQqdAGhsdZQGR1Da5e2SaFQfoRUijCI8FWMUj7t9WWCchnphSA8dJawOHcGm+V019c4P3+B2vAQcRwPFCmfR4A4VZKZLVNUq2Uef/wMQsZkmcYPfFZWGtx331HARwh3ovS6Hf7e3/0FsjTjVa+6acCj2Og4uem861Y5x6jNHBBZSEcaYxkeneQlL7mK//7f/4JyOWJoqDrAQv2ffFkERihMgdqVysdK6ZC9WKQnkNLZ3igF5ZqzMBvAS2xObnLnWSiMW5xms2+8K66FcV93YqSOkJZqh73SmUZKRavd4orrb+DKa66l0VhxQ7xuk876CqVSGYTBYBCecrMIg+PwC4nnRxihChcsXYSLY0jKwCeIQneyYQd1j1QevnSuX6WhIbTuYXSKFRalPMKghFIhQngIIWmuLlOujTnzIylYu7jA2sVFWqtLnHziYXbt3cPOvftIk/QZC3X59bgHXhDyD/7BW/md3/kQrWaDUilCyIBPfeprnD59AYCLF9cxxrCyvMz99x/j9tuv4ezZBebnVwZdp9XVJo1Gy0GppfvAa2stOsVsIY5DOp0e1uY8+OATaN3j+77v1Xz2s/dQqZS+7caZf13CQ0qPsFRysju2cJyScvDH9qVFTebmNIXWrkWTWSdEra0ZpF1G64FfuOnfTyi0cLMRg4Oa5HlGN+nSTXp088TVtFbzsld9B8Lz6HQ6WJMT+pJmY9kpLiqDMRmBChxXRUmEybEmdwGDxsrCpsCYgsDlqNpe4BXyqdYN8owhUBJ8iYpD4vowWZYO0n7pKZQXglQYAbnOaLXWKdVHMUZjdJf5M8dYmj/DuXPHufHlr2HvVTdy9MhRh3KWL2BQqJQk6TZ58/e8kjgO+LP3fpQrD+3DU7Br1yyjozWOPX6Ma67Zx/z8Ci9/+RA/8iPfxTvf+Ye87nW38da3voKHHz6OHwQcOrSL1dUmJ0+cZHbLBKdOnGTnzhmklKwsX+QVr7yJhx56gt/5rb/gZXdch1IR+/Zt5e1vfxOjo856QQjxf3h4OKUYT4VOw6rwUOnLd0rZNxmVA5PTNEnJkWjh0MVZqp3sT57TyzIyrQmd8A9S2A0j1L4fe1F7WCw6S0mTHkEY0O22CKsVXnLHy+m02lhraa9fRNocpQyt1gpRHDm4hu/jZY6NqbO0kC+KsLgU0FiLME45XgqFkm5W0WusOxENBIHRKOPSQD8KCUslsrSLtTnKi/G8GKE8kAIZ+jRXF7E6oTo0Ttrr0Fld5MKpoxgyDt3yUmpjszz4lc/RWF92CjrP0Bl9DpN0Sa/T5jWvexlpr0uz2aZUiojLJUzu5hz/8T/9E0yekmc5P/lT30/a6xIEHtdcd5C05+Al/+EX/yEYXQg1aKamhvmFf/8PwGiSXoIX+Pybf/N2Wq0O5XLM+//nR9ixc4abbz5EEPgOh/N/eIBQ7PCeH2BM7shSA31/NonAFe60vk+vbcmL9CVLMzpWkGnnfZ6kOak2eAVD1ZoNkGofSi8KK2VdCMoJIUh7KaNjw/z0v/y3jE1MsrJ80Q1NhaCxsoDC2Z5pWSwvTyKUj1Q+OR0Ebr6WdDugIqz1sZ5xonQUp0EQ0uq696g8gWc8rKfAaqJynSCK6a5dLESp3b2l7zsag+ezOn+KanWEMKzQuHiMuWMPcuqJR7n6+uupT8xy4dQpGsvz7N6zG6nUJs3IFyDa4KAj7YIoVMPzPHqdnpPrKb7XL+K77XahyJ4VMGoKKEiHJEmLCXD/np0CgCbJMxdscRyRJDkf/8RXOXLkNFu3TV0+PTZDTXSGtdq1NYtfnyxydDfB77dwcSr0VmK0I9B2OgmtVo9OL6eXGLQGnQuy1HHLcyMGNYjtBwTSYdpzg7BuCLm+3uDlr3wVr33Nm+m0Wug8J+l0KUUlojgmTVK3JpKOkw7Cw5MBfuBOFJ1nhSolBUZKD/jxUjj1yCiMnDxRmpMnDglgC/BkXBlGSEXSaRc+IALlFfB+6SF0xvLZE4xObsVqWFs8y/zcccqliInpLSycO42Qgn2HrseakCxNB8ZPL1ibt19Ma60vcYd6MsaqXytshphc8hjL0z6v/1itDZ4n+f/+x884Hwxjv61C0X/N4sMhYrOeU3EXbhi34Y5VMEME1Gs1R1VIOpw7v1S4vobowmfdoul1m3Q7bTy/SpZlrtVrXIdLGxd+VrvTQxhNpnNy4+YOS8trNJorrDfWUJ6i1+tg8g5CBkjpUpYk6WF0jueFKOXhR7FLs6wT2pDS2bAZm+EcCBzXxvN9yuUKeeZowjIHG7vnCCupjExirSDPEqQXDKyxpRD4fkS3sUxjeZ6rbnstSa+NyDNMLmg126yvrjK1Y5Jeq8fJI4+weGH+WTdf76/dIiiwWN8cNOz/HleeGjKV4geFlGieI6UqXLTA9xTT46MEYUjSbhAGp6nVh9myJaGXZqw3WrQ6bZYWz3Ph3GmkCIljVeRZm3BYxYDPCEuOLcQfMvI85eWvfg1R7HxjmqvL6LSLNpmDsucZNkuxJiHPU8JKHbSHCkK8uIQx/Y6RdIW4J9EmR2mBKeqgOAjItaST5gSqkG9CYYSgNDzmajDpgt7zI5QKUNIniEo8ft8XkEoQVWosnT3G0rmznD87x/TsNqa37mF1aZ1O8yK1Wg1dKNu8YJ/0zeJwTzdMfLLa+wuR1Hy65z+X4Nh4b8/1tZ76/+fy3I3P+e0/Q4xxmlZZ6iD/DDS47GCD8TyfuFwljOts2b6XQ4euZGZ8lMiT2F4b01rkwM5prrr2JYxObqc+NoEKYpYWLjgZHNFPtSj0slwaJ5Wisb7GgQNX8Nrv/lt02m1KcYUwLJMkXbqNNdJOC08qPKVYXV6k215HAEooAi/EDyt4XoSQHlL6jv4rHO/dzWoMUvl4cYy1lm6qaaWGburEJlQQUxmZdPbOwhbGsoHjwSjX+VpfPs+B6++kubbMwplHWVtZJM16zGzZilAlhkYnmZjdhRXOUx3BCz9BPE8NhKTz3FzCQ/c8WaREqhCS0wPTzkvTKzHYlfoLrf/tvo/hZrDj5udbawdpm1MTFIN7KuWOZK3NQHDuyQu5P/nvs+3yfMOOoY+f6j9382v129ObLR8cz9wM9L2+LXW6MeQ6gdQQhN6mz+qGfEoJfD8gimsIJEFNok3C0sJ5lhfmIG9x50tu5LaXvYrZrTsoV+t0ul2++MkPcPdnPlJ0cwRYUYhagyysFsjdQv6u7/khkjSh0VihtbaEznvE5RpCG1d3YIkrAWHJo9VYZGJ2j0uD/JAwquB5joIrPAXpJuNVlJOU9RS2VOFMO2dWGHqZoZXkaGMo1WpUhseclrSSjlKsXGqpfI/lhTN4vmRsdi8XF8/SSzp02g16nTbV+jieH6FNTqeXIHzJ2MSkG1zaF6DuLqXk/PkVVlfbDA+XmZwcGrgzaW25eLHB0FCZCxdWiaKAsfEqeTFE6uveCuGKwzzXVCrRAALfV1h8/Ogc1VrM5ORwwehyxJ8sdWJiSnkDBfmR0SpJz03fW60eC/NreL6iWo0ZG69hiumwlAxeu692qLVhaanB+Hit8MfQtNuuwzY+MeTU0pXHykoTpSRB4BXvPRs4TLWabcYnagNlxv79v9WtXmtxfh9ZOnCU6u8Ezk4NPBUghOSBB+7id3/vjzl29Ahbpke54/Y3cO3Nt1MbHiEOIi4uzfOX//MPuf+uT4KVhbpiSkGfwljtsL5S0mmt8wM/9g85dMNNLC2eRRtNplPSThPl+UjfkjWaaJ2DCdFJj/b6ajH7cnMKPyqBUhgMnu9ROFE7WwbrwIoIQblaYSGzHL3YYcizlMMQz/c5s7LOPiw+FuXFKD9ASc+dUp7i/ImHsXlCr9ug226QJwmtZot9h65m6/7DCC8mTVrQyGk311lZWHPNJiHRzzdAhHRFd5blnD69xLmzy4SRU2i/6qodXLiwyuholWOPnwcBk5NDrK628Dw1oNY2Gh3yXDMxXictulHdbkoY+lxxxVYWFtdI0oxTp5aoViPSJCfLNUpJ4jig203R2tBqdpmeGUZrw9pqmygOKJcjjh27wOGrtnPm9BIL82tkuSYMfUZHq1y4sIpSklotZmmpQRB4PP74ea65difn51Y4d24ZsExNDXNxqcHOXc4g5+iRObbMjmKtZX2946zoyiGrKy0q1RjfV3Q7Kdt3jDM7O/Yt7bIZbRxYUIoCxm437KGBPEuxNiPXPT784ffym7/xP+i2Gtz+0tt45Xd8N9u27UIFIUqFHD/2EO/743dx4rHH8L2QLLcYmwxOI4txxpgI0k6XA1cc4k3f/7fpdFrOsUq7OqDTbhBEMUo6g6IsaZO2lmk3mqTBlJNstQalPIKgjJUSrXPCwCfvKgc5V04U28HoDeWK0+5dzj3WOj28KOVDXzvKmVbKd/7tn8Qa7YLDc1NzUfivL555nPGJSTqNVVqrTpl/rdFg99XXEg+NsH5xiVOP3cuFcyccU7GbPePp8fVTLOsm3JVKRL1eIk1zjh+fp1YtOcuzXsbc3EqB/A24eLFJp90jLoWMjlaZm1thfb3D9m1jtNpJwWYzlMuOw54kKUNDFebnV9myZYReL+PC/Cq9bsrIaBVrLa1Wr6D3TnHq1BKlUoBUknqtxP6DW9i3bxo/8Djy2BzlSsTp00vMbhnl1KlF59+dZmRpztLiOtu2j7O21mZ1pcXoSIXl5SbT08NcuLDK2nqbXBui0Gf7jgmWLzYLG2mPZtN9JmMszWaXUilkdKxKp5N+yz3TdZKisxSjBFVVw9hNRDSbgdasLFzgX/3cP+KrX/kse3fv4FU//INcec1tlKs1gjAky3Lu+tQH+PD//BPWV9aIwpIbKOZ6IHHr4ZQJlZZ4nke3u87VN99GKS7TXGugjS7SVUnW65J2u5SrFTw/cq0vD1aDCuuthG53fZAOe56HlZI0T7EqxFhLlvWIVYySynXJtCHyA7LMoDyPcmWEuVTTWm8yMTlDtVQm6awWXS2LkIYgKrM0d4zV5QW27TtIa22d7voavU6Xialp9l91C912k4UzR2msLlEfGqVeG2ZtabHg3b+AANHaUCoFbNs2Pui379gxQZ5rothn374ZrLXc9pKDNBodarXSYDbi+4rx8frAIs3znOSlMZZSKSTPXTt3y5YRdu6cKFI3y969M3TaCcsrTfbsmSLpZcXwRzEzM0Kz2aVajUmSjDRxk9g0ydm+fRzPU8zOjhLH4YCAn6bZoHZwQZkRhW6gdOWVWwlDn9nZ0eJUc2nVyEiFHTsmAGg2u9TrJRqNDocObXNqIIUXPECW6W9dPSIgT1OnRyy9QkvMtWWFzkl7PULlcXF1kQfv/hRvfeN38+a3/QiV+gytdgcvkKwtL/Hh//kn3PWJjzgLCz8kS3MHizfFn8Jkqn8wpUlGVB3mzld/N61WayA8l+cam+dIC71uQs9T2DwDbYiiiC985S6W17vcctstxOUREI7ZqQFhcjABnh/T6zSxJnCegjgx7SgIkELQ7XaJfJ8k1ViTs3fvdsLQp9d25jiyaOh4vs+pRx9ESQ9E6Gohm7O+tsrs7kNUR8Y59fgD5FnOzM79SOGxOn+WSq1W2M/ZF9rmFUXd4O7R18IyWlOrxYOCdnS0eol/iKPqhgNeuAuScKC5FQQKrS31emnwi/Y8RRh6xLHP+EQNrY0jSG1688PDFfLcDIKg34LwfQ+tXZ2j9UaxXS47260wdJ2ZIIgHyu7971kL5XI4+Cz94l1KMfhcIyPVwpMkZEPR/tLulpROQf6bhzh24gpg8bzA7b5pVkzANb1GAxsFlOKAf/L//Ay3vvy78fwqeWap1Tweuvfz/Pnvv4uzx08R+DFpnpBkqatbjOsgWSvQQG4tCjcdX1lZ5Af+ztvZuecAc3OnyfKUXKfoNMXoDD8ukyUWk+UIIalVKjz2xAm+cPfDVCol1leWqFTHsAUdOE86YAwmTV1HC480z9ECpIjI0fiBRxz5JEnCWrPNyMgwyZrTQ/CDECECZy6qFNKLSDptTh97mGptCJNb0m6XLOmQ5ZKt+w6zfHEBKyST2w+Q9RLyXptKtUa3uT5w13pBAeIsoEXhWisHqE8pletsWOg7kIlCs1UXwyvfV7TbCVHkOy1UIS75uhOOkwMznCTJyDKnxWWMHWj6OoTvhnVB4Ly2XD+9mMZ2u8nAaMf3N7rXnU5CEHibPMbNoHvmHKnEgCff66VO11U4hl2vlxFFwYDP3u+C9YPP1We6sPlyO22pHBVe5fabYTOF5wUopTA2J+n1nBKIdQNEYzM8FTG5dQ93vPZvYXKHoI7DnE986P382bt/k/Z6m1K5Qi/pUSDcB6eTy8WlI0ihnI5vnvKyl7+UH/qxH2dtfWWACrYapPSJ4wppGJGqdZQwaJ3jhWN8+suPsdZs08tTLswvsHXHFSR5irG5U5wvGF5SOfCqzjIs1gm5WU0URoSh73gtiWZ9vYVAMDIyuikdctCUKAiZP32EdmOV2e3b3LAzz0i6LUYnJ6kNVWm1m4xP78KXIUnQopV1WV2cZ/ni4gtTd3c8Z9fFajW7jI7VaDQ6NJtdp0frKWq1eHA6ZFk+UBmsVCKq1Zjjx+dZX+9gtGHnrklWVlr4viJNnUKfs2qTVCsRi0sNdu+e4u67H2fPHkeaStOcSsVBT+r1EnnudueVlRbWWoaHy4N07sSJBeI4oFwOSZOcKApYb3RYXWly08376HRSB3TznV/fqWPnnaRMo8Pk5BCnTi0Rhh67d0+xtLhOGPk88shZtm8bp1QO6XRSlpbWufbaXTz88CmGhspkWc6WmVEQ8OijZ/F9RbVaYmSkMvjZfDNYhQaLQmIyp2ZCMdQLopByvUYUl8lSSxSWSbsLvOs3fplPffgjhH6AF0XOLMYWk3fLAJZunM0tUnikvQ71esQb3vh67viO1zM8uYXG2hq+H2ERJL0eedqj11xhdeEMaXcdz/eI4jLtDB49epwwDun2Opw5e56bbsnpJW0CcpTfP60zJAo/8uk0Oggl0aTYPEUV9Yoo7BeyPGNl+SLCCmRhjCOUE9r2PcmZxx8kDAPiUo006ZHnCbnRbNmzG+mHVGohUVQi73XpdhpcOHOC5voqYegm8S8gxXJpyulTixgLZ88ts7bWplaN2bJlhLW1NqdPLaKUZGSkglQSazssLqwzNT3Mvv1beOjB09TqJYbqJe699wSrKy38wGN6epi1tTZR6FOtxTz4wCnGxp2EaKkUcurU4qBmWF1p0Wx2ue0lByiXI770xSNUqjGeJzl1apE4Dti/fwutVo+jR+eYnByi2ezSbHTZvmPcoVeNZW5umSzLmZkZIdeWe+89ge8pdu+Z4qtfPUa5HOF5JVqtHl/80hFqtRKjoxVWVlscOTJHL0kZGam60wSYm1suTj6PLMvpdlIurLcZG6vR6fS46qodJMmLLDsqHFgpy1KCoOT0p9IemTYoYYmiGOn7IAVRWOP8mXt513/5RR74q4eo1qoYkwE5kqDfoyK3Bk8IN7DDiUanaYdypczf+5G/w479+xiZ2sHcqaN02utOOEM7Zfgs79FtLmOybqFzC2NDJb720MNcmF9kaHiIdrvNufPnyfKOw3MFMcaawhxUorXrRkksSucYNBKD7znh7UoUOwmmTBD4JaKo5B7ruTmW9AO67QZnn3iU2tCQ89DRHQwpuTaMb9mJF5QLO7YujZULNFYXCMKA+tg4SavxwrR5+12sMPSJSyFjY1Ua6x2qtRJSCMbG6yRJRhB4lDbVCZOTQ/i+RxT5HDq8jVIppFYrsbzcRGvN+fOrDA2V2L17ymn2xgGLi+uFaaJk374ZlJIsLzcJQ48DB7bQ62WMjFTdAt8ywq7iNCqXQ1ZX21QrEfv3b2HLlhFKcUij2SlaxBlh6CGlYO/e6UEd1ekkXHPNzkF3bnp6mNXVNmNjVSqVmDvuuBJPScLCfm1kpFJQjF2jYcfOCTodJ1M0OTk0sJ/bf2CGZqPL+ET9ksHlizkEieIIz/ddSiWd2Y1OcyjULtGQtFt89qPv4r3v/i0aqz2Gh4cxxm0UyissvK0o6LUGY+UgLU6zFOUL3v72H2G4HlGfGGdobIL1lRUqfkC3vU7SadNtrpB03cwjKJURJkdiCcKID33sc2QFQxQBp86cJcsyx3K0gaPXSok1Aqu181SXFLAPz/FVjCE3ltwYxmtVeqmm0wmI48iR76WDvoRhxLkjj9JeX2Fsz16QjpVqdcLiwgpBVCYIItrNZdqNVTqtJkGpWuDW8qIGsc84TX9W+4Msyzl4xVaiyC8sDuqXFKhSFobtZiOR7Rfdea7ZvXt6MFTbtm0MIQTT0yOE4aX+4i95yQHSNMcrZhYAtVppACXZGMhZrrjCdZ6GhpwG19SUs10YHi4zOlrBGMv4RH3wvD4vwr1cgfOJAw4c2DKwVCuVQiYnhwb+hzMzI5dYv/Vfq48WCAKfer2MlIIsc52XgwdnMca9n74d2zcDqJbnmrSbEJRDrOlL8BhybWk211i9uMTy4hxnThxz0PggoJu2iPwQYZ1nepanIJ3SicVJAGW5RltFt9PmDd/1GrZuGeHYE0c5dNuryHuuc5b0upgsRYoc34f2yjpZbvDDEOUFxHHIZ79ylC987VHiOKLbc6J7q+vrBQclReYBvvIGJjcUNRRCkmc9J8RtNEmakfScJnAljqlVqzTbTZTnfNqtASt8hLCcP3mEMI7xSzGp0RgBCxcWaCaSKC4NmgFRuYbW0G01nbpkmpL0OpuO5xdQpEeRP4Bj9DtSfbpsmmYbSoPFAuxLAPVbrBv/zgfQlb6PSF81uFQKKZejQrq/32LOLnkMbKisbzzfdW+c6uLmilM/JdjdZi4Gnaok2XhveW4GVgVC8KT3t/m9bPimbP6cfXj/88GRvVAgZ55mpL0eulTG5BaT547DYQyrF5fptJuk7QblcgVtLOutFllmCJQ7bSQeqXbdptQYtHWBkueWPE+p1iocvvYwi8trXHntK1AolhdP02k1MNapMiadDr3GEkvnT5N0O5SrQ8SlCrXyFv7iwx9DFP7ruXbNilazh9YuOK3OgNAhfvMMYRQGgfJDuusrhJWqq49wDZX1RpdzcoUZBEEQOkE6k0MBVOyurzB/9jiVWsWxCY0l77URIuBv/fDfotdpkapeAWaEMPbJU0n7YpvO6gpmQON+AW1eIQTtdkKSZNRqMWtrHSqVmDRNmZ9fY/v2iUF3bGNNiKddKJf4T4tLbRB0obQhxNPf51JhiKdfgJsD4LlqWT3Tgn7q/cXXfa1v2SykAJaZAoLuPBo9tM7pdbsDCRspJKkudJGtRufO5FMbQS/N8b2QNMuxQJY5pUWjE0ZGHRBQyYgdew7S7XXothuEpQoqKCGkR54kLKMZns7Jmsu01y4SlEM+/8W7eeSxJyiV4g0IPqKg45qiw5k6Oq5USOGovtaAH0ZO4DrPkNLNxFwKJllrtOnlGTZ1hDvXcpMEQcDpo8dora8ytXUWhcQTsL66yvTWHYxObSHX4AU+IP//9s40yNKrvO+/s7zLXfv2Mj3TM1pGEhotCCSEMGIzMTZ2AIOd2IY4sStxFidVoZJUkiqq8iGp5IshcVwpVz5QFEUqRIljO6IMmFUgi1VCMiABQhrNaLaenu6eXu/6bmfJh/N2zwhJAxLbCPUzdavm9vTt7rn9Pu8553me/++PKQSyKknbXZLOFP1ljzX+kiQpfUnj+khx9OhZsqxiNMrQKpR2G42YqrJcffW+H4lBzN5U+3OY5q3BccI5XCBJh96FrfCuJh4KifUO4QXaidCdJoChnXNUVYmWKsCpnQ+ruwijzfsPzGMLg2zERK02/fGAfQtHEDJGCE9ejhlurqJkRNqcxZWWQ9fM8o3vHOODd30SK6LA9HXBOdHjyfMJAoPSnkle4UVGrGJUFOB0ZVkSa0XSaGEKg46hKgOiVNSH9aI0mFHFYFgRqQZSjvG24sRjj6B1jNShHC+dZ7jVR+gOW+eXidM23jWDQan3CBFjqhKlNWmny3Z/WCfz89hiORtQPVorzi1tEMUapSRpGuGcZ319yPx8lz09009SC1KC9BhrgvVzPbNvrQkWFtS+5pXBOVC1V6EXHhUpKmtqH/FwMHW2wvuKRpKwmRUcOHCIdmeKcWGoSktvar4+2Fuct1RVSXf6IG5qP95ZtteWkXablY2HyCYlSaTJyzKIu3xITo/EqwQlNEyGmCrYMFBbf0up8ALiRov+cBUl0rrP4FARNOKISGv6hSHLJgFGEUWMNtdYP3eKtJGGnYhz5JMRJ06cZGpYcfjm24gb0+Al+WhAkjbxtkJ5iykNeVHS6XZ2+17Pw6PQc/DgNAALC73dJtnO7M9z0WLsxY/K5daSxGlNTLRYd0G/sTvU62xQsTpfm3oKhPQgPNrHNKNG6JabQF3spBFOKsaFYXZ+nul9c2wcPUo2GtLpTeOdCRPWuaGVdndVgNlkgtSaspK8812/xdmVIZ++517SRgPrLFpJsnHG1HSPdneK8bCPkqHJOc7H6HQKGQUusPOeqNGmKE6jRfh/ulriG+uINE3JGzlZNgow66TB49+8j/FwHa33UYyHVFmfxcUlZq88wht/9V1ced0NTEYZpsxJmtP011ewVXAYu/7lt7O1coKlk0/WfZDnqQfZqcZYa3YrWzuH2b34SYtBQik8iqKa0+vrrVPtaqvCL9q68FwKW/slBhtna8PrkyRmlGcYV5IkMbEWDIrQB2m2Okx1OjiXk2cDpvfNYXc81oVECgLd3YHQEa3eLDpNiaXjn/zeb/PE0Sd4cvEcaSOpiyGWaw5fRzNtMhn0w5iM0uTGM54UtFoNnHQ4I0jSLlGaUJkJhTGYKpRzsyKjqgomg4qzZxbDaLwpWF1ewqkmqjXL9BXXoXXM4dvewv4rDqPSlO2NTeI4Zri1RqPVRicJp5/4JlO9GYwtg/34ji5e/JCS24utA/bipyhKr6mJQkuEFOyMo+1YTrgd+okUuzbPtkYEGWeRImg8jLGkkaIZK/rjHGMFSkBcD2IKJRgOt7hSKfr9IUpGKKHD3JKUaKHRcYpSPbLJmHOnnyDWmn/++/+Qd7/n31NWJY1Wm8p4Xnn7K4K/oAiExDCXJ8iLCUJ4oihGSIWKW7Sm5hmsHGU0yciHgZl2zXWHueXmm9k3N8Mdr7qdvMgZD0e8/A3v4OVveAdCSZJGm/FwQBIljMcDyu11TFGQJhFFPubs8W9zxbVHSNOEk9/9OqPhNVTOB1qjEM9/BdmLyytkTZ4UO/Xw2rDcWYOtLELUW2BC78dUJiSOh6KsSLQmLyvwlnaSMMxz8tLgvcRUGUp6ojSmN73A2ZPHOHjoahqNDs5YdI3VEUBRlkyyAVWeYx10Zg+gpOA1h67lD/9Lyv/48F184xsPMzWVcuerf47+cBSsDVWEqXKEhEQpbFbiSkfcTPFS0p1bYPPMo5jhiFuvP8zrXn07f/vX3sz8/gO056+m0euydn4VV1WU+SRo2aVkvL2FtZa1/jreWdJGh8l4yMr2BtPz+xgNNjn56DdotttkozEbS4vM7D/IoIrIS0NXir0E+dlYRMSuFZuvR/ol1J1qFwZIRcAoUSeIkjpYNltLVfd1GommrBxlYeq5txxhPXGcIOKITrvLyuoyX77vk/zCr/wWvd40RZVR5Bmj0TAcxIUkjVrh+9kAjvA43v6Ot/OWt72V//y+P+Tb336UI0euY2VlOeg9rA2eMVoiYoVXQZBVFTmZNWhTEtPgyGyP9/yt1warh+0z3Hf/x4kacxx86eu54bZXMCkKpPBsb54nG4+IkpgkjtFaMtzeYmtlmWZ3ismoj7c5nd40i0cfDUOxpcVsbtKZmuWJxXVGk4wDUu4lyM9CBOaVw9k6WTyMhgOK8SQ0Ek0ZEsVrnKvw1qKSOHTOfaAqTjdiJqVhlBVILxHWgC2D4VQU0Wz38JhAhh9P+Kt7PsHr3/QWNJp+vw/K0262UCpCq/gp+3hrbUhOIfi3//pfsrG2Rn/9PMVoQNJo4n1otCoHYthn0h9g8gJcRTEckPe3GW+skW1uMBiPWFldY+qa6zh07RGaacyn//LP+NwnP8M/+1fvJvMe7S1mtEkx8PRNQKvOHjhIIcesnz1Bo9tm49xpknYbpGRtZZXKCpqNiKVzKzx2eimYOj1fPcjFxIwX3XZGysuPPbprBW1QQuG8o7+5RpUX6CRoYmxlUEpRmRznPRKJKQ1YS5omeCEZZkWwhPYOV+VoL0iUQqFQStNoxEQSWp0pEI6P/cXdXHfNDdz2ilux3qKlqrd7rhZPVVDT5QMCNTQFFxauYDgZIeQ22XAzvGZ9leFwm8nWBuPtbZwQFHkFSIbDLbbXzhPLCCtBxRErx08yc6jDdj+nFVvu/vO7qbbX+c1/8HfZOn+arL9Bno3RUYK1jhNr5+jN78d6y/LJE1SmpNzcRHpPVTmy3KAlrG6dZZDnSKmeP9UkbcS7jrA/iqbgC4nzWRXlZQetszacLZSsRU71H2Mt0muMMSDDfFVRljVBRFCWBWkcBi7XRxMqGwiMWZFTFTlKSwwWb4LRZdpq0Ww2qZylFQtmmoKH7v8SWT7mNa//ecoiQ1jLpMjwCCIdEadxSBAfZsbSTpfx1gbnn/gO/fNnWLjyarKVFY5++a+YXligzEcgJNv9MUWWY40jLzJGkwmtRotYRcHEaeks33pklWg6pb85Zn7fFN0D81RlzvLJxyirkiyvaDYau+ifxeN9OrPzjPOCrc1NvIBIKJyFwlqqwZiZBF5x5b6nWXs8B2iD5ImjZ+j3RyilXjQryc4g5pEjV+0Kqy6fQzrkxZBOuxcgbs6gIo1UAmdNYPbiMKbAOwFakpsCIT1NHQ7lZWWpjKMocmyRB2i00igdBv0iHaPjFkKkrC6f4vjiMllpieM2f/K//w+nFpd4x9vfRn9rnaQRdBZJnAY8lA9OI82Gpn/6KCcfvJ8TD3+T6cPXEi1cwzcfepCF629iuLXJ+vkNtgYDyqwkSVOysqDKS5RWbG1tg5JsDAaMK8uxtQwrUl5+MOUf/5t388Zf+Zvc95lP88jjp9A6oqoszWaTNI5oJhrjLev9MY0kQdS4qkp4jIeqLGmnCuslt79kgfauOvU5JIhzQVf83vd+mE9/+n6mptpPYVf9zB6CBVjrSdOIT3zij7j66oXLB5wtoKyK2p8QSpPhnCVJG5R5TlWWARVqLCa00UPvxDtaccwwyxhlYRaqMiVlVeCFQ0lNqiK8DrbQUmmiuMEwr7jnK9/k0ROLAS/kDJVxfOGBB6mqine8/a0IGeBtOwA7ax2Ndpulxx7ha//rAyw+foLewau444ab+MyffpjrbnkFN7zsFu767/+Nx08vcnBhllYS0x/2ycuKmV4P6zxnt7ZY2h6wuJlTeMn5fkmrWXHLbS9hu5L8h//4X7n33nuJI0Ez1qSJJk1imo0G3WbK7FSH0lSk0YRmFFGVFVk+xjjPTEPTbWqssTQSQRzJZ70J/gCSW02SxCRJ9JQEEeLCpO3FILgdR6mn//vFw4oXw+PE07Zvz/56/z0zexc+5v3FkLiLv6a/iF371I9/779fnCBxHF1mPZ8w5FlUBUpHWOeoqoDN1FFSl3ELnLHBzBOJ1OCdoR1LSmMY5AXGunpLkpNXAWgRCUcsBU6BliCUJkkiHnvyBI+dPEPlYDQcBVibVKAEf/C+93Fg3xyvef2dlEWJVx5hFXGasrl0jo998P3M9hr0bn4Zd7z2Ndz/mY8wGE04dNVVfOrP7mJz0Of1r7mTxdMn2BwM0UoxP9Wj8nBidZXFrQGPr0wYl5r2VIvZQ3M0Wy3ue+Q0n3rg/RgTJLrlVo50FgUkkaDbSUhTzYGZWZqxohFBt5lgS4PF0WnEpI0EgSASAtylp0H0c0GPXjxNW5ZmlzZ4MUAtaML1Lu1Q6wv0w+BZruq/yyD6qT3TL87gcDi+AGe7oP2W9YUSvMvLstp9baA/Bm/2i0fzd36+HY3KDiVyR58u5YUx+u+HQ/2pLx8eYp2gpMaYAPYODcEK52yY4CUIl6QLo4KxUjg8wywDG0bQy6qkqkqUEMRSE2lFHMdEUhArhZISLQTZZMJoXFBYQ14Gs5pIKpIkZpLn3HXX/+S6w/vozB5CNTX4irTR45Of+AvmGpojL7ud7vQ8D37245w+uco7/t7v8vCX7+H4ydO89hffjB32+frmJp12C601Y2s4trzOIM84vVnQH3vavTa9uf00Ox2sczihUVGOKQvGWYaOgwGpdY6RMYw2CvAFZ5ZHHF7oce3CFOtbA1KtaDUblHmB8k2UEpgqcI2ddXX5/BkSZMdb8Ll01I2xLCzMEUWafn+EMYY4jpFS0O22WFo6T6fTZt++aZaX1zHGMjMTiIbnz2/S6bTI85Jut1s7S2WkaRIOmMBwOEFrzexslywr6PfHHD48y/b2KFgp5CVZlnPllfvJ8xKA0WhCo5FQFBWHDvXIspw0TRj0R7UfH+zfP0O/P2Jqqk2eF7RbDUbjjNXVzRfEhICntkrzHmuqcGMQmqLIED6ANGR9eHfOoUUAPg8nOcYGdGxRVBRFhZIeLXQ9Iq5CRUyYWotxoVxbFCWFNRRVSRypMDZeBffZz33xAX7uYx/lXb/zexRlSqudMhqs8YmP/TnX75vn5lenfOXjd7OydI5f//v/iJPfeYivffVB7njDL1KNRjz4tftZWDjIgZlpHn7sMVZHOZuTgrPbBSt9Q2d2jvmDVxBrhZaS/mDAJMsp8wmmKqnKIjhTiUBjDOXaIKay1nD8zBZ4yWtvvYIqmxALEFKztLLOtVcs1D6ZZtdo9FkSxD2rN8KlKinNZkq73eD2229geXmd66+/ku9+9xQHDsxw6tQyUaSZnZ1iZqZLr9chTWOOHTvD+fNbvOQlV3D69Ap33HEjzWbKeJyzdn6L6ZkOWmsmk5w0jVld3aTZbHDzTdewurrJwk1zXHnlftbXt7nnnge5+eZrGI0yDh9e4PjxRfbvn2V7e8j0dIfl5XWmp7sMBmOmpzs451he3qDXa9NopJw+vcyhK+bJsoJz59aJIv2CsFnwtWDNOkNVFQGwMDG1aadD1jpzKT1aCYZZQVEFzUdWGrIix9kKrWJUvWLEWgcumbIYb/EiKEXLIqOyYSoYKzDC4ahINCACLPCjH/8sr7ztNq6/9Q6SdIaHvvAljh8/TkMpssEGZ548zht/7TdZfvI7fP5T93DnL7yZmY7mvs/fy2BseO2dN/HEiWOc2xhwdlBRCsVWBkmzRaMzzWSck0xNkU0qsqygyIrAV7MmbI+cQMiA7fFWBt9qPEJqhILjZ9bweH7j52+knIxpNVKWz29x7MwKvU5Ku9ND6UtBG55H9VZrxfnzm5Rlh7IMS/1f//Vj9QohahrhhFOnlpFCsLS0xtxcj6IIHhTOBZnriRNLdLttxqMJCMHm8T5JesH4M6xOltFoQrfbYnl5g7Nnz9PrdQA4d24d7z1f/eq3mJnp8sQTp9Fac/r0MsvLG9x660sYDCYsLa2hlGRqqs36ep+yXGd7e8ipU8thD/4CSQ6BCNUq7ynLAiFUjRgyu7NYwffckESCcWbIy+DrkVWGvChwNmxLlRBESpFGEWmSEMdxuIt6W18OklgntTpQgpcBe6ocha3AgZaScZ7zgQ9+mP/03psQXrD0xHeINNx05EZOfPtRvGiyee4MX/vSfbzqjW9iZqrFvZ/7LF94bJV/+nd+g8GwzyNPHGdpXLHYL9FS0u51GFvJJJ+wb24O78KwZFBylvg6Odhx8DUOIQkyXh+QrCFRQDcSnjy1zhd7i7z1VdcxHox4yVUH2R6OGE1GdFqNembtRzSLteNGO5nkjMfZU+AEQgTInJTBD291dWOX6r64uIqqCYkPP3xsF7LGRcY7O893xui1DlyntbXt+qxRI/ndEnEc8eijJ3Yv7BMnzu0esgP5XfH1rz/+lMP7xWedwP5Nfmj7hp988zKIowQKrSTeX7jpIAUK0EIwLA3josIYQ2kqiqqgqMZoKYiEQkqItSaJ46DzifUupTC8kREqSsJ4Or7mDwicsyBDN9zj0HGHo08+yZ/e/VHe855bGPQ3ueqKBaZbHR764ld45WtfxfLZJ4nas0zPTHPPZz/FvY+c4o1/401MNT3/9y+/zLeXR4wKy40HmqyOPSsTg9Ca6dkuQgqyvKCoqgCoMCaoJj21T6NHKIE3oZfhlQYvwZtaYBahGgkPfOsMV+2f4aaFNnllmJuboeemgmzgEscM/YN0k5WSz+IyK3ZZWE/10vDPIL/lootT1Ywq/ZTEe/ph+ekWBhd/vlLqGfs7Oz+D1uppFa6ntaWf4efcQR5dhgaFGGPJs4wkaeCd3aWiO+cQSiCFp/KQlRZfu0LlZcW4ttCLhEZJSaQ1WilULInTiHYrwVlVM7Y8SntanRQV6xrOHZjZ3spwE8JjvCerKg7OTfP+D3yIW2+7nWZ3iubUFFPTPQ5cvUBnKuHBr6/wylfdyfKZx3nouye47trrecMtV/Phj9zNsbUBUayZE6DTDllZYrOM3vQMaZwynIQqlXMWrMG5svZVD3Nn3lqE1iBrqzj8BSaBAO+qGnDo+cLDJ7nxqjsQrqQwVahkRelFVc3nkSDjccb29gjwNRjhZ328BIwJfZDLb2XxZNkEIcKdsygyymoSRFNAimNsdrw0oHSGwljG43EgHiodqjVCoFVwktVJRNoIq4i19ZbF+9orMIzNS8K2uTBVzc4NKBIhJJWxGOepSsOffOgD3HrkIK12l5PnT3Lr617Btx74JkUhmJ5q8JEvPErcmeP3f/ttfPWrX+TRc9sUVvGGG+ew1nHfmQGZFSTtFu12iyLPKMsCLUAJiamKC+V5L+u7XhWGNqXCu6o+tFNLiAUQkEwyVqyubnP07CYvv2YG4xymLJFSX1Lb9H0UhY5Xv/qlJElEs5n+xL0wflqNwh3saZo+e4f1pxVKKYwB53P6wy2iSKOEBF9S5o5JWWGspTIFZRmwOdZUaKXQQiC1JNZR6G+lURhhF6GS1UhlMMsR4ZAbxxGRkhgpqEqDtx4lQ7ccgjGosY5JYZjqNChHWyydcVx77QFm5nu0Z6ZJ4gYvveUI9913P2tj+N13vp2vP/AlvvqNx7lqX5ciK5lMPEMdkVWOOInptDs45xmPxsRJgsWhFJgiAxG22jhCIzRMSEIkCI0fe5Gho981URMuZMHDR5e46aperYqEyplLn7cvWc4tS979L95Zf9qLb2CxKvIfDwDueQ8qhhJmkedIJWtfcYkzBcIYBnlFXlmMMYH2mBfk+RgpCRUrEc4tsVbByjuOkUqT6IhOq0EUBcWgd8GIJ5IabxymCgkRKUllgs95MAJ1u6afUsGwKCicw1hLHCVMjOWlb3o9/eU+Gy7mD/7du/jS3f+Pz3/tUTZyxy2H9nOg2+RLjy9zdDhC60B7T5Mmo+Gg/h4eJQTOVJjKINMkHC92nISECha9UiCUxFtfn0EC+zckSE1yjBSnV7YYjB3t2ONql98fqlGYTwq8z7kEIf5nbgXZObNcdtO8EBpbzqCjhEaaYPIJvioZF+Hh6gs6KyzjSRYO7VIHj8Gau5umMa1WTKJjkjii203odBtIqVEqwrrAN5NSIVz9PlgHTtS1tNC0dLDbY+oPS06zEaaJjQXZgMYc+w7NMtfbz+/88i/x+OPH+NAnv8jrbjzC9qDPY6dWOHj7TWQqwmKIlKLZ7mJKQ5mXtDuBppk2Isb9rAZUiN37hagTxOOg3mYJoS7aGstds6FgT6fIJxWrWxnTB9pk1aQmr1wiQXZ0zZeqmry4pngv9wQOF6gUkjLLsFlGYRxZUWGMozIVpSkZTUYYU5FEqrY0EFgpaUYRaZrQiFMireh2UzrtlGajgRcClMR5F8RVtQYeQY22ritGTuxeWM55BALnBJvDAu/7RHHCwqRgWBo6hafZihlNMv7ojz/IkysbpFpzw3wT7y2f/9ZxtnwaIORxSpJoBlvbCK0w9RhQrBO28ixMavqdR4n3wV0KuWvNW8O8d1ZcD1T1cwGEpef44io3LnSwlUNo/322WHvX/gssQRRSRwhvwRR4qcmqDEsw3UQIysrjrKWVxmEVqMvvnTSl3WrSbbdJEkWzkdDrdml3mkRpE++DT6OUO17q4aSudYT2ocQbRnREqCR5wlZPKSKtKUpPXlnGRUllwqhQZio6Scxjjx/jO98+StKI+e76NgPn2D+7jzOrm7ikQRKlTPd6oTLnHI1mC+c9aZoE2w1riZM0dM2lwqNAhQTxBLdfoWRYUYS/qJBa9zh88FwU2rG8McQgEfXrfyj06F5cXvu/rBgx3FpHu5KsLBlmJWVRUZQlRVWR5QX9rT7SgZE7A6eQJglEikSUeDPAmDTMdSmPxaEl6CjG4bHe4lxFNh6yvrFGXrpw832WWCzHTILPKoMSjhXLzM9N05mbRUQtut0ZHrj/a1TG7H6dxXNrLCoJsYbhBkQNtpRgsrUJXjDOcrCGVq/H5sZ5ykn2TKfEpz4tzA/0Np5Z2uDoiUX2tyPyPAtVMPagDS/4rZWtKu58w5u4+qrDaCkojKGqQi/E2iCnzcsSU2TEUuNEGMFTUhDFEXGc0Ew1UkEUpzQbKTrSyCgiilOkhO70PpK4w/Ss4pd++VfpzV9LaV0Yn8eFrrO/YPMpELRSTZZV2HpLlESSKxfm2b9/P+3uNFNTU8hfTzh8zUuRSQQiFBhQEoHE15ZtgcKYE+molhc7Wq0W5WTMeDhERiqsEN6GVkeNO8Kaiw7I4nsWhB0bMLFDycZbzw1Xz7N/qoH1kDZbu6vj0973Ih95KRWmKn6M1mF78aNScsVpA0R0yW3BczCUvvCoLzBn7S4DTcfJD3kPteFhHah4t+R6uWmYq2L0tJ5XsOPQeyvIC22LlWeTp5QT/TP90v2zsbcFz8gGf8rHxa5tRD6pnncfSNRf5wL9P/s+fTSxe1Z4xrLij6XYURei1A+hSd8LXqQgiQtzdT+y4oJ8Ab7fe5fcXuzFXoLsxV7sJche7MVeguzFXuwlyF7sxWXDIdvrfezFXjx71fBFREzci714nlusvVVkL/aCZ5Bu692uYg1FEHvryV7sBR5BmiQIU+X+Au/KBDnjXuzFizs7iOKU82sr/H8NSLFa/4jpfQAAAABJRU5ErkJggg==" style="height:48px; width:auto;" alt="3rd I ProcessFX"/>
    <div style="text-align:center; font-size:12px; color:#5A7A8A;">
      GLOBAL FOOD CHAIN WAR ROOM &nbsp;·&nbsp; ISM World 2026<br>
      Gwen Mitchell &amp; John Atasie &nbsp;·&nbsp; Powered by Claude AI (Anthropic)
    </div>
    <img src="data:image/jpeg;base64,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" style="height:48px; width:auto;" alt="J5 Global Synergy Group"/>
</div>
""", unsafe_allow_html=True)
