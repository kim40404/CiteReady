"""HTML content parser for CiteReady.

Extracts structured metadata from raw HTML: headings, word count,
schema markup, links, images, dates, and more. This is the foundation
for the GEO scoring engine.
"""

from __future__ import annotations

import json
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Comment

from app.schemas.analysis import ContentMeta
from app.core.logging import get_logger

logger = get_logger(__name__)


def parse_html(html: str, source_url: str | None = None) -> ContentMeta:
    """Parse raw HTML into structured content metadata.

    Args:
        html: Raw HTML string.
        source_url: The URL the HTML was fetched from (for link classification).

    Returns:
        ContentMeta with all extracted metadata.
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # ── Title ────────────────────────────────────────────────────
    title = _extract_title(soup)

    # ── Meta Description ─────────────────────────────────────────
    meta_description = _extract_meta_description(soup)

    # ── Body Text ────────────────────────────────────────────────
    body_text = _extract_body_text(soup)
    word_count = len(body_text.split()) if body_text else 0

    # ── Paragraphs ───────────────────────────────────────────────
    paragraphs = soup.find_all("p")
    paragraph_count = len([p for p in paragraphs if len(p.get_text(strip=True)) > 20])

    # ── Headings ─────────────────────────────────────────────────
    headings, heading_counts = _extract_headings(soup)

    # ── Schema Markup ────────────────────────────────────────────
    has_schema, schema_types = _extract_schema_markup(soup)
    has_faq = "FAQPage" in schema_types
    has_howto = "HowTo" in schema_types

    # ── Links ────────────────────────────────────────────────────
    internal_links, external_links = _count_links(soup, source_url)

    # ── Images ───────────────────────────────────────────────────
    images_total, images_with_alt = _count_images(soup)

    # ── Publish Date ─────────────────────────────────────────────
    publish_date = _extract_publish_date(soup)

    meta = ContentMeta(
        title=title,
        meta_description=meta_description,
        word_count=word_count,
        paragraph_count=paragraph_count,
        heading_counts=heading_counts,
        headings=headings,
        has_schema_markup=has_schema,
        schema_types=schema_types,
        internal_links=internal_links,
        external_links=external_links,
        images_total=images_total,
        images_with_alt=images_with_alt,
        publish_date=publish_date,
        has_faq=has_faq,
        has_howto=has_howto,
    )

    logger.info(
        "parser.complete",
        word_count=word_count,
        headings_total=sum(heading_counts.values()),
        has_schema=has_schema,
    )

    return meta


def parse_plain_text(text: str) -> ContentMeta:
    """Parse plain text content (no HTML) into basic metadata.

    Args:
        text: Plain text content.

    Returns:
        ContentMeta with limited metadata (no HTML-specific features).
    """
    words = text.split()
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 20]

    # Try to detect headings from markdown-style formatting
    headings = []
    heading_counts = {"h1": 0, "h2": 0, "h3": 0, "h4": 0, "h5": 0, "h6": 0}

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            headings.append({"level": "h1", "text": line[2:]})
            heading_counts["h1"] += 1
        elif line.startswith("## "):
            headings.append({"level": "h2", "text": line[3:]})
            heading_counts["h2"] += 1
        elif line.startswith("### "):
            headings.append({"level": "h3", "text": line[4:]})
            heading_counts["h3"] += 1

    return ContentMeta(
        title=headings[0]["text"] if headings else None,
        word_count=len(words),
        paragraph_count=len(paragraphs),
        heading_counts=heading_counts,
        headings=headings,
    )


# ── Private Extraction Helpers ───────────────────────────────────


def _extract_title(soup: BeautifulSoup) -> str | None:
    """Extract the page title from <title> tag or <h1>."""
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        return title_tag.string.strip()

    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    return None


def _extract_meta_description(soup: BeautifulSoup) -> str | None:
    """Extract meta description from <meta name='description'>."""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return meta["content"].strip()

    # Also check og:description
    og_meta = soup.find("meta", attrs={"property": "og:description"})
    if og_meta and og_meta.get("content"):
        return og_meta["content"].strip()

    return None


def _extract_body_text(soup: BeautifulSoup) -> str:
    """Extract clean body text, stripping all tags."""
    body = soup.find("body")
    if body:
        return body.get_text(separator=" ", strip=True)
    return soup.get_text(separator=" ", strip=True)


def _extract_headings(soup: BeautifulSoup) -> tuple[list[dict], dict[str, int]]:
    """Extract all headings (H1-H6) with their levels and text."""
    headings = []
    counts = {"h1": 0, "h2": 0, "h3": 0, "h4": 0, "h5": 0, "h6": 0}

    for level in range(1, 7):
        tag_name = f"h{level}"
        for tag in soup.find_all(tag_name):
            text = tag.get_text(strip=True)
            if text:
                headings.append({"level": tag_name, "text": text})
                counts[tag_name] += 1

    return headings, counts


def _extract_schema_markup(soup: BeautifulSoup) -> tuple[bool, list[str]]:
    """Detect JSON-LD schema markup and extract @type values."""
    schema_types = []

    # Check for JSON-LD scripts
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
            if isinstance(data, dict):
                if "@type" in data:
                    schema_types.append(data["@type"])
                # Check @graph array
                if "@graph" in data and isinstance(data["@graph"], list):
                    for item in data["@graph"]:
                        if isinstance(item, dict) and "@type" in item:
                            schema_types.append(item["@type"])
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "@type" in item:
                        schema_types.append(item["@type"])
        except (json.JSONDecodeError, TypeError):
            continue

    # Also check microdata itemtype attributes
    for tag in soup.find_all(attrs={"itemtype": True}):
        itemtype = tag["itemtype"]
        if "schema.org" in itemtype:
            type_name = itemtype.rstrip("/").split("/")[-1]
            schema_types.append(type_name)

    has_schema = len(schema_types) > 0
    return has_schema, list(set(schema_types))


def _count_links(soup: BeautifulSoup, source_url: str | None) -> tuple[int, int]:
    """Count internal vs external links."""
    internal = 0
    external = 0

    source_domain = ""
    if source_url:
        parsed = urlparse(str(source_url))
        source_domain = parsed.netloc.lower()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        # Skip anchors, mailto, javascript
        if href.startswith(("#", "mailto:", "javascript:", "tel:")):
            continue

        if href.startswith("/") or href.startswith("./"):
            internal += 1
        elif source_domain and source_domain in href:
            internal += 1
        elif href.startswith("http"):
            external += 1

    return internal, external


def _count_images(soup: BeautifulSoup) -> tuple[int, int]:
    """Count total images and images with alt text."""
    images = soup.find_all("img")
    total = len(images)
    with_alt = sum(1 for img in images if img.get("alt", "").strip())

    return total, with_alt


def _extract_publish_date(soup: BeautifulSoup) -> str | None:
    """Try to extract publication date from various common patterns."""
    # Check <time> element
    time_tag = soup.find("time", attrs={"datetime": True})
    if time_tag:
        return time_tag["datetime"]

    # Check meta tags for dates
    date_metas = [
        ("property", "article:published_time"),
        ("name", "date"),
        ("name", "publish_date"),
        ("name", "publication_date"),
        ("property", "og:article:published_time"),
        ("name", "DC.date.issued"),
    ]

    for attr_name, attr_value in date_metas:
        meta = soup.find("meta", attrs={attr_name: attr_value})
        if meta and meta.get("content"):
            return meta["content"].strip()

    # Check JSON-LD for datePublished
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
            if isinstance(data, dict):
                if "datePublished" in data:
                    return data["datePublished"]
                if "@graph" in data and isinstance(data["@graph"], list):
                    for item in data["@graph"]:
                        if isinstance(item, dict) and "datePublished" in item:
                            return item["datePublished"]
        except (json.JSONDecodeError, TypeError):
            continue

    return None
