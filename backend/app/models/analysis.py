"""SQLAlchemy database models for CiteReady."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.core.database import Base


class AnalysisRecord(Base):
    """Stores the result of every content analysis for audit trail.

    Every request to /analyze creates one row here. This enables:
    - Full audit trail (who analyzed what, when)
    - Historical tracking (score changes over time for same URL)
    - Debugging via trace_id lookup
    """

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(36), unique=True, nullable=False, index=True)
    url = Column(String(2048), nullable=True)
    geo_score = Column(Float, nullable=False)
    grade = Column(String(2), nullable=False)
    scores_breakdown = Column(Text, nullable=False, doc="JSON string of per-category scores")
    issues = Column(Text, nullable=False, doc="JSON string of issues list")
    priority_actions = Column(Text, nullable=False, doc="JSON string of top actions")
    content_meta = Column(Text, nullable=False, doc="JSON string of content metadata")
    word_count = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    engine_version = Column(String(20), default="0.1.0")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def set_json_field(self, field_name: str, data: object) -> None:
        """Serialize a Python object to JSON and store it."""
        setattr(self, field_name, json.dumps(data, default=str))

    def get_json_field(self, field_name: str) -> object:
        """Deserialize a JSON field back to a Python object."""
        raw = getattr(self, field_name)
        return json.loads(raw) if raw else None
