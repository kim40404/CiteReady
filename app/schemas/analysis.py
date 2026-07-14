"""Pydantic schemas for CiteReady API request/response validation.

These schemas define the contract between the API and its consumers.
Every field is typed and documented for auto-generated Swagger docs.
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


# ── Request Schemas ──────────────────────────────────────────────


class AnalyzeRequest(BaseModel):
    """Input for the /analyze endpoint."""

    url: HttpUrl | None = Field(
        default=None,
        description="URL of the article/page to analyze.",
        json_schema_extra={"example": "https://example.com/blog/ai-search-2026"},
    )
    text: str | None = Field(
        default=None,
        description="Plain text content to analyze (use this if URL is not available).",
        min_length=50,
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="Optional target keywords to check coverage for.",
        json_schema_extra={"example": ["AI search", "GEO optimization"]},
    )


# ── Score Detail Schemas ─────────────────────────────────────────


class CategoryScore(BaseModel):
    """Score detail for a single GEO category."""

    name: str = Field(description="Category name (e.g., 'Entity Clarity').")
    score: float = Field(ge=0, le=100, description="Score for this category (0-100).")
    max_score: float = Field(description="Maximum possible score for this category.")
    weight: float = Field(description="Weight of this category in total score (0-1).")
    details: list[str] = Field(
        default_factory=list,
        description="Specific findings for this category.",
    )


class Issue(BaseModel):
    """A specific issue found during analysis."""

    severity: str = Field(description="Issue severity: critical, warning, or info.")
    category: str = Field(description="Which scoring category this issue belongs to.")
    message: str = Field(description="Human-readable description of the issue.")
    recommendation: str = Field(description="Actionable fix suggestion.")


# ── Content Metadata ─────────────────────────────────────────────


class ContentMeta(BaseModel):
    """Extracted metadata from the analyzed content."""

    title: str | None = None
    meta_description: str | None = None
    word_count: int = 0
    paragraph_count: int = 0
    heading_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Count of each heading level: {'h1': 1, 'h2': 3, ...}",
    )
    headings: list[dict[str, str]] = Field(
        default_factory=list,
        description="List of headings with level and text: [{'level': 'h1', 'text': '...'}]",
    )
    has_schema_markup: bool = False
    schema_types: list[str] = Field(
        default_factory=list,
        description="Schema.org types found (e.g., 'FAQPage', 'HowTo').",
    )
    internal_links: int = 0
    external_links: int = 0
    images_total: int = 0
    images_with_alt: int = 0
    publish_date: str | None = None
    has_faq: bool = False
    has_howto: bool = False


# ── Response Schemas ─────────────────────────────────────────────


class AnalyzeResponse(BaseModel):
    """Full output from the /analyze endpoint."""

    # Identification
    trace_id: str = Field(description="Unique trace ID for this analysis (for audit).")
    url: str | None = Field(description="The URL that was analyzed.")

    # Scores
    geo_score: float = Field(
        ge=0, le=100, description="Overall GEO score (0-100)."
    )
    grade: str = Field(
        description="Letter grade: A (80+), B (60-79), C (40-59), D (20-39), F (<20)."
    )
    scores: list[CategoryScore] = Field(
        description="Per-category score breakdown."
    )

    # Content Analysis
    content_meta: ContentMeta = Field(description="Extracted content metadata.")

    # Issues & Recommendations
    issues: list[Issue] = Field(
        description="List of issues found, ordered by severity."
    )
    priority_actions: list[str] = Field(
        description="Top 5 prioritized actions to improve the score."
    )

    # Audit
    analyzed_at: datetime = Field(description="Timestamp of analysis.")
    latency_ms: int = Field(description="Processing time in milliseconds.")
    engine_version: str = Field(description="Scoring engine version.")


class AnalysisListItem(BaseModel):
    """Summary item for listing past analyses."""

    trace_id: str
    url: str | None
    geo_score: float
    grade: str
    analyzed_at: datetime


class AnalysisListResponse(BaseModel):
    """Response for listing analyses."""

    total: int
    analyses: list[AnalysisListItem]
