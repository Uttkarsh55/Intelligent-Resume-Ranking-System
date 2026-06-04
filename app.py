import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from resume_parser import extract_text, extract_candidate_info
from ranker import rank_resumes, rank_resumes_bert

def render_results_ui(df_results, prefix_key):
    st.markdown("<p style='font-size:12px; font-weight:600; color:#64748B; text-transform:uppercase;'>Ranked Candidates</p>", unsafe_allow_html=True)
    
    # Display matching candidates cards
    for idx, row in df_results.iterrows():
        rank = row["Rank"]
        name = row["Candidate Name"]
        score = row["Match Score"]
        skills_str = row["Skills"]
        reason = row.get("Match Reason", "")
        
        skills_html = ""
        if skills_str and skills_str != "N/A":
            skills = [s.strip() for s in skills_str.split(",")]
            for skill in skills[:6]:  # Display up to 6 skills
                skills_html += f'<span class="pill pill-skill">{skill}</span>'
        
        card_html = f"""
        <div class="candidate-card">
            <div style="display: flex; align-items: center;">
                <span class="rank-number">#{rank}</span>
                <div>
                    <div class="candidate-name">{name}</div>
                    <div style="margin-top: 4px;">{skills_html}</div>
                    <div style="margin-top: 6px; font-size: 12px; color: #737373; font-style: italic;">{reason}</div>
                </div>
            </div>
            <div class="match-badge">{score}% Match</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Keyword Gap Analysis Section
    st.markdown("#### Candidate Details & Keyword Analysis")
    candidate_names = df_results["Candidate Name"].tolist()
    selected_name = st.selectbox("Select candidate to inspect keyword alignment:", candidate_names, key=f"sel_{prefix_key}")
    
    cand_row = df_results[df_results["Candidate Name"] == selected_name].iloc[0]
    
    col_details, col_gaps = st.columns([1, 2])
    
    with col_details:
        st.markdown(f"""
        <div style="background:#ffffff; border: 1px solid #e5e5e5; padding: 16px; border-radius: 6px; transition: all 0.3s ease;">
            <div style="font-size: 18px; font-weight: 600; color: #171717;">{cand_row["Candidate Name"]}</div>
            <div style="font-size: 13px; color: #737373; margin-top: 4px;">Rank: #{cand_row["Rank"]}</div>
            <div style="font-size: 13px; color: #737373;">Email: {cand_row["Email"]}</div>
            <div style="font-size: 13px; color: #737373;">Phone: {cand_row["Phone"]}</div>
            <div style="margin-top:12px; font-weight: 600; font-size: 13px; color:#1a1a1a;">Overall Score: {cand_row["Match Score"]}%</div>
            <div style="font-weight: 500; font-size: 13px; color:#737373;">Keyword Match: {cand_row["Keyword Match Rate"]}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_gaps:
        matched_kws = cand_row["Matched Keywords"]
        missing_kws = cand_row["Missing Keywords"]
        
        # Display matched keywords
        st.markdown("#### Matched Keywords")
        if matched_kws:
            matched_html = ""
            for kw in matched_kws:
                matched_html += f'<span class="pill pill-match">{kw}</span> '
            st.markdown(matched_html, unsafe_allow_html=True)
        else:
            st.markdown("<span style='font-size:12px; color:#a3a3a3;'>No key terms matched.</span>", unsafe_allow_html=True)
            
        st.markdown("#### Missing Keywords", unsafe_allow_html=True)
        if missing_kws:
            missing_html = ""
            for kw in missing_kws:
                missing_html += f'<span class="pill pill-missing">{kw}</span> '
            st.markdown(missing_html, unsafe_allow_html=True)
        else:
            st.markdown("<span style='font-size:12px; color:#404040;'>All key terms matched.</span>", unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(" View Candidate Resume Text"):
        st.text_area("Extracted Resume Content:", value=cand_row["Raw Text"], height=300, disabled=True, key=f"txt_{prefix_key}")

# Page Configuration
st.set_page_config(
    page_title=" Intelligent Resume Ranking System",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Minimalist, Professional Monochrome CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1a1a1a;
    }
    
    /* Wizard Steps Indicator */
    .steps-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 35px;
        padding: 0 10px;
        position: relative;
    }
    
    .steps-line {
        position: absolute;
        top: 15px;
        left: 30px;
        right: 30px;
        height: 1px;
        background-color: #e5e5e5;
        z-index: 1;
    }
    
    .step-node {
        position: relative;
        z-index: 2;
        background: #ffffff;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 500;
        font-size: 14px;
        border: 1px solid #e5e5e5;
        color: #a3a3a3;
        transition: all 0.4s ease;
    }
    
    .step-node.active {
        border-color: #1a1a1a;
        color: #1a1a1a;
        background-color: #f5f5f5;
        box-shadow: 0 0 0 2px rgba(26, 26, 26, 0.1);
    }
    
    .step-node.completed {
        border-color: #404040;
        color: #ffffff;
        background-color: #404040;
    }
    
    .step-label {
        position: absolute;
        top: 38px;
        font-size: 11px;
        font-weight: 500;
        white-space: nowrap;
        color: #737373;
        transition: all 0.4s ease;
    }
    
    .step-node.active .step-label {
        color: #1a1a1a;
        font-weight: 600;
    }
    
    /* Clean Custom Cards */
    .app-card {
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.4s ease;
    }
    
    .app-card:hover {
        border-color: #a3a3a3;
    }
    
    /* Candidate Item Cards */
    .candidate-card {
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .candidate-card:hover {
        transform: translateY(-2px);
        border-color: #1a1a1a;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    /* Badges */
    .pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 11px;
        font-weight: 500;
        margin: 3px;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    
    .pill-skill {
        background: #f5f5f5;
        color: #404040;
        border-color: #e5e5e5;
    }
    
    .pill-match {
        background: #fafafa;
        color: #171717;
        border-color: #d4d4d4;
    }
    
    .pill-missing {
        background: #ffffff;
        color: #737373;
        border-color: #e5e5e5;
        border-style: dashed;
    }
    
    /* Match Percentage Score Badge */
    .match-badge {
        font-size: 16px;
        font-weight: 600;
        color: #1a1a1a;
        background: #f5f5f5;
        border: 1px solid #e5e5e5;
        padding: 6px 14px;
        border-radius: 4px;
        text-align: center;
        min-width: 80px;
        transition: all 0.3s ease;
    }
    
    .rank-number {
        font-size: 16px;
        font-weight: 600;
        color: #737373;
        margin-right: 14px;
    }
    
    .candidate-name {
        font-size: 15px;
        font-weight: 600;
        color: #171717;
    }
    
    /* Streamlit overrides for minimalist monochrome */
    div.stButton > button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 4px !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        background-color: #404040 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #e5e5e5 !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #1a1a1a !important;
        background-color: #f5f5f5 !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "step" not in st.session_state:
    st.session_state.step = "jd"
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""
if "resumes" not in st.session_state:
    st.session_state.resumes = []
if "results" not in st.session_state:
    st.session_state.results = pd.DataFrame()
if "results_bert" not in st.session_state:
    st.session_state.results_bert = pd.DataFrame()
if "top_keywords" not in st.session_state:
    st.session_state.top_keywords = []

# Title Header
st.markdown("<h2 style='text-align: center; font-weight: 700; margin-bottom: 30px; color: #1a1a1a;'>Intelligent Resume Ranker</h2>", unsafe_allow_html=True)

# Render Wizard Steps
step_names = ["1. Job Description", "2. Upload Resumes", "3. Analysis Results"]
current_step = st.session_state.step

step_nodes_html = ""
step_line_html = '<div class="steps-line"></div>'

for idx, step_key in enumerate(["jd", "resumes", "results"]):
    node_class = "step-node"
    if current_step == step_key:
        node_class += " active"
    elif (st.session_state.step == "resumes" and step_key == "jd") or (st.session_state.step == "results" and step_key in ["jd", "resumes"]):
        node_class += " completed"
        
    step_nodes_html += f'<div class="{node_class}">{idx + 1}<div class="step-label">{step_names[idx]}</div></div>'

st.markdown(f'<div class="steps-container">{step_line_html}{step_nodes_html}</div><br>', unsafe_allow_html=True)

# ==================== STEP 1: JOB DESCRIPTION ====================
if st.session_state.step == "jd":
    st.markdown("#### Define Job Description")
    st.markdown("<p style='font-size:13px; color:#64748B; margin-top:-10px;'>Provide the target job description to match candidates against.</p>", unsafe_allow_html=True)
    
    jd_input_method = st.tabs(["Paste Text", "Upload File (.txt)"])
    
    with jd_input_method[0]:
        jd_pasted = st.text_area(
            "Paste Job Description text here:",
            value=st.session_state.jd_text,
            height=300,
            placeholder="Describe the job role, required skills, and responsibilities...",
            label_visibility="collapsed"
        )
        if jd_pasted:
            st.session_state.jd_text = jd_pasted
            
    with jd_input_method[1]:
        jd_file = st.file_uploader("Upload a text file containing the Job Description:", type=["txt"], label_visibility="collapsed")
        if jd_file:
            st.session_state.jd_text = jd_file.read().decode("utf-8")
            st.success("File uploaded successfully.")

    col_space, col_next = st.columns([4, 1])
    with col_next:
        if st.button("Continue", type="primary", use_container_width=True):
            if not st.session_state.jd_text.strip():
                st.error("Please provide a Job Description.")
            else:
                st.session_state.step = "resumes"
                st.rerun()

# ==================== STEP 2: RESUME UPLOADER ====================
elif st.session_state.step == "resumes":
    st.markdown("#### Upload Candidate Resumes")
    st.markdown("<p style='font-size:13px; color:#64748B; margin-top:-10px;'>Upload one or more resumes (.pdf, .docx, .txt) to rank against the Job Description.</p>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose files:",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    parsed_resumes = []
    if uploaded_files:
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Parse uploaded files in memory / temp files
        for file in uploaded_files:
            temp_path = os.path.join(temp_dir, file.name)
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
                
            text = extract_text(temp_path)
            candidate_info = extract_candidate_info(text, file.name)
            
            try:
                os.remove(temp_path)
            except:
                pass
                
            parsed_resumes.append({
                "id": file.name,
                "file_name": file.name,
                "raw_text": text,
                "candidate_info": candidate_info
            })
            
        st.session_state.resumes = parsed_resumes
        
        # Display uploaded file list summary
        st.markdown("<br><b>Uploaded Candidates:</b>", unsafe_allow_html=True)
        for res in parsed_resumes:
            st.markdown(f" {res['candidate_info']['name']} *({res['file_name']})*")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_back, col_space, col_rank = st.columns([1.2, 2.8, 1.5])
    with col_back:
        if st.button("Back", use_container_width=True):
            st.session_state.step = "jd"
            st.rerun()
            
    with col_rank:
        if st.button("Analyze & Rank ", type="primary", use_container_width=True):
            if not st.session_state.resumes:
                st.error("Please upload at least one resume.")
            else:
                with st.spinner("Analyzing relevance..."):
                    results, keywords = rank_resumes(
                        st.session_state.jd_text,
                        st.session_state.resumes
                    )
                    st.session_state.results = results
                    st.session_state.top_keywords = keywords
                    st.session_state.step = "results"
                    st.rerun()

# ==================== STEP 3: RESULTS AND DETAILS ====================
elif st.session_state.step == "results":
    if st.session_state.results.empty:
        st.session_state.step = "jd"
        st.rerun()
        
    st.markdown("#### Matching Analysis & Rankings")
    
    tab1, tab2 = st.tabs(["TF-IDF Keyword Ranking", "🧠 Semantic BERT Ranking"])
    
    with tab1:
        render_results_ui(st.session_state.results, "tfidf")
        
    with tab2:
        if st.session_state.results_bert.empty:
            st.info("Sentence-BERT evaluates the semantic context of the resumes instead of just matching exact keywords. The first run requires downloading the model weights.")
            if st.button("Run Sentence-BERT Analysis 🚀"):
                with st.spinner("Downloading Transformer Model & Ranking..."):
                    results_bert, _ = rank_resumes_bert(st.session_state.jd_text, st.session_state.resumes)
                    st.session_state.results_bert = results_bert
                st.rerun()
        else:
            render_results_ui(st.session_state.results_bert, "bert")
            
    # Start Over / CSV Export Buttons
    st.markdown("<hr>", unsafe_allow_html=True)
    col_csv, col_space, col_reset = st.columns([1.5, 2.5, 1])
    
    with col_csv:
        csv_buffer = io.StringIO()
        export_df = st.session_state.results.drop(columns=["Raw Text", "Matched Keywords", "Missing Keywords"])
        export_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="Export Results (CSV)",
            data=csv_data,
            file_name="resume_ranking_results.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col_reset:
        if st.button("Start Over", type="secondary", use_container_width=True):
            st.session_state.step = "jd"
            st.session_state.jd_text = ""
            st.session_state.resumes = []
            st.session_state.results = pd.DataFrame()
            st.session_state.results_bert = pd.DataFrame()
            st.session_state.top_keywords = []
            st.rerun()
