import streamlit as st
import pandas as pd
import time
from db import init_db, get_db
# REMOVED 'get_debunk_by_post_id' to fix ImportError
from models import Post, Company, create_post, save_debunk, create_ledger_entry, get_last_ledger_entry, get_unanalysed_posts, get_all_history, add_company, get_all_companies, delete_company
from collector_runner import collect_for_company
from core.analyzer import extract_claim, search_evidence, analyze_claim
from core.ledger import compute_hash
from core.priority import score_priority
from core.email_utils import send_alert_email
import config

# Initialize DB
init_db()

st.set_page_config(page_title="NeuroChain PR Shield", layout="wide")

# --- SIDEBAR ---
st.sidebar.title("🛡️ NeuroChain")
page = st.sidebar.radio("Navigate", ["Alerts Dashboard", "Manage Companies", "New Analysis", "History & Ledger"])

st.sidebar.markdown("---")
if config.OPENAI_API_KEY:
    st.sidebar.success("AI Connected")
else:
    st.sidebar.error("Missing API Key")

# --- HELPERS ---
def run_full_analysis(post_id, post_text, brand):
    with st.spinner("Analyzing..."):
        claim = extract_claim(post_text)
        if claim == "NO_CLAIM":
            st.warning("No claim detected.")
            return
        evidence = search_evidence(claim)
        analysis = analyze_claim(claim, evidence, brand)
        
        if not isinstance(analysis, dict):
            analysis = {
                "verdict": "Unclear",
                "confidence": 0,
                "explanation": "Analysis failed or returned invalid format.",
                "sources": [],
                "pr_response": "Error in analysis."
            }
            
        analysis['claim'] = claim 
        # --- NOISE FILTER (CRITICAL FIX) ---
        if "no clear factual claim" in analysis.get("claim", "").lower():
            return  # drop noise silently

        
        db = next(get_db())
        debunk = save_debunk(db, post_id, analysis)
        
        # Ledger
        last_entry = get_last_ledger_entry(db)
        prev = last_entry.hash if last_entry else "0"*64
        entry = create_ledger_entry(db, debunk.id, compute_hash(prev, {"id": debunk.id}), prev)
        
        st.success("Analysis Complete!")
        st.rerun()

def get_company_email(brand_name):
    db = next(get_db())
    # Fixed: Use 'Company' directly instead of 'models.Company'
    comp = db.query(Company).filter(Company.name == brand_name).first()
    return comp.email if comp else config.EMAIL_SENDER # Fallback to sender (self) if not found

# --- PAGE: MANAGE COMPANIES ---
if page == "Manage Companies":
    st.header("🏢 Company Management")
    st.write("Add companies here. The automated bot will track them 4x/day and email them alerts.")
    
    with st.form("add_company"):
        c_name = st.text_input("Company Name (e.g. Google, Tesla)")
        c_email = st.text_input("Contact Email")
        submitted = st.form_submit_button("Add Company")
        
        if submitted and c_name and c_email:
            db = next(get_db())
            add_company(db, c_name, c_email)
            st.success(f"Tracking added for {c_name}!")
            st.rerun()
            
    st.divider()
    st.subheader("Currently Tracked Companies")
    
    db = next(get_db())
    companies = get_all_companies(db)
    
    if not companies:
        st.info("No companies tracked yet.")
    else:
        for comp in companies:
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"**{comp.name}**")
            c2.write(comp.email)
            if c3.button("Remove", key=f"del_{comp.id}"):
                delete_company(db, comp.id)
                st.rerun()

