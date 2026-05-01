import streamlit as st
import requests
import os
import json

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "results"))

st.set_page_config(page_title="Tender Evaluation System", layout="wide")

st.title("🏛️ AI Tender Evaluation System")
st.markdown("Automated pipeline for evaluating bidder compliance against tender criteria.")

tab1, tab2, tab3 = st.tabs(["📤 1. Upload Documents", "⚙️ 2. Run Pipeline", "🧑‍⚖️ 3. Human Review"])

# --- TAB 1: UPLOAD ---
with tab1:
    st.header("Upload Documents")
    
    tender_file = st.file_uploader("Upload Tender Document (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"], key="tender")
    bidder_files = st.file_uploader("Upload Bidder Documents", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bidders")
    
    if st.button("Submit Documents", type="primary"):
        if not tender_file:
            st.error("Please upload a tender document.")
        elif not bidder_files:
            st.error("Please upload at least one bidder document.")
        else:
            with st.spinner("Uploading files to server..."):
                files = [("tender_file", (tender_file.name, tender_file.getvalue(), tender_file.type))]
                for b_file in bidder_files:
                    files.append(("bidder_files", (b_file.name, b_file.getvalue(), b_file.type)))
                
                try:
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.success("Files uploaded successfully!")
                        st.json(response.json())
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

# --- TAB 2: PIPELINE ---
with tab2:
    st.header("Pipeline Execution")
    st.markdown("Run the processing stages sequentially.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Step 1: OCR Processing")
        if st.button("Run OCR", use_container_width=True):
            with st.spinner("Extracting text from documents... This may take a while."):
                try:
                    res = requests.post(f"{API_BASE_URL}/process")
                    if res.status_code == 200:
                        st.success("OCR completed!")
                        st.json(res.json())
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
                    
    with col2:
        st.subheader("Step 2: LLM Extraction")
        if st.button("Run Extraction", use_container_width=True):
            with st.spinner("Structuring data with Groq LLM..."):
                try:
                    res = requests.post(f"{API_BASE_URL}/extract")
                    if res.status_code == 200:
                        st.success("Extraction completed!")
                        st.json(res.json())
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
                    
    with col3:
        st.subheader("Step 3: Rule Evaluation")
        if st.button("Run Evaluation", use_container_width=True):
            with st.spinner("Cross-referencing bidder data against tender..."):
                try:
                    res = requests.post(f"{API_BASE_URL}/evaluate")
                    if res.status_code == 200:
                        st.success("Evaluation completed!")
                        st.json(res.json())
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

# --- TAB 3: HUMAN REVIEW ---
with tab3:
    st.header("Human-in-the-Loop Review")
    
    if not os.path.exists(RESULTS_DIR):
        st.warning("No results directory found. Please run the pipeline first.")
    else:
        result_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('.json')]
        
        if not result_files:
            st.info("No evaluation results available yet.")
        else:
            selected_bidder = st.selectbox("Select Bidder to Review", result_files)
            
            if selected_bidder:
                file_path = os.path.join(RESULTS_DIR, selected_bidder)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                st.markdown("---")
                
                # Top-level status
                st.subheader(f"Evaluation: {selected_bidder}")
                
                ai_status = data.get("ai_status", "Unknown")
                human_status = data.get("human_status")
                final_status = data.get("final_status")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("🤖 AI Status", ai_status)
                c2.metric("🧑‍⚖️ Human Status", human_status if human_status else "Pending")
                c3.metric("🎯 Final Status", final_status)
                
                st.markdown("### Criteria Breakdown")
                evaluations = data.get("evaluations", [])
                
                for ev in evaluations:
                    with st.expander(f"{ev.get('result', '').upper()} - {ev.get('criterion', '').capitalize()}"):
                        st.markdown(f"**Required:** `{ev.get('operator')} {ev.get('required')}`")
                        st.markdown(f"**Found:** `{ev.get('found')}`")
                        st.markdown(f"**Reason:** {ev.get('reason')}")
                        st.info(f"**Evidence (Page {ev.get('page')}):** \"{ev.get('evidence')}\"")
                
                st.markdown("---")
                st.subheader("Submit Override")
                
                with st.form("review_form"):
                    new_status = st.selectbox(
                        "Final Decision", 
                        ["Eligible", "Not Eligible", "Needs Review"],
                        index=["Eligible", "Not Eligible", "Needs Review"].index(ai_status) if ai_status in ["Eligible", "Not Eligible", "Needs Review"] else 0
                    )
                    
                    if st.form_submit_button("Lock Decision", type="primary"):
                        payload = {
                            "bidder": selected_bidder,
                            "human_status": new_status
                        }
                        try:
                            res = requests.post(f"{API_BASE_URL}/review", json=payload)
                            if res.status_code == 200:
                                st.success("Decision locked successfully! Refreshing...")
                                st.rerun()
                            else:
                                st.error(f"Failed to submit: {res.text}")
                        except Exception as e:
                            st.error(f"Connection error: {e}")
