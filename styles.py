"""styles.py - premium dark glassmorphism theme + animations for ResearchMate AI."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root{
  --navy:#0a0e27; --navy2:#11163a; --purple:#7c5cff; --blue:#00b4ff;
  --text:#e8ebff; --muted:#9aa3d6; --glass:rgba(255,255,255,.055); --stroke:rgba(255,255,255,.12);
  --grad:linear-gradient(135deg,#7c5cff 0%,#00b4ff 100%);
}
html, body, [class*="css"], .stApp { font-family:'Inter',sans-serif; color:var(--text); }
.stApp{
  background:
    radial-gradient(900px 500px at 8% -10%, rgba(124,92,255,.30), transparent 60%),
    radial-gradient(800px 500px at 100% 0%, rgba(0,180,255,.20), transparent 60%),
    radial-gradient(700px 500px at 50% 120%, rgba(124,92,255,.18), transparent 60%),
    var(--navy);
  background-attachment:fixed;
}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"]{ display:none !important; }
[data-testid="stHeader"]{ background:transparent; }
.block-container{ padding-top:2.2rem; padding-bottom:4rem; max-width:1150px; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg, rgba(17,22,58,.92), rgba(10,14,39,.96));
  border-right:1px solid var(--stroke); backdrop-filter:blur(18px);
}
[data-testid="stSidebar"] .block-container{ padding-top:1.4rem; }
.rm-logo{ display:flex; align-items:center; gap:.75rem; margin:.2rem 0 1.4rem; }
.rm-logo .mark{
  width:42px; height:42px; border-radius:13px; background:var(--grad); display:grid; place-items:center;
  box-shadow:0 0 24px rgba(124,92,255,.65); font-size:1.3rem; animation:pulseGlow 3.2s ease-in-out infinite;
}
.rm-logo b{ font-family:'Space Grotesk',sans-serif; font-size:1.18rem; letter-spacing:.2px; display:block; line-height:1.1; }
.rm-logo span{ font-size:.72rem; color:var(--muted); letter-spacing:.14em; text-transform:uppercase; }
[data-testid="stSidebar"] .stButton button{
  justify-content:flex-start; border:1px solid transparent; background:transparent; color:var(--muted);
  border-radius:12px; padding:.62rem .9rem; font-weight:500; transition:all .25s ease; box-shadow:none;
}
[data-testid="stSidebar"] .stButton button > div, [data-testid="stSidebar"] .stButton button p{ justify-content:flex-start !important; text-align:left; width:100%; }
[data-testid="stSidebar"] .stButton button:hover{ background:var(--glass); color:#fff; border-color:var(--stroke); transform:translateX(3px); }
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"], [data-testid="stSidebar"] button[kind="primary"]{
  background:linear-gradient(135deg, rgba(124,92,255,.40), rgba(0,180,255,.22)); color:#fff;
  border:1px solid rgba(124,92,255,.55); box-shadow:0 0 22px rgba(124,92,255,.28);
}
.rm-status{ margin-top:1.2rem; padding:.7rem .9rem; border-radius:12px; background:var(--glass); border:1px solid var(--stroke); font-size:.8rem; color:var(--muted); }
.rm-dot{ display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:.5rem; }
.rm-dot.ok{ background:#2ee59d; box-shadow:0 0 10px #2ee59d; } .rm-dot.bad{ background:#ff5d73; box-shadow:0 0 10px #ff5d73; }

/* ---------- Hero ---------- */
.rm-hero{ margin-bottom:1.6rem; animation:fadeUp .7s ease both; }
.rm-hero .eyebrow{ display:inline-block; padding:.28rem .8rem; border-radius:99px; font-size:.72rem; letter-spacing:.14em; text-transform:uppercase;
  background:rgba(124,92,255,.16); border:1px solid rgba(124,92,255,.45); color:#c9bcff; margin-bottom:.9rem; }
.rm-hero h1{ font-family:'Space Grotesk',sans-serif; font-size:clamp(2rem,5vw,3.3rem); line-height:1.08; margin:0 0 .6rem; font-weight:700; letter-spacing:-.02em;
  background:linear-gradient(120deg,#fff 10%,#b9a8ff 45%,#4cc9ff 90%); -webkit-background-clip:text; background-clip:text; color:transparent; }
.rm-hero p{ color:var(--muted); font-size:1.08rem; margin:0; }
.rm-page-title{ font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700; margin:0 0 .3rem;
  background:linear-gradient(120deg,#fff,#b9a8ff 60%,#4cc9ff); -webkit-background-clip:text; background-clip:text; color:transparent; }

/* ---------- Stat tiles ---------- */
.rm-stats{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:.9rem; margin:0 0 1.4rem; }
.rm-stat{ padding:1rem 1.1rem; border-radius:18px; background:var(--glass); border:1px solid var(--stroke); backdrop-filter:blur(14px);
  animation:fadeUp .7s ease both; transition:transform .25s ease, box-shadow .25s ease; }
.rm-stat:hover{ transform:translateY(-3px); box-shadow:0 12px 32px rgba(124,92,255,.22); }
.rm-stat small{ color:var(--muted); font-size:.74rem; letter-spacing:.1em; text-transform:uppercase; }
.rm-stat div{ font-family:'Space Grotesk',sans-serif; font-size:1.55rem; font-weight:700; margin-top:.15rem; }

/* ---------- Glass cards (st.container(key="card_*")) ---------- */
[class*="st-key-card"]{
  background:var(--glass); border:1px solid var(--stroke); border-radius:22px; padding:1.4rem 1.5rem 1.2rem;
  backdrop-filter:blur(18px); box-shadow:0 10px 40px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.06);
  animation:fadeUp .6s ease both; transition:border-color .3s ease, box-shadow .3s ease; margin-bottom:.4rem;
}
[class*="st-key-card"]:hover{ border-color:rgba(124,92,255,.5); box-shadow:0 14px 48px rgba(124,92,255,.20); }
.rm-card-head{ display:flex; align-items:center; gap:.8rem; margin-bottom:.9rem; }
.rm-badge{ min-width:34px; height:34px; border-radius:11px; background:var(--grad); display:grid; place-items:center; font-weight:700; font-size:.85rem;
  box-shadow:0 0 16px rgba(124,92,255,.5); }
.rm-card-head h3{ margin:0; font-family:'Space Grotesk',sans-serif; font-size:1.15rem; font-weight:600; }
.rm-title-row{ display:flex; gap:.8rem; padding:.8rem 1rem; margin:.45rem 0; border-radius:14px; background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.07); line-height:1.45; transition:all .25s ease; }
.rm-title-row:hover{ background:rgba(124,92,255,.12); border-color:rgba(124,92,255,.4); transform:translateX(4px); }
.rm-title-row i{ font-style:normal; font-weight:700; color:#8fd8ff; font-family:'Space Grotesk',sans-serif; }
.rm-abstract{ line-height:1.78; color:#dfe3ff; text-align:justify; font-size:1rem; }
.rm-meta{ color:var(--muted); font-size:.8rem; margin-top:.6rem; }
.rm-chip{ display:inline-block; margin:.25rem .4rem .25rem 0; padding:.42rem .95rem; border-radius:99px; font-size:.88rem; font-weight:500;
  background:linear-gradient(135deg,rgba(124,92,255,.22),rgba(0,180,255,.14)); border:1px solid rgba(124,92,255,.45); transition:all .25s ease; }
.rm-chip:hover{ transform:translateY(-2px) scale(1.03); box-shadow:0 0 18px rgba(0,180,255,.35); }
.rm-li{ display:flex; gap:.75rem; margin:.55rem 0; line-height:1.55; }
.rm-li b{ flex:0 0 26px; height:26px; border-radius:8px; display:grid; place-items:center; font-size:.78rem; background:rgba(0,180,255,.16); color:#8fd8ff; border:1px solid rgba(0,180,255,.4); }

/* ---------- Inputs ---------- */
label, [data-testid="stWidgetLabel"] p{ color:#cfd5ff !important; font-weight:500; }
.stTextArea textarea, .stTextInput input, [data-baseweb="select"] > div, [data-baseweb="input"]{
  background:rgba(8,11,34,.70) !important; border:1px solid var(--stroke) !important; border-radius:14px !important; color:var(--text) !important;
  transition:border-color .25s ease, box-shadow .25s ease;
}
.stTextArea textarea{ font-size:1rem; line-height:1.6; }
.stTextArea textarea:focus, .stTextInput input:focus{ border-color:var(--purple) !important; box-shadow:0 0 0 3px rgba(124,92,255,.25), 0 0 24px rgba(124,92,255,.25) !important; }

/* ---------- Buttons ---------- */
.stButton button, .stDownloadButton button{
  border-radius:12px; border:1px solid var(--stroke); background:var(--glass); color:var(--text); font-weight:600;
  transition:all .25s ease; padding:.5rem 1rem;
}
.stButton button:hover, .stDownloadButton button:hover{ border-color:rgba(124,92,255,.7); background:rgba(124,92,255,.18); transform:translateY(-2px); color:#fff; box-shadow:0 8px 24px rgba(124,92,255,.28); }
.stMain button[data-testid="stBaseButton-primary"], .stMain button[kind="primary"]{
  background:var(--grad); border:none; color:#fff; padding:.8rem 1.4rem; font-size:1.02rem; letter-spacing:.2px;
  box-shadow:0 0 26px rgba(124,92,255,.55), 0 8px 24px rgba(0,180,255,.25); animation:pulseGlow 3s ease-in-out infinite;
}
.stMain button[data-testid="stBaseButton-primary"]:hover, .stMain button[kind="primary"]:hover{
  transform:translateY(-3px) scale(1.01); box-shadow:0 0 38px rgba(124,92,255,.85), 0 12px 32px rgba(0,180,255,.4); }

/* ---------- Loader ---------- */
.rm-loader{ display:flex; align-items:center; gap:1.2rem; padding:1.4rem 1.6rem; border-radius:20px; margin:1rem 0;
  background:var(--glass); border:1px solid rgba(124,92,255,.5); box-shadow:0 0 40px rgba(124,92,255,.25); animation:fadeUp .4s ease both; }
.rm-orb{ flex:0 0 54px; height:54px; border-radius:50%; background:conic-gradient(from 0deg,#7c5cff,#00b4ff,#7c5cff);
  animation:spin 1.1s linear infinite; mask:radial-gradient(circle 17px at center,transparent 96%,#000 100%); -webkit-mask:radial-gradient(circle 17px at center,transparent 96%,#000 100%); filter:drop-shadow(0 0 10px #7c5cff); }
.rm-loader b{ display:block; font-size:1.05rem; } .rm-loader span{ color:var(--muted); font-size:.88rem; }
.rm-bar{ margin-top:.7rem; height:5px; border-radius:9px; background:rgba(255,255,255,.08); overflow:hidden; width:min(360px,60vw); }
.rm-bar i{ display:block; height:100%; width:40%; border-radius:9px; background:var(--grad); animation:slide 1.3s ease-in-out infinite; }

.rm-empty{ text-align:center; padding:2.6rem 1rem; color:var(--muted); border:1px dashed var(--stroke); border-radius:20px; background:rgba(255,255,255,.025); }
.rm-feature-grid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:.9rem; margin-top:1.2rem; }
.rm-feature{ padding:1rem; border-radius:16px; background:var(--glass); border:1px solid var(--stroke); font-size:.9rem; color:var(--muted); }
.rm-feature b{ color:var(--text); display:block; margin-bottom:.25rem; }
hr{ border-color:var(--stroke) !important; }
[data-testid="stAlert"]{ border-radius:14px; backdrop-filter:blur(10px); }
[data-testid="stExpander"]{ border-radius:14px; border:1px solid var(--stroke); background:var(--glass); }
iframe{ border-radius:12px; }

/* ---------- Keyframes ---------- */
@keyframes fadeUp{ from{opacity:0; transform:translateY(14px)} to{opacity:1; transform:none} }
@keyframes spin{ to{ transform:rotate(360deg) } }
@keyframes slide{ 0%{ transform:translateX(-110%) } 100%{ transform:translateX(280%) } }
@keyframes pulseGlow{ 0%,100%{ filter:brightness(1) } 50%{ filter:brightness(1.18) } }

/* ---------- Mobile ---------- */
@media (max-width:768px){
  .block-container{ padding:1.2rem .9rem 3rem; }
  [class*="st-key-card"]{ padding:1.05rem 1rem; border-radius:18px; }
  .rm-abstract{ text-align:left; }
  .rm-loader{ flex-direction:column; text-align:center; }
}
</style>
"""