# --- PAGE: ALERTS DASHBOARD ---
elif page == "Alerts Dashboard":
    st.header("🚨 Threat Alerts (Live)")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Force Scan All Companies Now"):
            db = next(get_db())
            comps = get_all_companies(db)
            if not comps:
                st.error("Please add companies in 'Manage Companies' page first.")
            else:
                total_found = 0
                status = st.empty()
                progress = st.progress(0)
                
                for i, comp in enumerate(comps):
                    status.write(f"Scanning for {comp.name}...")
                    count = collect_for_company(comp.name, config.RISK_KEYWORDS)
                    total_found += count
                    progress.progress((i + 1) / len(comps))
                
                status.success(f"Scan complete! Found {total_found} new items across {len(comps)} companies.")
                time.sleep(2)
                st.rerun()
                
    with col2:
        auto_on = st.checkbox("Enable Auto-Scan (60s)")
        
    if auto_on:
        placeholder = st.empty()
        placeholder.info("⏳ Auto-scan active...")
        time.sleep(60)
        # In a real app, you'd use a better loop, but this works for demo
        st.rerun()

    # Display Posts
    db = next(get_db())
    posts = get_unanalysed_posts(db)
    
    if not posts:
        st.info("No active threats.")
    else:
        for post in posts:
            with st.container():
                c1, c2, c3, c4 = st.columns([1, 1, 4, 1]) # Adjusted columns
                
                # Platform
                c1.markdown(f"**{post.platform.upper()}**")
                
                # Brand
                c2.write(f"**{post.brand}**")
                
                # Text
                c3.write(f"{post.text[:150]}...")
                
                # Priority Badge (The part you were missing/want to see)
                prio = post.priority or "Low" # Default to Low if missing
                if prio == "High":
                    c4.error(f"🔥 {prio}") # Red badge
                elif prio == "Medium":
                    c4.warning(f"⚠️ {prio}") # Yellow/Orange badge
                else:
                    c4.info(f"ℹ️ {prio}") # Blue/Green badge
                
                if c4.button("Analyse", key=f"btn_{post.id}"):
                    run_full_analysis(post.id, post.text, post.brand)
            st.divider()

# --- PAGE: NEW ANALYSIS ---
elif page == "New Analysis":
    st.header("Manual Analysis")
    txt = st.text_area("Paste text:")
    if st.button("Analyze"):
        db = next(get_db())
        # Create dummy post for manual flow
        p = create_post(db, {"platform": "manual", "brand": "Manual", "text": txt, "priority": "High"})
        run_full_analysis(p.id, txt, "Manual")

# --- PAGE: HISTORY & LEDGER ---
elif page == "History & Ledger":
    st.header("History & Reporting")
    db = next(get_db())
    
    # Filter
    history = get_all_history(db)
    
    # Fetch companies for the dropdown
    all_companies = get_all_companies(db)
    
    if not history:
        st.info("No history yet.")
    
    for d in history:
        with st.expander(f"{d.created_at.strftime('%Y-%m-%d %H:%M')} | {d.verdict} | {d.post.brand}"):
            c1, c2 = st.columns([3, 1])
            
            with c1:
                st.markdown(f"**Claim:** {d.claim_text}")
                st.write(d.explanation)
                st.code(d.pr_response, language="text")
                
            with c2:
                st.caption("Actions")
                
                # --- SEND EMAIL BUTTON ---
                email_input = ""
                
                if not all_companies:
                    # Fallback to manual entry if no companies managed
                    email_input = st.text_input("Recipient Email", key=f"email_in_{d.id}")
                else:
                    # Create options list
                    options = [f"{c.name} ({c.email})" for c in all_companies]
                    
                    # Try to find the matching company
                    default_idx = 0
                    for i, c in enumerate(all_companies):
                        # Simple check if brand name matches
                        if c.name.lower() in d.post.brand.lower() or d.post.brand.lower() in c.name.lower():
                            default_idx = i
                            break
                    
                    selected_opt = st.selectbox(
                        "Select Recipient", 
                        options, 
                        index=default_idx, 
                        key=f"sel_{d.id}"
                    )
                    
                    # Parse the email out of "Name (email@domain.com)"
                    if selected_opt:
                        email_input = selected_opt.split("(")[-1].strip(")")

                if st.button("📧 Send Email Report", key=f"email_btn_{d.id}"):
                    if not email_input:
                        st.error("No valid email selected.")
                    else:
                        with st.spinner("Sending email..."):
                            success = send_alert_email(
                                to_email=email_input,
                                company_name=d.post.brand,
                                post_url=d.post.url or "Manual Entry",
                                claim=d.claim_text,
                                verdict=d.verdict,
                                explanation=d.explanation,
                                pr_response=d.pr_response
                            )
                            
                            if success:
                                st.success("Email sent successfully!")
                            else:
                                st.error("Failed to send email. Check console/logs.")