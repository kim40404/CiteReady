"""LLM Semantic Analyzer for CiteReady.

Uses LiteLLM to connect to local Ollama models (or OpenAI/Anthropic).
Analyzes the semantic meaning, authority, and fact density of the content.
"""

from __future__ import annotations

import json
from litellm import acompletion
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger
from app.core.prompts import SEMANTIC_EVAL_PROMPT
from app.schemas.analysis import ContentMeta, SemanticAnalysisResult

logger = get_logger(__name__)




@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=10))
async def analyze_semantics(
    content_meta: ContentMeta,
    raw_text: str | None = None
) -> SemanticAnalysisResult:
    """Send content to LLM for semantic evaluation."""

    logger.info("llm.start_analysis", model=settings.LLM_MODEL)

    # We use raw_text if provided, otherwise reconstruct from meta
    content_to_analyze = raw_text
    if not content_to_analyze:
        # Fallback to headings and metadata if raw text is missing
        headings = "\\n".join([f"{h['level'].upper()}: {h['text']}" for h in content_meta.headings])
        content_to_analyze = f"Title: {content_meta.title}\\nDesc: {content_meta.meta_description}\\n\\nStructure:\\n{headings}"
    
    # Truncate to avoid blowing up local LLM context limits (roughly ~3000 words max for safety)
    words = content_to_analyze.split()
    if len(words) > 2500:
        content_to_analyze = " ".join(words[:2500]) + "... [TRUNCATED]"

    try:
        # Dynamically configure LiteLLM based on provider
        kwargs = {
            "model": settings.LLM_MODEL,
            "messages": [
                {"role": "system", "content": SEMANTIC_EVAL_PROMPT},
                {"role": "user", "content": f"Analyze this content:\n\n{content_to_analyze}"}
            ],
            "response_format": {"type": "json_object"},
            "timeout": settings.LLM_TIMEOUT,
        }

        if settings.LLM_PROVIDER == "ollama":
            kwargs["api_base"] = settings.LLM_BASE_URL
        elif settings.LLM_API_KEY:
            kwargs["api_key"] = settings.LLM_API_KEY
            if settings.LLM_BASE_URL:
                kwargs["api_base"] = settings.LLM_BASE_URL

        response = await acompletion(**kwargs)

        # Parse JSON response
        result_text = response.choices[0].message.content
        logger.debug("llm.raw_response", raw=result_text)
        
        # Clean up in case LLM added markdown despite instructions
        result_text = result_text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]

        parsed = json.loads(result_text.strip())
        
        result = SemanticAnalysisResult(
            reasoning_authority=parsed.get("reasoning_authority", ""),
            authority_score=float(parsed.get("authority_score", 50.0)),
            reasoning_fact_density=parsed.get("reasoning_fact_density", ""),
            fact_density_score=float(parsed.get("fact_density_score", 50.0)),
            reasoning_clarity=parsed.get("reasoning_clarity", ""),
            clarity_score=float(parsed.get("clarity_score", 50.0)),
            total_semantic_score=float(parsed.get("total_semantic_score", 50.0)),
            insights=parsed.get("insights", [])[:3]
        )
        
        logger.info("llm.success", score=result.total_semantic_score)
        return result

    except Exception as e:
        logger.error("llm.analysis_failed", error=str(e), provider=settings.LLM_PROVIDER)
        # Graceful degradation: If LLM fails (e.g. Ollama is down or API timeouts), return a neutral score
        # so the technical analysis can still proceed.
        return SemanticAnalysisResult(
            authority_score=50.0,
            fact_density_score=50.0,
            clarity_score=50.0,
            total_semantic_score=50.0,
            insights=[f"🤖 AI Insight: The AI semantic engine ({settings.LLM_PROVIDER}) is currently unreachable. Returning baseline scores so technical analysis can proceed."]
        )
