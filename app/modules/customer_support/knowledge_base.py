import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.email_support import KnowledgeArticle
from app.config import logger

DEFAULT_KNOWLEDGE_ARTICLES = [
    {
        "slug": "billing-cycles-and-invoicing",
        "category": "BILLING",
        "title": "Enterprise Invoicing Cycles and Payment Schedules",
        "content": (
            "Enterprise invoices are generated automatically on the 1st of each calendar month. "
            "Payments are processed through Stripe via credit card or ACH transfer. Receipts are "
            "emailed immediately following successful charge verification. For payment discrepancies "
            "or wire instructions, contact accounts-receivable@enterprise.com."
        ),
        "tags": ["billing", "invoice", "payment", "stripe", "cycle", "receipt"]
    },
    {
        "slug": "refund-and-cancellation-policy",
        "category": "BILLING",
        "title": "Corporate Refund and Cancellation Policy",
        "content": (
            "All refund requests must undergo mandatory review by our finance operations department. "
            "Refunds for unused monthly subscriptions can be requested within 14 days of invoice issue date. "
            "AI agents and automated systems are strictly prohibited from issuing or committing to financial refunds."
        ),
        "tags": ["refund", "cancel", "dispute", "credit", "reversal"]
    },
    {
        "slug": "api-rate-limits-and-integration",
        "category": "TECHNICAL",
        "title": "API Gateway Authentication and Rate Limits",
        "content": (
            "All REST API requests require Bearer token authentication in the Authorization header. "
            "Standard accounts are limited to 120 requests/minute; Enterprise tier accounts are allocated "
            "1,200 requests/minute. Webhooks retry with exponential backoff up to 5 attempts over 24 hours."
        ),
        "tags": ["api", "rate limit", "token", "auth", "webhook", "error", "technical"]
    },
    {
        "slug": "account-access-and-2fa",
        "category": "ACCOUNT_ACCESS",
        "title": "Account Recovery and Multi-Factor Authentication",
        "content": (
            "To reset your account password, navigate to /auth/forgot-password and provide your registered "
            "corporate email. Multi-Factor Authentication (2FA) is enforced across all enterprise workspaces. "
            "To transfer workspace ownership or re-issue backup codes, a verified admin ticket is required."
        ),
        "tags": ["account", "password", "reset", "2fa", "login", "locked", "access"]
    },
    {
        "slug": "critical-sla-and-incident-management",
        "category": "URGENT_INCIDENT",
        "title": "Sev-1 Incident Escalation and SLA Policy",
        "content": (
            "Our enterprise SLA guarantees 99.9% operational uptime. Sev-1 Critical Incidents (production "
            "system outage, data pipeline halt) are immediately paged to on-call engineering with a 15-minute "
            "target response time. Status updates are posted live to status.enterprise-platform.com."
        ),
        "tags": ["urgent", "sla", "outage", "down", "incident", "critical", "sev-1"]
    }
]

class KnowledgeBaseRetriever:
    """Retrieval-Augmented Generation (RAG) retriever for enterprise support."""

    @staticmethod
    def seed_articles(db: Session):
        """Seed default approved knowledge base articles into the database if not present."""
        for item in DEFAULT_KNOWLEDGE_ARTICLES:
            existing = db.query(KnowledgeArticle).filter(KnowledgeArticle.slug == item["slug"]).first()
            if not existing:
                art = KnowledgeArticle(
                    slug=item["slug"],
                    category=item["category"],
                    title=item["title"],
                    content=item["content"],
                    tags=item["tags"],
                    approved=True
                )
                db.add(art)
        db.commit()

    @staticmethod
    def retrieve_relevant_passages(db: Session, query_text: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Retrieve top-k approved knowledge base passages matching query text."""
        # Query tokens
        query_words = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", query_text.lower()))
        if not query_words:
            return []

        articles = db.query(KnowledgeArticle).filter(KnowledgeArticle.approved == True).all()
        scored_articles = []

        for art in articles:
            text = f"{art.title} {art.content} {' '.join(art.tags or [])}".lower()
            art_words = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", text))

            overlap = query_words.intersection(art_words)
            if overlap:
                score = len(overlap) / (len(query_words) + 1)
                scored_articles.append({
                    "score": round(score, 3),
                    "slug": art.slug,
                    "title": art.title,
                    "category": art.category,
                    "content": art.content,
                    "overlap_terms": list(overlap)
                })

        # Sort by relevance score descending
        scored_articles.sort(key=lambda x: x["score"], reverse=True)
        return scored_articles[:top_k]

kb_retriever = KnowledgeBaseRetriever()
