# NeuroChain

## Overview

**NeuroChain** is an AI-powered reputation risk intelligence system.

Most Online Reputation Management (ORM) tools only *listen* — they flood teams with alerts, mentions, and sentiment data. When a real reputational risk appears, PR teams are left asking:

- Is this serious or just noise?
- Do we respond or stay silent?
- How fast is this spreading?
- What exactly are people claiming?

NeuroChain solves this gap by acting as a **decision & response layer on top of existing ORM tools**.

Instead of tracking mentions, NeuroChain:
- Detects real reputation-threatening incidents
- Scores risk based on credibility, spread, and context
- Tracks incidents across their lifecycle
- Helps teams decide *when* and *how* to respond

---

## Problem It Solves

Reputation damage does not happen overnight — it accumulates over time.

Current ORM tools:
- Generate excessive alerts
- Lack prioritization and time awareness
- Do not assist with decision-making or response strategy

As a result:
- Slack channels explode with alerts
- PR teams draft responses from scratch under pressure
- Leadership lacks clear situational awareness

**NeuroChain turns noise into clarity.**

---

## Key Features

- 🔎 **Multi-source monitoring** (news, web, social, manual input)
- ⚠️ **Incident-based risk detection** (not keyword spam)
- 📊 **Risk scoring with source weighting**
- ⏱️ **Time-aware incident timelines**
- 🔁 **Incident lifecycle tracking**  
  (Open → Monitoring → Responded → Closed)
- 🧠 **AI-assisted claim analysis & response drafting**
- 📜 **Ledger-style audit trail for trust & accountability**

---

## Technology Stack

**Frontend**
- Streamlit (dashboard & UI)

**Backend**
- Python
- SQLAlchemy (data models & persistence)

**AI / NLP**
- OpenAI API (claim analysis, explanation, response drafting)

**Data Sources**
- NewsAPI
- Google Web Search
- YouTube Data API
- Manual analyst input

**Architecture Highlights**
- Deterministic priority & risk engine
- AI used for analysis support, not blind automation
- Designed to integrate *alongside* existing ORM tools

---

## Product Demo

🔗 **Demo / Presentation Link:**  
  Drive_Link:https://drive.google.com/file/d/1RI5RHEsje28fGep7-KM5X1xg-UqrOutS/view?usp=sharing
  Youtube_Link:https://youtu.be/EgfDnuKq1m8?si=8VfYkMRa69zZzST1
---

## Status

This project was built as a **working prototype** during **AIBoomi Startup Weekend**.

The current version demonstrates:
- End-to-end incident detection
- Risk scoring & prioritization
- Analyst workflow and reporting

Future work includes:
- Client-facing dashboards
- Slack & email escalation
- Configurable alert thresholds
- Expanded data sources

---

## One-Line Summary

**NeuroChain helps companies decide what to do when their reputation is at risk — before it’s too late.**
