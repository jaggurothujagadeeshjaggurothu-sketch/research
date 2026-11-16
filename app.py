"""
ResearchMate AI - Smart Research Assistant (Streamlit edition)
Turns a rough project idea into titles, abstract, keywords, objectives and future
enhancements using a local Ollama Llama 3.2 model.

Run:  streamlit run app.py
"""
from __future__ import annotations

import html
import json
import os
import uuid
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

import ai_service as ai
import storage
from pdf_utils import SECTION_TITLES, build_pdf
from styles import CSS

st.set_page_config(
    page_title="ResearchMate AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)

DOMAINS = [
    "AI / Machine Learning",
    "Internet of Things (IoT)",
    "Web Development",
    "Cybersecurity",
    "Data Science",
    "Cloud Computing",
    "Other",
]
LEVELS = ["Beginner", "Intermediate", "Advanced"]
PAGES = [
    ("Dashboard", ":material/dashboard:"),
    ("New Research", ":material/add_circle:"),
    ("Research History", ":material/history:"),
    ("Saved Projects", ":material/bookmark:"),
    ("Settings", ":material/settings:"),
]


# --------------------------------------------------------------------------- #
# State helpers
# --------------------------------------------------------------------------- #
def _default(name: str, fallback: str) -> str:
    """Environment variable > Streamlit secret > fallback."""
    value = os.getenv(name)
    if value:
        return value
    try:
        return str(st.secrets[name])
    except Exception:
        return fallback


def init_state() -> None:
    ss = st.session_state
    if "persist_flag_set" not in ss:
        # Allow RESEARCHMATE_PERSIST to be provided through Streamlit secrets.
        if "RESEARCHMATE_PERSIST" not in os.environ:
            os.environ["RESEARCHMATE_PERSIST"] = _default("RESEARCHMATE_PERSIST", "1")
        ss.persist_flag_set = True
    ss.setdefault("page", "Dashboard")
    ss.setdefault("cfg_url", _default("OLLAMA_URL", ai.DEFAULT_URL))
    ss.setdefault("cfg_model", _default("OLLAMA_MODEL", ai.DEFAULT_MODEL))
    ss.setdefault("cfg_temp", 0.7)
    ss.setdefault("cfg_timeout", 180)
    if "history" not in ss:
        ss.history = storage.load()
    ss.setdefault("current_id", None)
    ss.setdefault("in_idea", "")
    ss.setdefault("in_domain", DOMAINS[0])
    ss.setdefault("in_other", "")
    ss.setdefault("in_tech", "")
    ss.setdefault("in_level", "Intermediate")


def get_entry(entry_id: str | None) -> dict | None:
    return next((e for e in st.session_state.history if e["id"] == entry_id), None)


def persist() -> None:
    storage.save(st.session_state.history)


def goto(page: str) -> None:
    st.session_state.page = page


def new_research() -> None:
    clear_all()
    st.session_state.page = "Dashboard"


def clear_all() -> None:
    ss = st.session_state
    ss.in_idea, ss.in_tech, ss.in_other = "", "", ""
    ss.in_domain, ss.in_level = DOMAINS[0], "Intermediate"
    ss.current_id = None


def open_entry(entry_id: str) -> None:
    ss = st.session_state
    e = get_entry(entry_id)
    if not e:
        return
    ss.current_id = entry_id
    ss.in_idea, ss.in_tech, ss.in_level = e["idea"], e.get("tech", ""), e.get("level", "Intermediate")
    if e["domain"] in DOMAINS:
        ss.in_domain, ss.in_other = e["domain"], ""
    else:
        ss.in_domain, ss.in_other = "Other", e["domain"]
    ss.page = "Dashboard"


def toggle_saved(entry_id: str) -> None:
    e = get_entry(entry_id)
    if e:
        e["saved"] = not e.get("saved", False)
        persist()


def delete_entry(entry_id: str) -> None:
    ss = st.session_state
    ss.history = [e for e in ss.history if e["id"] != entry_id]
    if ss.current_id == entry_id:
        ss.current_id = None
    persist()


@st.cache_data(ttl=15, show_spinner=False)
def cached_status(url: str, model: str) -> tuple[bool, str]:
    return ai.check_connection(url, model)


# --------------------------------------------------------------------------- #
# Formatting helpers
# --------------------------------------------------------------------------- #
def section_text(key: str, value) -> str:
    if key == "abstract":
        return value
    if key == "keywords":
        return ", ".join(value)
    return "\n".join(f"{i}. {v}" for i, v in enumerate(value, 1))


def full_text(entry: dict) -> str:
    r = entry["result"]
    parts = [
        "RESEARCHMATE AI - RESEARCH PROPOSAL",
        f"Domain: {entry['domain']} | Level: {entry.get('level', '-')} | Generated: {entry['created']}",
        f"Project idea: {entry['idea']}",
        "",
    ]
    for i, key in enumerate(ai.SECTIONS, 1):
        parts += [f"{i}. {SECTION_TITLES[key].upper()}", section_text(key, r[key]), ""]
    return "\n".join(parts).strip()


def copy_button(text: str, label: str = "Copy", height: int = 46) -> None:
    """Clipboard button (Streamlit has no native copy API, so we use a tiny HTML component)."""
    payload = json.dumps(text).replace("<", "\\u003c")
    page = (
        f"""
        <style>
          html,body{{margin:0;background:transparent;font-family:Inter,system-ui,sans-serif}}
          button{{width:100%;height:38px;margin-top:2px;border-radius:12px;border:1px solid rgba(255,255,255,.14);
            background:rgba(255,255,255,.06);color:#e8ebff;font-weight:600;font-size:14px;cursor:pointer;transition:all .25s}}
          button:hover{{border-color:rgba(124,92,255,.8);background:rgba(124,92,255,.22);box-shadow:0 8px 24px rgba(124,92,255,.3)}}
          button.ok{{border-color:#2ee59d;color:#2ee59d}}
        </style>
        <button id="b">📋 {html.escape(label)}</button>
        <script>
          const t = {payload}; const b = document.getElementById('b'); const l = b.innerHTML;
          b.onclick = async () => {{
            try {{ await navigator.clipboard.writeText(t); }}
            catch (e) {{ const a=document.createElement('textarea'); a.value=t; document.body.appendChild(a); a.select(); document.execCommand('copy'); a.remove(); }}
            b.innerHTML='✅ Copied!'; b.classList.add('ok');
            setTimeout(()=>{{b.innerHTML=l; b.classList.remove('ok')}}, 1600);
          }};
        </script>
        """
    )
    if hasattr(st, "iframe"):  # newer Streamlit (components.html is being removed)
        st.iframe(page, height=height)
    else:
        components.html(page, height=height)


LOADER = """
<div class="rm-loader"><div class="rm-orb"></div>
  <div><b>{title}</b><span>{sub}</span><div class="rm-bar"><i></i></div></div>
</div>
"""


def show_ollama_error(exc: Exception) -> None:
    if isinstance(exc, ai.ModelNotFoundError):
        st.error(f"**Model not installed.** {exc}", icon="📦")
    elif isinstance(exc, ai.OllamaConnectionError):
        st.error(f"**Ollama is not reachable.** {exc}", icon="🔌")
    elif isinstance(exc, ai.InvalidResponseError):
        st.error(f"**The AI response could not be validated.** {exc} Please try again.", icon="⚠️")
    else:
        st.error(str(exc), icon="⚠️")


# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #
def render_sidebar() -> None:
    ss = st.session_state
    with st.sidebar:
        st.markdown(
            '<div class="rm-logo"><div class="mark">🔬</div><div><b>ResearchMate AI</b><span>Smart Research Assistant</span></div></div>',
            unsafe_allow_html=True,
        )
        for name, icon in PAGES:
            active = ss.page == name and name != "New Research"
            if name == "New Research":
                st.button(name, icon=icon, key="nav_new", use_container_width=True, on_click=new_research)
            else:
                st.button(
                    name, icon=icon, key=f"nav_{name}", use_container_width=True,
                    type="primary" if active else "secondary", on_click=goto, args=(name,),
                )
        ok, msg = cached_status(ss.cfg_url, ss.cfg_model)
        st.markdown(
            f'<div class="rm-status"><span class="rm-dot {"ok" if ok else "bad"}"></span>'
            f'{"Ollama online" if ok else "Ollama offline"}<br><span style="opacity:.8">{html.escape(ss.cfg_model)}</span></div>',
            unsafe_allow_html=True,
        )
        if not ok:
            st.caption(msg)


# --------------------------------------------------------------------------- #
# Results
# --------------------------------------------------------------------------- #
def regenerate(entry: dict, key: str) -> None:
    ss = st.session_state
    slot = st.empty()
    slot.markdown(
        LOADER.format(title=f"Regenerating {SECTION_TITLES[key].lower()}…", sub="Llama 3.2 is writing a fresh version."),
        unsafe_allow_html=True,
    )
    try:
        entry["result"][key] = ai.regenerate_section(
            key, entry["idea"], entry["domain"], entry["result"], entry.get("tech", ""), entry.get("level", ""),
            ss.cfg_url, ss.cfg_model, min(1.0, ss.cfg_temp + 0.2), ss.cfg_timeout,
        )
        persist()
        slot.empty()
        st.toast(f"{SECTION_TITLES[key]} regenerated", icon="✨")
        st.rerun()
    except ai.OllamaError as exc:
        slot.empty()
        show_ollama_error(exc)


def card_actions(entry: dict, key: str, regen: bool = True) -> None:
    text = section_text(key, entry["result"][key])
    c1, c2, c3 = st.columns(3 if regen else 2)
    with c1:
        copy_button(text, "Copy")
    if regen:
        with c2:
            if st.button("Regenerate", icon=":material/autorenew:", key=f"regen_{key}_{entry['id']}", use_container_width=True):
                regenerate(entry, key)
    with (c3 if regen else c2):
        st.download_button(
            "Download", text, file_name=f"researchmate_{key}.txt", mime="text/plain",
            icon=":material/download:", key=f"dl_{key}_{entry['id']}", use_container_width=True,
        )


def card_head(num: int, title: str) -> None:
    st.markdown(f'<div class="rm-card-head"><div class="rm-badge">{num:02d}</div><h3>{title}</h3></div>', unsafe_allow_html=True)


def render_results(entry: dict) -> None:
    r = entry["result"]
    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    st.markdown("### Your Research Dashboard")
    for w in entry.get("warnings", []):
        st.warning(w, icon="📝")

    # Global actions
    g1, g2, g3 = st.columns([1.3, 1, 1])
    with g1:
        try:
            pdf_bytes = build_pdf(entry)
            st.download_button(
                "Download Complete Research (PDF)", pdf_bytes, file_name="ResearchMate_Research.pdf",
                mime="application/pdf", type="primary", icon=":material/picture_as_pdf:",
                key=f"pdf_{entry['id']}", use_container_width=True,
            )
        except Exception as exc:  # never let PDF problems break the page
            st.error(f"PDF export failed: {exc}")
    with g2:
        copy_button(full_text(entry), "Copy All Research")
    with g3:
        saved = entry.get("saved", False)
        st.button(
            "Saved" if saved else "Save Project", icon=":material/bookmark:" if saved else ":material/bookmark_add:",
            key=f"save_{entry['id']}", on_click=toggle_saved, args=(entry["id"],), use_container_width=True,
        )

    # 1 Titles
    with st.container(key="card_titles"):
        card_head(1, SECTION_TITLES["titles"])
        st.markdown(
            "".join(f'<div class="rm-title-row"><i>{i}</i><span>{html.escape(t)}</span></div>' for i, t in enumerate(r["titles"], 1)),
            unsafe_allow_html=True,
        )
        card_actions(entry, "titles")

    # 2 Abstract
    with st.container(key="card_abstract"):
        card_head(2, SECTION_TITLES["abstract"])
        st.markdown(f'<div class="rm-abstract">{html.escape(r["abstract"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="rm-meta">{ai.word_count(r["abstract"])} words</div>', unsafe_allow_html=True)
        card_actions(entry, "abstract")

    # 3 Keywords
    with st.container(key="card_keywords"):
        card_head(3, SECTION_TITLES["keywords"])
        st.markdown("".join(f'<span class="rm-chip">{html.escape(k)}</span>' for k in r["keywords"]), unsafe_allow_html=True)
        st.write("")
        card_actions(entry, "keywords")

    # 4 & 5
    for key, num in (("objectives", 4), ("future_enhancements", 5)):
        with st.container(key=f"card_{key}"):
            card_head(num, SECTION_TITLES[key])
            st.markdown(
                "".join(f'<div class="rm-li"><b>{i}</b><span>{html.escape(v)}</span></div>' for i, v in enumerate(r[key], 1)),
                unsafe_allow_html=True,
            )
            card_actions(entry, key)


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #
def validate_inputs(idea: str, domain: str, other: str) -> list[str]:
    errors = []
    idea = idea.strip()
    if not idea:
        errors.append("Please describe your project idea.")
    elif len(idea.split()) < 4:
        errors.append("Your idea is too short - write at least a full sentence (4+ words).")
    elif len(idea) > 1500:
        errors.append("Your idea is too long - please keep it under 1500 characters (2-3 lines is ideal).")
    if domain == "Other" and other.strip() and len(other.strip()) < 3:
        errors.append("Please enter a valid custom domain.")
    return errors


def page_dashboard() -> None:
    ss = st.session_state
    st.markdown(
        '<div class="rm-hero"><span class="eyebrow">✦ Powered by local Llama 3.2</span>'
        "<h1>Turn Your Ideas Into Research</h1><p>Your AI-powered academic research assistant.</p></div>",
        unsafe_allow_html=True,
    )

    hist = ss.history
    domains = [e["domain"] for e in hist]
    top = max(set(domains), key=domains.count) if domains else "-"
    st.markdown(
        f'<div class="rm-stats">'
        f'<div class="rm-stat"><small>Projects</small><div>{len(hist)}</div></div>'
        f'<div class="rm-stat"><small>Saved</small><div>{sum(1 for e in hist if e.get("saved"))}</div></div>'
        f'<div class="rm-stat"><small>Top domain</small><div style="font-size:1.05rem;padding-top:.5rem">{html.escape(top)}</div></div>'
        f'<div class="rm-stat"><small>AI engine</small><div style="font-size:1.05rem;padding-top:.5rem">{html.escape(ss.cfg_model)}</div></div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # ----- Input card -----
    with st.container(key="card_input"):
        st.markdown(
            '<div class="rm-card-head"><div class="rm-badge">✦</div><h3>Describe your project</h3></div>',
            unsafe_allow_html=True,
        )
        st.text_area(
            "Project idea",
            key="in_idea",
            height=130,
            max_chars=1500,
            placeholder="Describe your project idea in 2–3 lines...",
            help="Example: Detect fake news using machine learning.",
        )
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Domain", DOMAINS, key="in_domain")
        with c2:
            st.selectbox("Research level", LEVELS, key="in_level")
        if ss.in_domain == "Other":
            st.text_input("Your domain (optional)", key="in_other", placeholder="e.g. Healthcare Informatics")
        st.text_input(
            "Technology preferences (optional)", key="in_tech",
            placeholder="e.g. Python, TensorFlow, BERT, MQTT, React…",
        )
        b1, b2 = st.columns([3, 1])
        generate = b1.button("Generate Research", icon=":material/auto_awesome:", type="primary", use_container_width=True, key="btn_generate")
        b2.button("Clear all", icon=":material/delete_sweep:", use_container_width=True, key="btn_clear", on_click=clear_all)
        if not ss.in_idea.strip():
            st.caption("💡 Try: *Detect fake news using machine learning.*")

    if generate:
        domain = ss.in_other.strip() if ss.in_domain == "Other" and ss.in_other.strip() else ss.in_domain
        errors = validate_inputs(ss.in_idea, ss.in_domain, ss.in_other)
        if errors:
            for e in errors:
                st.error(e, icon="✋")
        else:
            slot = st.empty()
            slot.markdown(
                LOADER.format(
                    title="Analyzing your idea…",
                    sub="Llama 3.2 is drafting titles, abstract, keywords, objectives and enhancements. The first run can take a minute.",
                ),
                unsafe_allow_html=True,
            )
            try:
                result, warnings = ai.generate_research(
                    ss.in_idea, domain, ss.in_tech, ss.in_level, ss.cfg_url, ss.cfg_model, ss.cfg_temp, ss.cfg_timeout,
                )
                entry = {
                    "id": uuid.uuid4().hex[:8],
                    "created": datetime.now().strftime("%d %b %Y, %H:%M"),
                    "idea": ss.in_idea.strip(),
                    "domain": domain,
                    "level": ss.in_level,
                    "tech": ss.in_tech.strip(),
                    "result": result,
                    "warnings": warnings,
                    "saved": False,
                }
                ss.history.insert(0, entry)
                ss.current_id = entry["id"]
                persist()
                slot.empty()
                st.toast("Research generated!", icon="🎉")
            except ai.OllamaError as exc:
                slot.empty()
                show_ollama_error(exc)

    entry = get_entry(ss.current_id)
    if entry:
        render_results(entry)
    elif not generate:
        st.markdown(
            '<div class="rm-empty">Your generated research will appear here.</div>'
            '<div class="rm-feature-grid">'
            '<div class="rm-feature"><b>3 Research Titles</b>Academic, unique, domain-aware.</div>'
            '<div class="rm-feature"><b>150–200 word Abstract</b>Background, method, outcomes, significance.</div>'
            '<div class="rm-feature"><b>5 Keywords</b>Ready for indexing.</div>'
            '<div class="rm-feature"><b>Objectives &amp; Future Work</b>Measurable and realistic.</div>'
            "</div>",
            unsafe_allow_html=True,
        )


def render_entries(entries: list[dict], key_prefix: str, empty_msg: str) -> None:
    q = st.text_input("Search", key=f"{key_prefix}_q", placeholder="Search by idea, domain or title…", label_visibility="collapsed")
    if q.strip():
        ql = q.lower()
        entries = [e for e in entries if ql in (e["idea"] + e["domain"] + " ".join(e["result"]["titles"])).lower()]
    if not entries:
        st.markdown(f'<div class="rm-empty">{empty_msg}</div>', unsafe_allow_html=True)
        return
    for e in entries:
        with st.container(key=f"card_{key_prefix}_{e['id']}"):
            st.markdown(
                f'<div class="rm-card-head"><div class="rm-badge">{"★" if e.get("saved") else "•"}</div>'
                f'<h3>{html.escape(e["result"]["titles"][0])}</h3></div>'
                f'<div class="rm-meta" style="margin:-.4rem 0 .7rem">{html.escape(e["domain"])} · {html.escape(e.get("level", ""))} · {e["created"]}</div>'
                f'<div class="rm-abstract" style="font-size:.93rem">{html.escape(e["idea"])}</div>',
                unsafe_allow_html=True,
            )
            c1, c2, c3, c4 = st.columns(4)
            c1.button("Open", icon=":material/open_in_new:", key=f"{key_prefix}_open_{e['id']}", on_click=open_entry, args=(e["id"],), use_container_width=True)
            c2.button(
                "Unsave" if e.get("saved") else "Save", icon=":material/bookmark:", key=f"{key_prefix}_save_{e['id']}",
                on_click=toggle_saved, args=(e["id"],), use_container_width=True,
            )
            c3.download_button(
                "PDF", build_pdf(e), file_name=f"ResearchMate_{e['id']}.pdf", mime="application/pdf",
                icon=":material/picture_as_pdf:", key=f"{key_prefix}_pdf_{e['id']}", use_container_width=True,
            )
            c4.button("Delete", icon=":material/delete:", key=f"{key_prefix}_del_{e['id']}", on_click=delete_entry, args=(e["id"],), use_container_width=True)


def page_history() -> None:
    st.markdown('<div class="rm-page-title">Research History</div>', unsafe_allow_html=True)
    st.caption("Every research package you generate is stored here.")
    render_entries(st.session_state.history, "hist", "No research yet. Generate your first project from the Dashboard.")


def page_saved() -> None:
    st.markdown('<div class="rm-page-title">Saved Projects</div>', unsafe_allow_html=True)
    st.caption("Projects you bookmarked.")
    render_entries([e for e in st.session_state.history if e.get("saved")], "saved", "No saved projects yet. Click “Save Project” on any result.")


def page_settings() -> None:
    ss = st.session_state
    st.markdown('<div class="rm-page-title">Settings</div>', unsafe_allow_html=True)
    st.caption("Configure the local Ollama connection.")
    with st.container(key="card_settings"):
        ss.cfg_url = st.text_input("Ollama URL", ss.cfg_url, help="Default: http://localhost:11434 (the app calls /api/chat).")
        ss.cfg_model = st.text_input("Model", ss.cfg_model, help="Default: llama3.2")
        c1, c2 = st.columns(2)
        ss.cfg_temp = c1.slider("Creativity (temperature)", 0.0, 1.0, float(ss.cfg_temp), 0.05)
        ss.cfg_timeout = c2.slider("Request timeout (seconds)", 30, 600, int(ss.cfg_timeout), 10)
        if st.button("Test connection", icon=":material/wifi_tethering:"):
            cached_status.clear()
            ok, msg = ai.check_connection(ss.cfg_url, ss.cfg_model)
            (st.success if ok else st.error)(msg)
            if ok or "not installed" in msg:
                try:
                    st.caption("Installed models: " + ", ".join(ai.list_models(ss.cfg_url)))
                except ai.OllamaError:
                    pass
    with st.container(key="card_data"):
        card_head(0, "Your data")
        st.caption(
            "History is stored in `data/history.json`." if storage.persistence_enabled()
            else "Persistence is off (RESEARCHMATE_PERSIST=0): history lives only in this browser session."
        )
        if st.button("Delete all history", icon=":material/delete_forever:"):
            ss.history, ss.current_id = [], None
            persist()
            st.toast("History cleared")
            st.rerun()


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
init_state()
render_sidebar()
{
    "Dashboard": page_dashboard,
    "Research History": page_history,
    "Saved Projects": page_saved,
    "Settings": page_settings,
}.get(st.session_state.page, page_dashboard)()
