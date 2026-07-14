"""GEO Scoring Engine for CiteReady (Rule-Based Baseline).

Scores content on 5 categories that determine how "citable" it is
by AI search engines. This is the Phase 1 rule-based scorer;
Phase 2 will add LLM-powered analysis on top.

Scoring Categories:
    1. Entity Clarity    (20 pts) — Is the topic/brand clearly defined?
    2. Citation Readiness (25 pts) — Can AI engines easily cite this content?
    3. Content Structure  (20 pts) — Is the content well-organized?
    4. Freshness          (15 pts) — Is the content current and timely?
    5. Technical          (20 pts) — Is the page technically accessible?
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from app.core.config import settings
from app.schemas.analysis import CategoryScore, ContentMeta, Issue
from app.core.logging import get_logger

logger = get_logger(__name__)

ENGINE_VERSION = "0.1.0"


def calculate_geo_score(
    meta: ContentMeta,
    keywords: list[str] | None = None,
) -> tuple[float, str, list[CategoryScore], list[Issue], list[str]]:
    """Calculate the GEO score for analyzed content.

    Args:
        meta: Parsed content metadata from the parser.
        keywords: Optional target keywords to check for.

    Returns:
        Tuple of (total_score, grade, category_scores, issues, priority_actions).
    """
    all_issues: list[Issue] = []

    # ── Score each category ──────────────────────────────────────
    entity_score = _score_entity_clarity(meta, keywords, all_issues)
    citation_score = _score_citation_readiness(meta, all_issues)
    structure_score = _score_content_structure(meta, all_issues)
    freshness_score = _score_freshness(meta, all_issues)
    technical_score = _score_technical(meta, all_issues)

    # ── Build category list ──────────────────────────────────────
    categories = [entity_score, citation_score, structure_score, freshness_score, technical_score]

    # ── Calculate weighted total ─────────────────────────────────
    total_score = sum(cat.score * cat.weight for cat in categories)
    total_score = round(min(100.0, max(0.0, total_score)), 1)

    # ── Grade ────────────────────────────────────────────────────
    grade = _calculate_grade(total_score)

    # ── Sort issues by severity ──────────────────────────────────
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    all_issues.sort(key=lambda i: severity_order.get(i.severity, 99))

    # ── Priority actions (top 5 from critical/warning issues) ────
    priority_actions = [
        issue.recommendation
        for issue in all_issues
        if issue.severity in ("critical", "warning")
    ][:5]

    if not priority_actions:
        priority_actions = ["Content looks good! Consider adding more structured data for bonus points."]

    logger.info(
        "scorer.complete",
        geo_score=total_score,
        grade=grade,
        issues_count=len(all_issues),
        entity=entity_score.score,
        citation=citation_score.score,
        structure=structure_score.score,
        freshness=freshness_score.score,
        technical=technical_score.score,
    )

    return total_score, grade, categories, all_issues, priority_actions


# ── Category 1: Entity Clarity (max 100, weight 0.20) ────────────


def _score_entity_clarity(
    meta: ContentMeta,
    keywords: list[str] | None,
    issues: list[Issue],
) -> CategoryScore:
    """Score how clearly the content defines its topic/entity."""
    score = 0.0
    max_score = 100.0
    details = []

    # Has title? (+25)
    if meta.title:
        score += 25
        details.append(f"✅ Title found: '{meta.title[:60]}...'")
    else:
        issues.append(Issue(
            severity="critical",
            category="Entity Clarity",
            message="No page title found.",
            recommendation="Add a descriptive <title> tag that clearly states the topic.",
        ))

    # Has meta description? (+20)
    if meta.meta_description:
        score += 20
        if len(meta.meta_description) >= 120:
            score += 5
            details.append("✅ Meta description is well-written (120+ chars).")
        else:
            details.append(f"⚠️ Meta description is short ({len(meta.meta_description)} chars).")
            issues.append(Issue(
                severity="warning",
                category="Entity Clarity",
                message=f"Meta description is only {len(meta.meta_description)} characters.",
                recommendation="Expand meta description to 120-160 characters for better AI context.",
            ))
    else:
        issues.append(Issue(
            severity="critical",
            category="Entity Clarity",
            message="No meta description found.",
            recommendation="Add a <meta name='description'> that summarizes the page in 120-160 characters.",
        ))

    # Has H1? (+25)
    h1_count = meta.heading_counts.get("h1", 0)
    if h1_count == 1:
        score += 25
        details.append("✅ Exactly one H1 tag found (ideal).")
    elif h1_count > 1:
        score += 15
        issues.append(Issue(
            severity="warning",
            category="Entity Clarity",
            message=f"Multiple H1 tags found ({h1_count}). Should be exactly one.",
            recommendation="Use a single H1 for the main topic; demote extras to H2.",
        ))
    else:
        issues.append(Issue(
            severity="critical",
            category="Entity Clarity",
            message="No H1 heading found.",
            recommendation="Add one H1 heading that clearly states the page's main topic.",
        ))

    # Keyword presence in title/H1 (+25)
    if keywords:
        title_text = (meta.title or "").lower()
        h1_texts = " ".join(
            h["text"] for h in meta.headings if h["level"] == "h1"
        ).lower()
        combined = title_text + " " + h1_texts

        matched = [kw for kw in keywords if kw.lower() in combined]
        if matched:
            score += 25
            details.append(f"✅ Keywords found in title/H1: {matched}")
        else:
            score += 5
            issues.append(Issue(
                severity="warning",
                category="Entity Clarity",
                message=f"Target keywords not found in title or H1: {keywords}",
                recommendation="Include your primary keyword in both the title tag and H1 heading.",
            ))
    else:
        # No keywords provided — give partial credit
        score += 15
        details.append("ℹ️ No target keywords provided; partial credit given.")

    return CategoryScore(
        name="Entity Clarity",
        score=round(score, 1),
        max_score=max_score,
        weight=0.20,
        details=details,
    )


# ── Category 2: Citation Readiness (max 100, weight 0.25) ────────


def _score_citation_readiness(
    meta: ContentMeta,
    issues: list[Issue],
) -> CategoryScore:
    """Score how easily AI engines can cite this content."""
    score = 0.0
    max_score = 100.0
    details = []

    body_text = ""  # We reconstruct from available meta
    word_count = meta.word_count

    # Has sufficient content depth? (+20)
    if word_count >= settings.IDEAL_WORD_COUNT:
        score += 20
        details.append(f"✅ Content depth is excellent ({word_count} words).")
    elif word_count >= settings.MIN_WORD_COUNT:
        ratio = (word_count - settings.MIN_WORD_COUNT) / (settings.IDEAL_WORD_COUNT - settings.MIN_WORD_COUNT)
        score += 10 + (10 * ratio)
        details.append(f"⚠️ Content is adequate ({word_count} words) but could be deeper.")
        issues.append(Issue(
            severity="info",
            category="Citation Readiness",
            message=f"Content has {word_count} words. Ideal is {settings.IDEAL_WORD_COUNT}+.",
            recommendation=f"Consider expanding content to {settings.IDEAL_WORD_COUNT}+ words for better topical coverage.",
        ))
    else:
        score += 5
        issues.append(Issue(
            severity="warning",
            category="Citation Readiness",
            message=f"Content is thin ({word_count} words). Minimum recommended: {settings.MIN_WORD_COUNT}.",
            recommendation=f"Expand content to at least {settings.MIN_WORD_COUNT} words with substantive information.",
        ))

    # Has FAQ schema? (+20)
    if meta.has_faq:
        score += 20
        details.append("✅ FAQ schema detected — excellent for AI citation.")
    else:
        score += 0
        issues.append(Issue(
            severity="info",
            category="Citation Readiness",
            message="No FAQ schema markup found.",
            recommendation="Add FAQPage schema markup to help AI engines extract Q&A pairs from your content.",
        ))

    # Has HowTo schema? (+10)
    if meta.has_howto:
        score += 10
        details.append("✅ HowTo schema detected — great for instructional citations.")

    # Has multiple headings (indicates structured answers)? (+20)
    total_subheadings = sum(
        meta.heading_counts.get(f"h{i}", 0) for i in range(2, 5)
    )
    if total_subheadings >= 5:
        score += 20
        details.append(f"✅ Well-structured with {total_subheadings} subheadings (H2-H4).")
    elif total_subheadings >= 3:
        score += 12
        details.append(f"⚠️ {total_subheadings} subheadings found. 5+ recommended.")
    else:
        score += 5
        issues.append(Issue(
            severity="warning",
            category="Citation Readiness",
            message=f"Only {total_subheadings} subheadings (H2-H4). Content may appear unstructured to AI.",
            recommendation="Break content into 5+ sections with clear H2/H3 headings that answer specific questions.",
        ))

    # Has external links (credibility signals)? (+15)
    if meta.external_links >= 3:
        score += 15
        details.append(f"✅ {meta.external_links} external links — good credibility signals.")
    elif meta.external_links >= 1:
        score += 8
        details.append(f"⚠️ Only {meta.external_links} external link(s). More sources = more credible.")
    else:
        issues.append(Issue(
            severity="info",
            category="Citation Readiness",
            message="No external links found.",
            recommendation="Add 3+ outbound links to authoritative sources to boost credibility signals.",
        ))

    # Paragraph density (not too long, not too short) (+15)
    if meta.paragraph_count > 0:
        avg_words_per_para = word_count / meta.paragraph_count
        if 40 <= avg_words_per_para <= 150:
            score += 15
            details.append("✅ Good paragraph density for readability.")
        elif avg_words_per_para < 40:
            score += 8
            details.append("⚠️ Paragraphs may be too short; consider expanding.")
        else:
            score += 5
            issues.append(Issue(
                severity="info",
                category="Citation Readiness",
                message="Paragraphs are very long. AI prefers digestible content blocks.",
                recommendation="Break long paragraphs into 2-3 sentence blocks for better AI parsing.",
            ))

    return CategoryScore(
        name="Citation Readiness",
        score=round(min(score, max_score), 1),
        max_score=max_score,
        weight=0.25,
        details=details,
    )


# ── Category 3: Content Structure (max 100, weight 0.20) ─────────


def _score_content_structure(
    meta: ContentMeta,
    issues: list[Issue],
) -> CategoryScore:
    """Score how well the content is organized."""
    score = 0.0
    max_score = 100.0
    details = []

    # Heading hierarchy check (+30)
    h1 = meta.heading_counts.get("h1", 0)
    h2 = meta.heading_counts.get("h2", 0)
    h3 = meta.heading_counts.get("h3", 0)

    if h1 >= 1 and h2 >= 2:
        score += 30
        details.append(f"✅ Good heading hierarchy: H1={h1}, H2={h2}, H3={h3}.")
    elif h1 >= 1 and h2 >= 1:
        score += 20
        details.append("⚠️ Basic heading structure present but could be richer.")
    else:
        score += 5
        issues.append(Issue(
            severity="warning",
            category="Content Structure",
            message="Weak heading hierarchy. AI engines rely on headings to understand content structure.",
            recommendation="Use H1 for the main topic, H2 for sections, H3 for subsections.",
        ))

    # Content length adequacy (+25)
    if meta.word_count >= settings.IDEAL_WORD_COUNT:
        score += 25
        details.append(f"✅ Content length ({meta.word_count} words) exceeds ideal threshold.")
    elif meta.word_count >= settings.MIN_WORD_COUNT:
        ratio = meta.word_count / settings.IDEAL_WORD_COUNT
        score += 25 * ratio
    else:
        score += 5
        issues.append(Issue(
            severity="critical",
            category="Content Structure",
            message=f"Content is too short ({meta.word_count} words).",
            recommendation=f"Expand to at least {settings.MIN_WORD_COUNT} words for meaningful analysis.",
        ))

    # Has images with alt text? (+20)
    if meta.images_total > 0:
        alt_ratio = meta.images_with_alt / meta.images_total if meta.images_total > 0 else 0
        if alt_ratio >= 0.8:
            score += 20
            details.append(f"✅ {meta.images_with_alt}/{meta.images_total} images have alt text.")
        elif alt_ratio >= 0.5:
            score += 12
            issues.append(Issue(
                severity="warning",
                category="Content Structure",
                message=f"Only {meta.images_with_alt}/{meta.images_total} images have alt text.",
                recommendation="Add descriptive alt text to all images for accessibility and AI understanding.",
            ))
        else:
            score += 5
            issues.append(Issue(
                severity="warning",
                category="Content Structure",
                message="Most images lack alt text.",
                recommendation="Add descriptive alt text to every image.",
            ))
    else:
        score += 10  # No images is neutral, not penalized
        details.append("ℹ️ No images found. Consider adding visuals to enrich content.")

    # Internal linking (+25)
    if meta.internal_links >= 5:
        score += 25
        details.append(f"✅ Strong internal linking ({meta.internal_links} links).")
    elif meta.internal_links >= 2:
        score += 15
        details.append(f"⚠️ Some internal links ({meta.internal_links}). 5+ recommended.")
    else:
        score += 5
        issues.append(Issue(
            severity="info",
            category="Content Structure",
            message=f"Weak internal linking ({meta.internal_links} links).",
            recommendation="Add 5+ internal links to related content to strengthen site topology signals.",
        ))

    return CategoryScore(
        name="Content Structure",
        score=round(min(score, max_score), 1),
        max_score=max_score,
        weight=0.20,
        details=details,
    )


# ── Category 4: Freshness & Relevance (max 100, weight 0.15) ────


def _score_freshness(
    meta: ContentMeta,
    issues: list[Issue],
) -> CategoryScore:
    """Score content freshness and timeliness."""
    score = 0.0
    max_score = 100.0
    details = []

    # Has publish date? (+40)
    if meta.publish_date:
        score += 25
        details.append(f"✅ Publication date found: {meta.publish_date}")

        # How recent is it?
        try:
            # Try to parse common date formats
            date_str = meta.publish_date[:10]  # Take YYYY-MM-DD portion
            pub_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)
            days_old = (now - pub_date).days

            if days_old <= 90:
                score += 25
                details.append(f"✅ Content is fresh ({days_old} days old).")
            elif days_old <= 365:
                score += 15
                details.append(f"⚠️ Content is {days_old} days old. Consider updating.")
            else:
                score += 5
                issues.append(Issue(
                    severity="warning",
                    category="Freshness",
                    message=f"Content is {days_old} days old (over a year).",
                    recommendation="Update the content and publication date to signal freshness to AI engines.",
                ))
        except (ValueError, TypeError):
            score += 10  # Date exists but can't parse — partial credit
            details.append("⚠️ Date found but format could not be fully parsed.")
    else:
        issues.append(Issue(
            severity="warning",
            category="Freshness",
            message="No publication or last-updated date found.",
            recommendation="Add a visible publication date and/or datePublished in schema markup.",
        ))

    # Check for current year mention in headings (+20)
    current_year = str(datetime.now().year)
    headings_text = " ".join(h["text"] for h in meta.headings).lower()
    title_text = (meta.title or "").lower()

    if current_year in headings_text or current_year in title_text:
        score += 20
        details.append(f"✅ Current year ({current_year}) mentioned in headings/title.")
    else:
        score += 5
        details.append(f"ℹ️ No mention of current year ({current_year}) in headings.")

    # Has schema type Article/BlogPosting/NewsArticle? (+15)
    article_types = {"Article", "BlogPosting", "NewsArticle", "TechArticle", "WebPage"}
    if any(st in article_types for st in meta.schema_types):
        score += 15
        details.append("✅ Article-type schema found — helps AI understand content type.")
    else:
        score += 0
        issues.append(Issue(
            severity="info",
            category="Freshness",
            message="No Article/BlogPosting schema type found.",
            recommendation="Add Article or BlogPosting schema with datePublished and dateModified.",
        ))

    return CategoryScore(
        name="Freshness & Relevance",
        score=round(min(score, max_score), 1),
        max_score=max_score,
        weight=0.15,
        details=details,
    )


# ── Category 5: Technical Accessibility (max 100, weight 0.20) ───


def _score_technical(
    meta: ContentMeta,
    issues: list[Issue],
) -> CategoryScore:
    """Score technical accessibility for AI crawlers."""
    score = 0.0
    max_score = 100.0
    details = []

    # Has any schema markup? (+30)
    if meta.has_schema_markup:
        score += 30
        details.append(f"✅ Schema markup detected: {meta.schema_types}")
    else:
        issues.append(Issue(
            severity="warning",
            category="Technical",
            message="No structured data (schema markup) found.",
            recommendation="Add JSON-LD schema markup (Article, FAQPage, or HowTo) for better AI understanding.",
        ))

    # Has meta description (technical presence check)? (+15)
    if meta.meta_description:
        score += 15
        details.append("✅ Meta description present for search engine snippets.")
    else:
        score += 0

    # Title length check (+15)
    if meta.title:
        title_len = len(meta.title)
        if 30 <= title_len <= 70:
            score += 15
            details.append(f"✅ Title length is optimal ({title_len} chars).")
        elif title_len > 70:
            score += 8
            issues.append(Issue(
                severity="info",
                category="Technical",
                message=f"Title is long ({title_len} chars). May be truncated in search results.",
                recommendation="Shorten title to 50-60 characters for optimal display.",
            ))
        else:
            score += 8
            details.append(f"⚠️ Title is short ({title_len} chars).")

    # Image optimization (+20)
    if meta.images_total > 0:
        alt_ratio = meta.images_with_alt / meta.images_total
        score += 20 * alt_ratio
        if alt_ratio >= 0.8:
            details.append("✅ Good image accessibility (alt text coverage).")
    else:
        score += 10  # Neutral — no images isn't a penalty
        details.append("ℹ️ No images to evaluate.")

    # Content-to-heading ratio (+20)
    total_headings = sum(meta.heading_counts.values())
    if total_headings > 0 and meta.word_count > 0:
        words_per_heading = meta.word_count / total_headings
        if 100 <= words_per_heading <= 400:
            score += 20
            details.append(f"✅ Good content density ({int(words_per_heading)} words per section).")
        elif words_per_heading < 100:
            score += 12
            details.append("⚠️ Sections may be too short.")
        else:
            score += 10
            issues.append(Issue(
                severity="info",
                category="Technical",
                message="Sections are very long. Consider breaking them up.",
                recommendation="Aim for 150-300 words per section with clear headings.",
            ))
    else:
        score += 5

    return CategoryScore(
        name="Technical Accessibility",
        score=round(min(score, max_score), 1),
        max_score=max_score,
        weight=0.20,
        details=details,
    )


# ── Helpers ──────────────────────────────────────────────────────


def _calculate_grade(score: float) -> str:
    """Convert a 0-100 score to a letter grade."""
    if score >= 80:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 40:
        return "C"
    elif score >= 20:
        return "D"
    else:
        return "F"
