import streamlit as st
import requests
import os
import json
import pandas as pd

API_BASE_URL = "http://127.0.0.1:8000"
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "results"))

st.set_page_config(page_title="Tender Evaluation System", layout="wide")

st.title("🏛️ AI Tender Evaluation System")
st.caption("Automated pipeline for evaluating bidder compliance against tender criteria.")

# ─── 1. File Upload ──────────────────────────────────────────────────────────
st.subheader("1. Upload Documents")
tender_file = st.file_uploader("Tender Document", type=["pdf", "png", "jpg", "jpeg"], key="tender")
bidder_files = st.file_uploader("Bidder Documents (multiple allowed)", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bidders")

if st.button("📤 Upload Files"):
    if tender_file and bidder_files:
        with st.spinner("Uploading files..."):
            files = [("tender_file", (tender_file.name, tender_file.getvalue(), tender_file.type))]
            for b in bidder_files:
                files.append(("bidder_files", (b.name, b.getvalue(), b.type)))
            try:
                res = requests.post(f"{API_BASE_URL}/upload", files=files)
                if res.status_code == 200:
                    st.success(f"Uploaded: {tender_file.name} + {len(bidder_files)} bidder file(s)")
                else:
                    st.error(f"Upload failed: {res.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")
    else:
        st.warning("Please select both a tender document and at least one bidder document.")

st.markdown("---")

# ─── 2. Run Evaluation ───────────────────────────────────────────────────────
st.subheader("2. Run Evaluation Pipeline")
if st.button("▶️ Run Evaluation", type="primary"):
    steps = [
        ("🔍 OCR Processing", "/process"),
        ("🧠 AI Data Extraction", "/extract"),
        ("⚖️ Rule Engine Evaluation", "/evaluate"),
    ]
    all_ok = True
    for label, endpoint in steps:
        with st.spinner(f"{label}..."):
            try:
                res = requests.post(f"{API_BASE_URL}{endpoint}", timeout=180)
                if res.status_code == 200:
                    st.success(f"{label} — Done")
                else:
                    st.error(f"{label} failed: {res.text}")
                    all_ok = False
                    break
            except Exception as e:
                st.error(f"Connection error during {label}: {e}")
                all_ok = False
                break
    if all_ok:
        st.balloons()

st.markdown("---")

# ─── Helper functions ─────────────────────────────────────────────────────────
RESULT_ICONS = {"pass": "✅", "fail": "❌", "review": "⚠️"}
STATUS_COLORS = {"Eligible": "🟢", "Not Eligible": "🔴", "Needs Review": "🟡"}

def style_row(row):
    result = str(row.get("Result", "")).lower()
    color_map = {"pass": "#1a3d1a", "fail": "#3d1a1a", "review": "#3d3214"}
    bg = color_map.get(result, "transparent")
    return [f"background-color: {bg}"] * len(row)

def update_status(bidder_filename, status):
    payload = {"bidder": bidder_filename, "human_status": status}
    try:
        res = requests.post(f"{API_BASE_URL}/review", json=payload)
        if res.status_code == 200:
            st.success(f"✅ Marked as **{status}**")
            st.rerun()
        else:
            st.error(f"Failed to update status: {res.text}")
    except Exception as e:
        st.error(f"Connection error: {e}")

# ─── 3. Results Display ───────────────────────────────────────────────────────
st.subheader("3. Evaluation Results")

if os.path.exists(RESULTS_DIR):
    result_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('.json')]
    if not result_files:
        st.info("No results yet. Run the evaluation pipeline first.")
    else:
        for bidder_file in result_files:
            file_path = os.path.join(RESULTS_DIR, bidder_file)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            bidder_name = bidder_file.replace(".json", "")
            ai_status = data.get("ai_status", "Unknown")
            human_status = data.get("human_status")
            final_status = data.get("final_status", "Unknown")
            summary = data.get("summary", "")
            passed = data.get("passed", 0)
            total = data.get("total", 0)
            evaluations = data.get("evaluations", [])

            st.markdown(f"### 📄 {bidder_name}")

            # ── Summary line ──────────────────────────────────────
            icon = STATUS_COLORS.get(final_status, "⚪")
            if final_status == "Eligible":
                st.success(f"{icon} Final Status: **{final_status}** — {summary}")
            elif final_status == "Not Eligible":
                st.error(f"{icon} Final Status: **{final_status}** — {summary}")
            else:
                st.warning(f"{icon} Final Status: **{final_status}** — {summary}")

            # ── Status metrics ─────────────────────────────────────
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🤖 AI Status", ai_status)
            c2.metric("🧑‍⚖️ Human Status", human_status if human_status else "Not Applied")
            c3.metric("🎯 Final Status", final_status)
            c4.metric("📊 Criteria", f"{passed}/{total} passed")


            # ── Criteria table with color rows ────────────────────
            if evaluations:
                st.markdown("#### Criteria Breakdown")
                df = pd.DataFrame([{
                    "Criterion": ev.get("criterion", "").capitalize(),
                    "Required": ev.get("required_display", ev.get("required", "N/A")),
                    "Found": ev.get("found_display", ev.get("found", "N/A")),
                    "Result": RESULT_ICONS.get(ev.get("result", ""), "") + " " + str(ev.get("result", "")).capitalize(),
                    "Reason": ev.get("reason", ""),
                    "Evidence": ev.get("evidence", ""),
                    "Page": ev.get("page", "—"),
                    "Confidence": ev.get("confidence", "—"),
                } for ev in evaluations])

                # Apply row-level background colors
                raw_results = [ev.get("result", "") for ev in evaluations]
                def color_row(row):
                    idx = df.index.get_loc(row.name)
                    result = raw_results[idx] if idx < len(raw_results) else ""
                    bg = {"pass": "#0f2e0f", "fail": "#2e0f0f", "review": "#2e2700"}.get(result, "")
                    return [f"background-color: {bg}; color: white" if bg else ""] * len(row)

                styled = df.style.apply(color_row, axis=1)
                st.dataframe(styled, use_container_width=True)

                # ── Evidence highlights ────────────────────────────
                st.markdown("#### 🔍 Evidence Highlights")
                for ev in evaluations:
                    page = ev.get("page")
                    evidence = ev.get("evidence", "No match found")
                    crit = ev.get("criterion", "").capitalize()
                    icon = RESULT_ICONS.get(ev.get("result", ""), "")
                    if page:
                        st.markdown(f"- {icon} **{crit}** — Found on **Page {page}**: *\"{evidence}\"*")
                    else:
                        st.markdown(f"- {icon} **{crit}** — *{evidence}*")


            # ── Human review buttons ────────────────────────────────
            st.markdown("#### 🧑‍⚖️ Human Review")
            btn1, btn2, btn3 = st.columns(3)
            with btn1:
                if st.button("✅ Approve", key=f"approve_{bidder_name}"):
                    update_status(bidder_file, "Eligible")
            with btn2:
                if st.button("❌ Mark Not Eligible", key=f"reject_{bidder_name}"):
                    update_status(bidder_file, "Not Eligible")
            with btn3:
                if st.button("⚠️ Needs Review", key=f"review_{bidder_name}"):
                    update_status(bidder_file, "Needs Review")

            st.markdown("---")
else:
    st.info("No results directory found. Please run the evaluation pipeline first.")
