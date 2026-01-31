# =========================================================
# Incident lifecycle constants (GLOBAL)
# =========================================================

INCIDENT_STATUS_OPEN = "open"
INCIDENT_STATUS_MONITORING = "monitoring"
INCIDENT_STATUS_RESPONDED = "responded"
INCIDENT_STATUS_CLOSED = "closed"

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey,Float
from sqlalchemy.orm import relationship
from datetime import datetime
import json

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String)  # news, reddit, youtube, web, manual
    brand = Column(String)
    text = Column(Text)
    url = Column(String, nullable=True)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    priority = Column(String)  # Low, Medium, High
    created_at = Column(DateTime, default=datetime.utcnow)
    analysed = Column(Boolean, default=False)

    debunks = relationship("Debunk", back_populates="post", uselist=False)

class Debunk(Base):
    __tablename__ = "debunks"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    claim_text = Column(Text)
    verdict = Column(String)  # True, Misleading, False, Unclear
    confidence = Column(Integer)
    explanation = Column(Text)
    sources_json = Column(Text)  # JSON string
    pr_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    email_sent = Column(Boolean, default=False) # Track if we emailed the company

    post = relationship("Post", back_populates="debunks")
    ledger_entry = relationship("LedgerEntry", back_populates="debunk", uselist=False)

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    debunk_id = Column(Integer, ForeignKey("debunks.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    hash = Column(String)
    prev_hash = Column(String, nullable=True)

    debunk = relationship("Debunk", back_populates="ledger_entry")

# --- DATA ACCESS HELPERS ---

def add_company(db, name, email):
    existing = db.query(Company).filter(Company.name == name).first()
    if not existing:
        comp = Company(name=name, email=email)
        db.add(comp)
        db.commit()
        return comp
    return existing

def get_all_companies(db):
    return db.query(Company).all()

def delete_company(db, company_id):
    comp = db.query(Company).filter(Company.id == company_id).first()
    if comp:
        db.delete(comp)
        db.commit()

def create_post(db, data: dict):
    # Standard Mode: Check duplicates to prevent spam
    existing = None
    if data.get('url'):
        existing = db.query(Post).filter(Post.url == data['url']).first()
    
    if not existing:
        post = Post(**data)
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
    return existing

def get_unanalysed_posts(db):
    return db.query(Post).filter(Post.analysed == False).order_by(Post.created_at.desc()).all()

def get_unanalysed_posts_by_brand(db, brand):
    return db.query(Post).filter(Post.analysed == False, Post.brand == brand).all()

def get_post_by_id(db, post_id):
    return db.query(Post).filter(Post.id == post_id).first()

def save_debunk(db, post_id, analysis_result):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        post.analysed = True
        
        debunk = Debunk(
            post_id=post_id,
            claim_text=analysis_result.get('claim', 'No Claim Extracted'),
            verdict=analysis_result.get('verdict', 'Unclear'),
            confidence=analysis_result.get('confidence', 0),
            explanation=analysis_result.get('explanation', ''),
            sources_json=json.dumps(analysis_result.get('sources', [])),
            pr_response=analysis_result.get('pr_response', '')
        )
        db.add(debunk)
        db.commit()
        db.refresh(debunk)
        return debunk
    return None

def mark_email_sent(db, debunk_id):
    debunk = db.query(Debunk).filter(Debunk.id == debunk_id).first()
    if debunk:
        debunk.email_sent = True
        db.commit()

def create_ledger_entry(db, debunk_id, current_hash, prev_hash):
    entry = LedgerEntry(
        debunk_id=debunk_id,
        hash=current_hash,
        prev_hash=prev_hash
    )
    db.add(entry)
    db.commit()
    return entry

def get_last_ledger_entry(db):
    return db.query(LedgerEntry).order_by(LedgerEntry.id.desc()).first()

def get_all_history(db):
    return db.query(Debunk).order_by(Debunk.created_at.desc()).all()

def get_debunk_by_post_id(db, post_id):
    return db.query(Debunk).filter(Debunk.post_id == post_id).first()

# =========================================================
# INCIDENT MODELS (NeuroChain v2)
# =========================================================

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Basic identification
    title = Column(String(512), nullable=False)
    source = Column(String(64), nullable=False)   # news / reddit / youtube / web
    risk_level = Column(String(16), nullable=False)
    risk_score = Column(Float, nullable=True)

    # Lifecycle
    status = Column(String(16), default=INCIDENT_STATUS_OPEN)

    opened_at = Column(DateTime, default=datetime.utcnow)
    alerted_at = Column(DateTime, nullable=True)
    response_drafted_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # AI response
    response_draft = Column(Text, nullable=True)

    # ---- lifecycle helpers ----

    def mark_alerted(self):
        if not self.alerted_at:
            self.alerted_at = datetime.utcnow()

    def mark_responded(self, response_text=None):
        if not self.response_drafted_at:
            self.response_drafted_at = datetime.utcnow()
        if response_text:
            self.response_draft = response_text
        self.status = INCIDENT_STATUS_RESPONDED

    def close_incident(self):
        self.status = INCIDENT_STATUS_CLOSED
        self.closed_at = datetime.utcnow()


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(Integer, nullable=False)

    event_type = Column(String(64), nullable=False)
    description = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
