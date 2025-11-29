import time
import schedule
from db import init_db, get_db
from models import get_all_companies, get_unanalysed_posts_by_brand, save_debunk, mark_email_sent, create_ledger_entry, get_last_ledger_entry
from collector_runner import collect_for_company
from core.analyzer import extract_claim, search_evidence, analyze_claim
from core.ledger import compute_hash
from core.email_utils import send_alert_email
import config

# --- JOB 1: DATA COLLECTION (Runs infrequently to save API quota) ---
def collection_job():
    print("\n⏰ [Scheduler] Starting 6-hour data collection cycle...")
    db = next(get_db())
    companies = get_all_companies(db)
    
    if not companies:
        print("   No companies to track.")
        return

    for company in companies:
        print(f"   🔎 Auto-scanning for: {company.name}")
        collect_for_company(company.name, config.RISK_KEYWORDS)
    
    print("✅ [Scheduler] Collection cycle finished.")

# --- JOB 2: HIGH THREAT WATCHDOG (Runs constantly) ---
def watchdog_job():
    """
    Checks DB for ANY unanalysed 'High' priority posts.
    This catches threats found by the auto-collector OR manual dashboard scans.
    """
    db = next(get_db())
    companies = get_all_companies(db)
    
    for company in companies:
        # Get all unanalysed posts for this brand
        posts = get_unanalysed_posts_by_brand(db, company.name)
        
        for post in posts:
            # STRICT FILTER: Only act on HIGH priority
            if post.priority != "High":
                continue

            print(f"\n⚡ [Watchdog] HIGH THREAT DETECTED (ID: {post.id})! Analyzing immediately...")
            
            try:
                # 1. Extract Claim
                claim = extract_claim(post.text)
                if claim == "NO_CLAIM":
                    # Mark as analysed (but empty) so we don't loop forever
                    save_debunk(db, post.id, {"verdict": "Skipped", "explanation": "No claim extracted"})
                    continue
                    
                # 2. Analyze
                evidence = search_evidence(claim)
                analysis = analyze_claim(claim, evidence, company.name)
                
                if not isinstance(analysis, dict):
                    continue
                if 'claim' not in analysis: analysis['claim'] = claim

                # 3. Save to Ledger
                debunk = save_debunk(db, post.id, analysis)
                
                last_entry = get_last_ledger_entry(db)
                prev = last_entry.hash if last_entry else "0"*64
                create_ledger_entry(db, debunk.id, compute_hash(prev, {"id": debunk.id}), prev)
                
                # 4. Email (Only if verdict is bad)
                if debunk.verdict in ["False", "Misleading"]:
                    print(f"   🚨 Verdict is {debunk.verdict}. Sending Email to {company.email}...")
                    success = send_alert_email(
                        to_email=company.email,
                        company_name=company.name,
                        post_url=post.url,
                        claim=claim,
                        verdict=debunk.verdict,
                        explanation=debunk.explanation,
                        pr_response=debunk.pr_response
                    )
                    if success:
                        mark_email_sent(db, debunk.id)
                else:
                    print(f"   ℹ️ Verdict is {debunk.verdict}. No email sent.")
                    
            except Exception as e:
                print(f"   ❌ Error processing post {post.id}: {e}")

# --- MAIN LOOP ---
init_db()

# Schedule Collection every 6 hours
schedule.every(6).hours.do(collection_job)

# Schedule Watchdog every 10 seconds (Near Real-Time)
schedule.every(10).seconds.do(watchdog_job)

# Run collection once on startup to ensure we have data
print("🤖 NeuroChain Bot Active.")
print("   - Collection: Every 6 hours")
print("   - Watchdog: Every 10 seconds (Monitoring for High Threats)")

# Uncomment to run a full collection immediately on startup:
# collection_job()

while True:
    schedule.run_pending()
    time.sleep(1)