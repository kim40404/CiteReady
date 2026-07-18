"""CiteReady API routes.

Provides endpoints for content analysis, history lookup, and health checks.
Every request gets a unique trace_id for full audit trail support.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.api.deps import get_session
from app.models.analysis import AnalysisRecord
from app.schemas.analysis import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnalysisListItem,
    AnalysisListResponse,
)
from app.services.parser import parse_html, parse_plain_text
from app.services.scorer import calculate_geo_score, ENGINE_VERSION
from app.services.scraper import ScraperError, fetch_url
from app.services.llm_analyzer import analyze_semantics
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Analysis"])


# ── POST /analyze ────────────────────────────────────────────────


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze content for AI Search Visibility",
    description=(
        "Submit a URL or plain text to get a GEO (Generative Engine Optimization) score. "
        "The engine evaluates Entity Clarity, Citation Readiness, Content Structure, "
        "Freshness, and Technical Accessibility."
    ),
)
async def analyze_content(
    request: AnalyzeRequest,
    session: AsyncSession = Depends(get_session),
) -> AnalyzeResponse:
    """Main analysis endpoint — the core of CiteReady."""

    # Generate unique trace ID for this request
    trace_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    # Bind trace_id to all logs in this request context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(trace_id=trace_id)

    logger.info("analyze.start", url=str(request.url), has_text=bool(request.text))

    # ── Validate input ───────────────────────────────────────────
    if not request.url and not request.text:
        raise HTTPException(
            status_code=422,
            detail="Either 'url' or 'text' must be provided.",
        )

    # ── Fetch & Parse ────────────────────────────────────────────
    url_str = str(request.url) if request.url else None

    try:
        if request.url:
            html = await fetch_url(url_str)
            content_meta = parse_html(html, source_url=url_str)
        else:
            content_meta = parse_plain_text(request.text)
    except ScraperError as e:
        logger.error("analyze.scraper_failed", error=e.message)
        raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {e.message}")
    except Exception as e:
        logger.error("analyze.parse_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to parse content: {str(e)}")

    # ── Semantic LLM Analysis (Phase 2) ──────────────────────────
    try:
        semantic_result = await analyze_semantics(content_meta, raw_text=request.text)
    except Exception as e:
        logger.error("analyze.llm_failed", error=str(e))
        semantic_result = None

    # ── Score ────────────────────────────────────────────────────
    try:
        geo_score, grade, scores, issues, priority_actions = calculate_geo_score(
            meta=content_meta,
            semantic_result=semantic_result,
            keywords=request.keywords or None,
        )
    except Exception as e:
        logger.error("analyze.scoring_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Scoring engine error: {str(e)}")

    # ── Calculate latency ────────────────────────────────────────
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    # ── Build response ───────────────────────────────────────────
    analyzed_at = datetime.now(timezone.utc)

    response = AnalyzeResponse(
        trace_id=trace_id,
        url=url_str,
        geo_score=geo_score,
        semantic_score=semantic_result.total_semantic_score if semantic_result else 0.0,
        grade=grade,
        scores=scores,
        content_meta=content_meta,
        issues=issues,
        ai_insights=semantic_result.insights if semantic_result else [],
        priority_actions=priority_actions,
        analyzed_at=analyzed_at,
        latency_ms=latency_ms,
        engine_version=ENGINE_VERSION,
    )

    # ── Persist to database (audit trail) ────────────────────────
    try:
        record = AnalysisRecord(
            trace_id=trace_id,
            url=url_str,
            geo_score=geo_score,
            grade=grade,
            word_count=content_meta.word_count,
            latency_ms=latency_ms,
            engine_version=ENGINE_VERSION,
            created_at=analyzed_at,
        )
        record.set_json_field("scores_breakdown", [s.model_dump() for s in scores])
        record.set_json_field("issues", [i.model_dump() for i in issues])
        record.set_json_field("priority_actions", priority_actions)
        record.set_json_field("content_meta", content_meta.model_dump())
        if semantic_result:
            record.set_json_field("ai_insights", semantic_result.insights)

        session.add(record)
        await session.commit()

        logger.info(
            "analyze.complete",
            geo_score=geo_score,
            grade=grade,
            latency_ms=latency_ms,
            word_count=content_meta.word_count,
        )
    except Exception as e:
        logger.error("analyze.db_save_failed", error=str(e))
        # Don't fail the request if DB save fails — return the analysis anyway
        await session.rollback()

    return response


# ── GET /analyses ────────────────────────────────────────────────


@router.get(
    "/analyses",
    response_model=AnalysisListResponse,
    summary="List past analyses",
    description="Retrieve a paginated list of all past content analyses.",
)
async def list_analyses(
    limit: int = Query(default=20, ge=1, le=100, description="Max results to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    session: AsyncSession = Depends(get_session),
) -> AnalysisListResponse:
    """List past analyses with pagination."""

    # Count total
    count_result = await session.execute(
        select(AnalysisRecord.id)
    )
    total = len(count_result.all())

    # Fetch paginated results
    result = await session.execute(
        select(AnalysisRecord)
        .order_by(AnalysisRecord.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    records = result.scalars().all()

    analyses = [
        AnalysisListItem(
            trace_id=r.trace_id,
            url=r.url,
            geo_score=r.geo_score,
            grade=r.grade,
            analyzed_at=r.created_at,
        )
        for r in records
    ]

    return AnalysisListResponse(total=total, analyses=analyses)


# ── GET /analyses/{trace_id} ─────────────────────────────────────


@router.get(
    "/analyses/{trace_id}",
    response_model=AnalyzeResponse,
    summary="Get analysis by trace ID",
    description="Retrieve the full analysis result for a specific trace ID (audit lookup).",
)
async def get_analysis(
    trace_id: str,
    session: AsyncSession = Depends(get_session),
) -> AnalyzeResponse:
    """Retrieve a specific analysis by trace ID."""

    result = await session.execute(
        select(AnalysisRecord).where(AnalysisRecord.trace_id == trace_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail=f"Analysis with trace_id '{trace_id}' not found.")

    # Reconstruct response from stored record
    from app.schemas.analysis import CategoryScore, ContentMeta, Issue

    scores_data = record.get_json_field("scores_breakdown") or []
    issues_data = record.get_json_field("issues") or []
    content_data = record.get_json_field("content_meta") or {}
    priority_data = record.get_json_field("priority_actions") or []

    return AnalyzeResponse(
        trace_id=record.trace_id,
        url=record.url,
        geo_score=record.geo_score,
        grade=record.grade,
        scores=[CategoryScore(**s) for s in scores_data],
        content_meta=ContentMeta(**content_data),
        issues=[Issue(**i) for i in issues_data],
        priority_actions=priority_data,
        analyzed_at=record.created_at,
        latency_ms=record.latency_ms,
        engine_version=record.engine_version,
    )
