"""
TerraVision — Streamlit Demo UI
Run: streamlit run app.py
"""

import streamlit as st
import tempfile
import os
import sys
import json

# Make sure src/ is importable
sys.path.insert(0, os.path.dirname(__file__))

from src.blueprint import process_blueprint
from src.photo import process_site_photo
from src.diff import compute_diff
from src.claude import claude_analysis

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TerraVision",
    page_icon="🏗️",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Mono', monospace !important; }
.stApp { background-color: #0d0d18; color: #e2e8f0; }
h1, h2, h3 { color: #f97316 !important; }
.stButton > button {
    background: #f97316 !important; color: #0d0d18 !important;
    font-weight: 700 !important; border: none !important;
    width: 100% !important; font-size: 16px !important; padding: 14px !important;
}
.done { color: #10b981; padding: 4px 0; font-size: 14px; }
.miss { color: #f43f5e; padding: 4px 0; font-size: 14px; }
.warn { color: #f97316; padding: 4px 0; font-size: 14px; }
.need { color: #a78bfa; padding: 4px 0; font-size: 14px; }
.step-box {
    background: #1a1a2e; border-left: 3px solid #f97316;
    padding: 10px 14px; margin: 5px 0;
    border-radius: 0 4px 4px 0; font-size: 13px;
}
.obs-box {
    background: #1a1a2e; border-left: 3px solid #10b981;
    padding: 12px 16px; border-radius: 0 4px 4px 0;
    font-size: 13px; line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🏗️ TerraVision")
st.markdown("**Spatial Intelligence Pipeline** — Blueprint × Site Photo × Materials Manifest")
st.caption("Ironsite × UMD Startup Shell Hackathon · Feb 2026")
st.divider()

# ── Default manifest ──────────────────────────────────────────────────────────
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "data", "inputs", "materials_manifest.txt")
DEFAULT_MANIFEST = open(MANIFEST_PATH).read() if os.path.exists(MANIFEST_PATH) else ""

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📐 Blueprint")
    st.caption("Reference drawing or finished-state photo")
    bp_file = st.file_uploader("Blueprint", type=["jpg","jpeg","png"],
                                key="bp", label_visibility="collapsed")
    if bp_file:
        st.image(bp_file, caption="Blueprint (target state)", use_column_width=True)

with col2:
    st.markdown("### 📸 Site Photo")
    st.caption("Current partial state of construction")
    ph_file = st.file_uploader("Site Photo", type=["jpg","jpeg","png"],
                                key="ph", label_visibility="collapsed")
    if ph_file:
        st.image(ph_file, caption="Site photo (current state)", use_column_width=True)

st.markdown("### 📝 Materials Manifest")
manifest = st.text_area("Manifest", value=DEFAULT_MANIFEST,
                         height=200, label_visibility="collapsed")

with st.expander("⚙️ Settings"):
    api_key = st.text_input("Anthropic API Key", type="password",
                             placeholder="sk-ant-...")

st.divider()
run_btn = st.button("🔍 Analyze Construction Progress")

# ── Run ───────────────────────────────────────────────────────────────────────
if run_btn:
    if not bp_file or not ph_file:
        st.error("Please upload both images.")
    elif not api_key and not os.getenv("ANTHROPIC_API_KEY"):
        st.error("Add your Anthropic API key in Settings.")
    else:
        os.environ["ANTHROPIC_API_KEY"] = api_key or os.getenv("ANTHROPIC_API_KEY", "")

        with tempfile.TemporaryDirectory() as tmp:
            bp_path = os.path.join(tmp, "blueprint.jpg")
            ph_path = os.path.join(tmp, "site.jpg")

            with open(bp_path, "wb") as f: f.write(bp_file.getvalue())
            with open(ph_path, "wb") as f: f.write(ph_file.getvalue())

            bar = st.progress(0, "Starting...")
            try:
                bar.progress(10, "Step 1: Blueprint (OpenCV)...")
                bp_data = process_blueprint(bp_path)

                bar.progress(30, "Step 2: Photo detection (YOLOv8)...")
                ph_data = process_site_photo(ph_path)

                bar.progress(55, "Step 3: Spatial diff...")
                diff = compute_diff(bp_data, ph_data, manifest)

                bar.progress(75, "Step 4: Claude reasoning...")
                result = claude_analysis(bp_path, ph_path, manifest, diff)

                bar.progress(100, "✅ Done!")
                st.session_state["result"] = result
                st.session_state["raw"] = {
                    "blueprint_data": bp_data,
                    "photo_data": ph_data,
                    "diff_data": diff
                }
            except Exception as e:
                st.error(f"Error: {e}")
                bar.empty()

# ── Results ───────────────────────────────────────────────────────────────────
if "result" in st.session_state:
    a = st.session_state["result"]

    if "parse_error" in a:
        st.warning("Raw Claude response:")
        st.text(a.get("raw_response", ""))
    else:
        st.divider()
        st.markdown("## 📊 Results")

        pct = a.get("progress_percentage", 0)
        conf = a.get("confidence", "medium").upper()
        conf_color = {"HIGH": "#10b981", "MEDIUM": "#f97316", "LOW": "#f43f5e"}.get(conf, "#888")

        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"### {pct}% Complete")
            st.progress(pct / 100)
            st.caption(a.get("progress_summary", ""))
        with c2:
            st.markdown(
                f'<div style="text-align:center;margin-top:20px">'
                f'<span style="color:{conf_color};border:1px solid {conf_color};'
                f'padding:4px 10px;font-size:12px;font-weight:700">'
                f'{conf}</span></div>',
                unsafe_allow_html=True
            )

        st.divider()

        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.markdown("#### ✅ Done")
            for i in a.get("completed_items", []):
                st.markdown(f'<div class="done">✓ {i}</div>', unsafe_allow_html=True)
        with r2:
            st.markdown("#### ❌ Missing")
            for i in a.get("missing_items", []):
                st.markdown(f'<div class="miss">✗ {i}</div>', unsafe_allow_html=True)
        with r3:
            st.markdown("#### ⚠️ Issues")
            items = a.get("incorrect_items", [])
            for i in items:
                st.markdown(f'<div class="warn">⚠ {i}</div>', unsafe_allow_html=True)
            if not items:
                st.caption("None found")
        with r4:
            st.markdown("#### 📦 Still Needed")
            for i in a.get("materials_still_needed", []):
                st.markdown(f'<div class="need">→ {i}</div>', unsafe_allow_html=True)

        st.divider()
        n1, n2 = st.columns(2)
        with n1:
            st.markdown("#### 🔨 Next Steps")
            for i, s in enumerate(a.get("next_steps", []), 1):
                st.markdown(f'<div class="step-box"><b>{i}.</b> {s}</div>',
                            unsafe_allow_html=True)
        with n2:
            st.markdown("#### 🧠 Spatial Observations")
            st.markdown(f'<div class="obs-box">{a.get("spatial_observations","")}</div>',
                        unsafe_allow_html=True)

        st.divider()
        with st.expander("🔬 Raw Pipeline Data"):
            raw = st.session_state.get("raw", {})
            t1, t2, t3 = st.tabs(["Blueprint", "Photo", "Diff"])
            with t1: st.json(raw.get("blueprint_data", {}))
            with t2: st.json(raw.get("photo_data", {}))
            with t3: st.json(raw.get("diff_data", {}))
