"""Quick test script for CiteReady /analyze endpoint."""

import httpx
import json

r = httpx.post(
    "http://localhost:8000/api/v1/analyze",
    json={"url": "https://flyrank.com"},
    timeout=30,
)
print(f"Status: {r.status_code}")
data = r.json()

if r.status_code == 200:
    print(f"GEO Score: {data['geo_score']} (Grade: {data['grade']})")
    print(f"Semantic Score (AI): {data.get('semantic_score', 0.0)}")
    print(f"Trace ID: {data['trace_id']}")
    print(f"Latency: {data['latency_ms']}ms")
    print(f"Word Count: {data['content_meta']['word_count']}")
    print()

    print("=== AI INSIGHTS ===")
    for insight in data.get("ai_insights", []):
        print(f"  💡 {insight}")
    print()

    print("=== SCORE BREAKDOWN ===")
    for s in data["scores"]:
        print(f"  {s['name']}: {s['score']}/{s['max_score']} (weight: {s['weight']})")
    print()

    print("=== TOP ISSUES ===")
    for i in data["issues"][:5]:
        print(f"  [{i['severity'].upper()}] {i['message']}")
    print()

    print("=== PRIORITY ACTIONS ===")
    for a in data["priority_actions"]:
        print(f"  -> {a}")
else:
    print(json.dumps(data, indent=2))
