import streamlit as st
import pandas as pd
import joblib
import time

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Ledger — Loan Risk Assessment",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# LOAD MODEL
# =========================================================
MODEL_PATH = "best_model.pkl"

@st.cache_resource
def load_model():
    try:
        return joblib.load(MODEL_PATH)
    except FileNotFoundError:
        return None

model = load_model()

# =========================================================
# DESIGN SYSTEM — "Ledger" (vault-dial aesthetic)
#   bg:        #0B0E11  near-black charcoal
#   surface:   #14181D  card surface
#   border:    #232830  hairline
#   text:      #E8EAED  primary
#   muted:     #7C8592  secondary
#   gold:      #E8B04B  accent / headers
#   safe:      #3DDC97  mint green
#   risk:      #FF5C5C  coral red
#   display font: 'Space Grotesk' | mono: 'IBM Plex Mono' | body: 'Inter'
# =========================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

<style>
:root{
  --bg:#0B0E11; --surface:#14181D; --surface2:#181D23; --border:#232830;
  --text:#E8EAED; --muted:#7C8592; --gold:#E8B04B; --safe:#3DDC97; --risk:#FF5C5C;
}

/* app shell */
.stApp{
  background:
    radial-gradient(1200px 600px at 15% -10%, rgba(232,176,74,0.06), transparent 60%),
    radial-gradient(1000px 500px at 100% 10%, rgba(61,220,151,0.04), transparent 55%),
    var(--bg);
  color: var(--text);
  font-family: 'Inter', sans-serif;
}
header[data-testid="stHeader"]{ background: transparent; }
.block-container{ padding-top: 2.2rem; max-width: 1180px; }
#MainMenu, footer {visibility: hidden;}

/* ---- Hero ---- */
.eyebrow{
  font-family:'IBM Plex Mono', monospace; font-size:0.72rem; letter-spacing:0.22em;
  text-transform:uppercase; color: var(--gold); margin-bottom:0.6rem;
  display:flex; align-items:center; gap:0.5rem;
}
.eyebrow::before{ content:""; width:6px; height:6px; border-radius:50%; background: var(--gold);
  box-shadow: 0 0 8px var(--gold); }
h1.title{
  font-family:'Space Grotesk', sans-serif; font-weight:700; font-size:2.6rem;
  line-height:1.08; margin:0 0 0.4rem 0; letter-spacing:-0.01em;
}
p.subtitle{ color: var(--muted); font-size:1rem; max-width:560px; margin-bottom:2.2rem; }

/* ---- Ledger card ---- */
.ledger-card{
  background: linear-gradient(180deg, var(--surface), var(--surface2));
  border:1px solid var(--border); border-radius:14px; padding:1.6rem 1.8rem;
  box-shadow: 0 1px 0 rgba(255,255,255,0.02) inset, 0 20px 40px -20px rgba(0,0,0,0.6);
}
.ledger-heading{
  font-family:'IBM Plex Mono', monospace; font-size:0.75rem; letter-spacing:0.14em;
  text-transform:uppercase; color: var(--muted); margin-bottom:1.1rem;
  border-bottom:1px solid var(--border); padding-bottom:0.7rem;
}

/* inputs */
div[data-baseweb="input"] input, div[data-baseweb="select"] > div, .stNumberInput input{
  background: #0F1216 !important; border:1px solid var(--border) !important;
  color: var(--text) !important; border-radius:8px !important;
  font-family:'IBM Plex Mono', monospace !important;
}
.stSlider [data-baseweb="slider"] { padding-top: 0.4rem; }
label, .stSlider label, .stSelectbox label, .stNumberInput label{
  color: var(--muted) !important; font-size:0.82rem !important; font-weight:500 !important;
  text-transform:uppercase; letter-spacing:0.04em;
}
.stSlider div[role="slider"]{ background-color: var(--gold) !important; border-color: var(--gold) !important; }
.stSlider div[data-testid="stTickBarMin"], .stSlider div[data-testid="stTickBarMax"]{ color: var(--muted); }

