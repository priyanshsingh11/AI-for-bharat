import streamlit as st
import requests
import os
import json
import pandas as pd

API_BASE_URL = "http://127.0.0.1:8000"
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "results"))

st.set_page_config(page_title="Tender Evaluation System", layout="wide")

st.title("AI Tender Evaluation System")

# --- 1. File Upload Section ---
st.subheader("1. Upload Documents")
tender_file = st.file_uploader("Upload Tender Document", type=["pdf", "png", "jpg", "jpeg"], key="tender")
bidder_files = st.file_uploader("Upload Bidder Documents", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bidders")

if st.button("Upload Files"):
    if tender_file and bidder_files:
        with st.spinner("Uploading files..."):
            files = [("tender_file", (tender_file.name, tender_file.getvalue(), tender_file.type))]
            for b_file in bidder_files:
                files.append(("bidder_files", (b_file.name, b_file.getvalue(), b_file.type)))
            try:
                response = requests.post(f"{API_BASE_URL}/upload", files=files)
                if response.status_code == 200:
                    st.success("Files uploaded successfully!")
                else:
                    st.error(f"Upload failed: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")
    else:
        st.warning("Please upload both tender and bidder documents.")

st.markdown("---")

# --- 2. Run Evaluation Button ---
st.subheader("2. Run Evaluation Pipeline")
if st.button("Run Evaluation", type="primary"):
    with st.spinner("Processing documents (OCR)..."):
        try:
            res1 = requests.post(f"{API_BASE_URL}/process")
            if res1.status_code == 200:
                with st.spinner("Extracting structured data (LLM)..."):
                    res2 = requests.post(f"{API_BASE_URL}/extract")
                    if res2.status_code == 200:
                        with st.spinner("Evaluating criteria and extracting evidence..."):
                            res3 = requests.post(f"{API_BASE_URL}/evaluate")
                            if res3.status_code == 200:
                                st.success("Evaluation pipeline completed successfully!")
                            else:
                                st.error(f"Evaluation failed: {res3.text}")
                    else:
                        st.error(f"Extraction failed: {res2.text}")
            else:
                st.error(f"OCR Processing failed: {res1.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")

st.markdown("---")

# --- 3. Results Display & Human-in-the-Loop ---
st.subheader("3. Evaluation Results")

def update_status(bidder_filename, status):
    payload = {
        "bidder": bidder_filename,
        "human_status": status
    }
    try:
        res = requests.post(f"{API_BASE_URL}/review", json=payload)
        if res.status_code == 200:
            st.success(f"Status updated to {status} for {bidder_filename}")
            st.rerun()
        else:
            st.error(f"Failed to update status: {res.text}")
    except Exception as e:
        st.error(f"Connection error: {e}")

if os.path.exists(RESULTS_DIR):
    result_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('.json')]
    if not result_files:
        st.info("No evaluation results available yet. Please run the evaluation pipeline.")
    else:
        for bidder_file in result_files:
            file_path = os.path.join(RESULTS_DIR, bidder_file)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            bidder_name = bidder_file.replace(".json", "")
            
            st.markdown(f"### Bidder: {bidder_name}")
            
            ai_status = data.get("ai_status", "Unknown")
            human_status = data.get("human_status", "Not Reviewed")
            final_status = data.get("final_status", "Unknown")
            
            # Color coding final status
            if final_status == "Eligible":
                st.success(f"Final Status: {final_status}")
            elif final_status == "Not Eligible":
                st.error(f"Final Status: {final_status}")
            else:
                st.warning(f"Final Status: {final_status}")
                
            # Status Display
            col1, col2, col3 = st.columns(3)
            col1.metric("AI Status", ai_status)
            col2.metric("Human Status", human_status if human_status else "Not Applied")
            col3.metric("Final Status", final_status)
            
            # Detailed Explanation Table
            evaluations = data.get("evaluations", [])
            if evaluations:
                df = pd.DataFrame(evaluations)
                # Reorder and rename columns for display
                display_cols = ["criterion", "required", "found", "result", "reason", "evidence", "page"]
                # Filter out columns that might be missing just in case
                display_cols = [c for c in display_cols if c in df.columns]
                df_display = df[display_cols].copy()
                
                # Capitalize column names for UI
                df_display.columns = [col.capitalize() for col in df_display.columns]
                if "Page" in df_display.columns:
                    df_display.rename(columns={"Page": "Page Number"}, inplace=True)
                
                st.dataframe(df_display, use_container_width=True)
                
                # Evidence Highlight
                st.markdown("#### Evidence Highlights")
                for ev in evaluations:
                    page = ev.get("page")
                    evidence = ev.get("evidence")
                    criterion = ev.get("criterion", "").capitalize()
                    
                    if page:
                        st.markdown(f"- **{criterion}** - Found on Page {page}: *'{evidence}'*")
                    else:
                        st.markdown(f"- **{criterion}** - *{evidence}*")
            
            # Human-in-the-Loop buttons
            st.markdown("#### Human Review")
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                if st.button("Approve", key=f"approve_{bidder_name}"):
                    update_status(bidder_file, "Eligible")
            with btn_col2:
                if st.button("Mark as Not Eligible", key=f"reject_{bidder_name}"):
                    update_status(bidder_file, "Not Eligible")
            with btn_col3:
                if st.button("Needs Review", key=f"review_{bidder_name}"):
                    update_status(bidder_file, "Needs Review")
                    
            st.markdown("---")
else:
    st.info("No evaluation results available yet. Please run the evaluation pipeline.")
