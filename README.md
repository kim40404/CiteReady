# CiteReady 🚀

**AI Search Visibility Scoring Engine** — Know if AI will cite your content before you publish.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)

CiteReady is an enterprise-grade API that analyzes web content and scores its "Generative Engine Optimization" (GEO) readiness. It tells you how likely AI search engines (like ChatGPT, Perplexity, and Google AI Overviews) are to cite your content as a source.

## 🎯 The Problem

The SEO landscape has shifted from "ranking for keywords" to "being cited in AI answers." Traditional SEO tools don't measure AI citation readiness. CiteReady fills this gap by scoring your content based on what LLMs actually look for.

## ✨ Features (Phase 1)

- **GEO Scoring Engine**: 5-category analysis (Entity Clarity, Citation Readiness, Content Structure, Freshness, Technical Accessibility).
- **Comprehensive Parsing**: Extracts headings, schema markup (JSON-LD/Microdata), links, images, and metadata from raw HTML.
- **Enterprise Observability**: Built-in Trace IDs, structured JSON logging, and database persistence for full audit trails.
- **Actionable Insights**: Returns a prioritized list of critical issues and actionable recommendations.

## 🚀 Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/kim40404/citeready.git
cd citeready
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

Copy the environment template and adjust if necessary:

```bash
cp .env.example .env
```

_(By default, CiteReady uses SQLite which requires zero setup)._

### 3. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.
Check out the interactive Swagger documentation at `http://localhost:8000/docs`.

## 🛠️ Usage

### Analyze a URL

Send a POST request to `/api/v1/analyze`:

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Example Response:**

```json
{
  "trace_id": "2c9d39cd-7ece-4608-8ca0-73025e61c55b",
  "url": "https://example.com",
  "geo_score": 75.5,
  "grade": "B",
  "scores": [
    {
      "name": "Entity Clarity",
      "score": 90.0,
      "max_score": 100.0,
      "weight": 0.2,
      "details": ["✅ Title found...", "✅ Exactly one H1 tag found"]
    }
  ],
  "issues": [
    {
      "severity": "warning",
      "category": "Content Structure",
      "message": "Only 2/5 images have alt text.",
      "recommendation": "Add descriptive alt text to all images for accessibility and AI understanding."
    }
  ],
  "priority_actions": [
    "Add descriptive alt text to all images for accessibility and AI understanding."
  ]
}
```

## 🏗️ Architecture

CiteReady is built with modern, async Python:

- **API**: FastAPI + Pydantic v2
- **Scraping/Parsing**: HTTPX + BeautifulSoup4 + lxml
- **Database**: SQLAlchemy 2.0 (async) + SQLite/PostgreSQL
- **Observability**: Structlog + OpenTelemetry readiness

## 🗺️ Roadmap

- **Phase 1 (Current)**: Foundation API, Content Parser, Rule-based GEO Scorer, Audit Database.
- **Phase 2 (Upcoming)**: LLM Integration (Claude/OpenAI), Semantic Entity Detection, Content Gap Analysis.
- **Phase 3**: Web Dashboard (Next.js), Batch Processing, Scheduled Scans.

## 👨‍💻 Author

**Kimsang Silalahi**
AI Engineer | LLM Apps & Agentic Systems

- [Portfolio](https://kimsilalahi.vercel.app)
- [LinkedIn](https://www.linkedin.com/in/kimsang-silalahi-3a8b13308/)
- [Hugging Face](https://huggingface.co/Kimsang766)