/* button */
.stButton>button{
  background: linear-gradient(180deg, #F0C264, var(--gold));
  color:#14181D; border:none; border-radius:9px; font-weight:600;
  font-family:'Space Grotesk', sans-serif; padding:0.7rem 1.2rem; width:100%;
  letter-spacing:0.02em; transition: transform .15s ease, box-shadow .15s ease;
  box-shadow: 0 8px 20px -8px rgba(232,176,74,0.55);
}
.stButton>button:hover{ transform: translateY(-1px); box-shadow: 0 10px 26px -8px rgba(232,176,74,0.7); }
.stButton>button:active{ transform: translateY(0px); }

/* divider dots between sections */
.section-gap{ height: 1.6rem; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# HERO
# =========================================================
st.markdown('<div class="eyebrow">Ledger · Credit Risk Terminal</div>', unsafe_allow_html=True)
st.markdown('<h1 class="title">Will this loan be repaid?</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Enter an applicant\'s profile below. The model reads their financial signal and returns a live default-risk reading — not a yes/no verdict, a dial you can reason with.</p>', unsafe_allow_html=True)

# =========================================================
# LAYOUT — form (left) | dial (right)
# =========================================================
left, right = st.columns([1.15, 1], gap="large")

with left:
    st.markdown('<div class="ledger-card">', unsafe_allow_html=True)
    st.markdown('<div class="ledger-heading">01 — Applicant Profile</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age", 18, 100, 35)
        income = st.number_input("Annual income ($)", 0, 1_000_000, 55000, step=1000)
        loan_amount = st.number_input("Loan amount ($)", 0, 1_000_000, 15000, step=500)
        credit_score = st.slider("Credit score", 300, 850, 650)
        months_employed = st.number_input("Months employed", 0, 600, 36)
    with c2:
        num_credit_lines = st.number_input("Number of credit lines", 0, 50, 4)
        interest_rate = st.slider("Interest rate (%)", 0.0, 40.0, 12.5, step=0.1)
        loan_term = st.selectbox("Loan term (months)", [12, 24, 36, 48, 60, 72], index=2)
        dti_ratio = st.slider("Debt-to-income ratio", 0.0, 1.0, 0.35, step=0.01)

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    st.markdown('<div class="ledger-heading">02 — Background</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        education = st.selectbox("Education", ["High School", "Bachelor's", "Master's", "PhD"])
        employment_type = st.selectbox("Employment type", ["Full-time", "Part-time", "Self-employed", "Unemployed"])
        marital_status = st.selectbox("Marital status", ["Single", "Married", "Divorced"])
        loan_purpose = st.selectbox("Loan purpose", ["Auto", "Business", "Education", "Home", "Other"])
    with c4:
        has_mortgage = st.selectbox("Has mortgage", ["Yes", "No"])
        has_dependents = st.selectbox("Has dependents", ["Yes", "No"])
        has_cosigner = st.selectbox("Has co-signer", ["Yes", "No"])

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    run = st.button("Run risk assessment  →")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# RIGHT — animated dial + verdict
# =========================================================
def build_dial_html(probability: float, animate: bool):
    """Animated SVG arc gauge, sweeps from 0 to `probability` on load."""
    pct = max(0.0, min(1.0, probability))
    deg = pct * 270  # 270-degree sweep gauge

    if pct < 0.35:
        color = "#3DDC97"; verdict = "LOW RISK"; note = "Profile aligns with repayment."
    elif pct < 0.6:
        color = "#E8B04B"; verdict = "MODERATE RISK"; note = "Some caution flags present."
    else:
        color = "#FF5C5C"; verdict = "HIGH RISK"; note = "Strong default signal detected."

    anim_class = "animate" if animate else ""
    pct_label = f"{pct*100:.1f}%"

    return f"""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center;
                font-family:'Inter',sans-serif; padding: 0.4rem 0 0.2rem 0;">
      <style>
        @keyframes sweepIn {{
          from {{ stroke-dashoffset: 628; }}
          to   {{ stroke-dashoffset: {628 - (628 * (deg/360))}; }}
        }}
        @keyframes fadeUp {{
          from {{ opacity:0; transform: translateY(8px); }}
          to   {{ opacity:1; transform: translateY(0px); }}
        }}
        @keyframes pulseGlow {{
          0%,100% {{ filter: drop-shadow(0 0 6px {color}66); }}
          50%     {{ filter: drop-shadow(0 0 16px {color}aa); }}
        }}
        .dial-arc.animate {{ animation: sweepIn 1.3s cubic-bezier(.2,.8,.2,1) forwards, pulseGlow 2.4s ease-in-out 1.3s infinite; }}
        .dial-label.animate {{ animation: fadeUp .6s ease 1.0s both; }}
      </style>
      <svg width="260" height="260" viewBox="0 0 260 260">
        <circle cx="130" cy="130" r="100" fill="none" stroke="#232830" stroke-width="14"
                stroke-dasharray="471 628" stroke-dashoffset="0" transform="rotate(135 130 130)" stroke-linecap="round"/>
        <circle class="dial-arc {anim_class}" cx="130" cy="130" r="100" fill="none" stroke="{color}" stroke-width="14"
                stroke-dasharray="628" stroke-dashoffset="{628 if animate else 628 - (628*(deg/360))}"
                transform="rotate(135 130 130)" stroke-linecap="round"/>
        <text x="130" y="122" text-anchor="middle" font-family="IBM Plex Mono, monospace"
              font-size="40" font-weight="600" fill="{color}">{pct_label}</text>
        <text x="130" y="148" text-anchor="middle" font-family="IBM Plex Mono, monospace"
              font-size="12" letter-spacing="2" fill="#7C8592">DEFAULT PROB.</text>
      </svg>
      <div class="dial-label {anim_class}" style="text-align:center; margin-top:0.3rem;">
        <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.15rem; color:{color}; letter-spacing:0.03em;">
          {verdict}
        </div>
        <div style="color:#7C8592; font-size:0.85rem; margin-top:0.2rem;">{note}</div>
      </div>
    </div>
    """

with right:
    st.markdown('<div class="ledger-card" style="height:100%;">', unsafe_allow_html=True)
    st.markdown('<div class="ledger-heading">03 — Risk Reading</div>', unsafe_allow_html=True)

    if not run:
        st.markdown(build_dial_html(0.0, animate=False), unsafe_allow_html=True)
        st.markdown(
            '<p style="text-align:center; color:#7C8592; font-size:0.85rem; margin-top:0.6rem;">'
            'Fill in the profile and run the assessment to see a live reading.</p>',
            unsafe_allow_html=True
        )
    else:
        if model is None:
            st.error("Model file `best_model.pkl` not found. Place it next to this script.")
        else:
            row = pd.DataFrame([{
                "Age": age, "Income": income, "LoanAmount": loan_amount,
                "CreditScore": credit_score, "MonthsEmployed": months_employed,
                "NumCreditLines": num_credit_lines, "InterestRate": interest_rate,
                "LoanTerm": loan_term, "DTIRatio": dti_ratio,
                "Education": education, "EmploymentType": employment_type,
                "MaritalStatus": marital_status, "HasMortgage": has_mortgage,
                "HasDependents": has_dependents, "LoanPurpose": loan_purpose,
                "HasCoSigner": has_cosigner,
            }])

            with st.spinner("Reading applicant signal..."):
                time.sleep(0.4)
                try:
                    proba = float(model.predict_proba(row)[0][1])
                except Exception as e:
                    st.error(f"Prediction failed: {e}")
                    proba = None

            if proba is not None:
                st.markdown(build_dial_html(proba, animate=True), unsafe_allow_html=True)

                st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric("Credit score", credit_score)
                m2.metric("DTI ratio", f"{dti_ratio:.2f}")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center; color:#4B525E; font-size:0.75rem; font-family:\'IBM Plex Mono\',monospace;">'
    'LEDGER TERMINAL · MODEL: LOGISTIC REGRESSION + SMOTE · FOR PORTFOLIO DEMONSTRATION ONLY</p>',
    unsafe_allow_html=True
)