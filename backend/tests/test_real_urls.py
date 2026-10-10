"""
Phase 2 Real Public URLs Test Suite.
Tests diverse real-world public web pages across 13 distinct categories politely,
with single requests, respectful User-Agent, and measuring latency and extraction accuracy.
Marked as integration tests so default offline test runs skip live network calls.
"""
import time
import pytest
from backend.app.services.url_fetcher import fetch_and_parse_url
from backend.app.errors import SecondOpinionException, ErrorCode

@pytest.mark.integration
@pytest.mark.anyio
async def test_real_urls_suite():
    test_cases = [
        {
            "category": "Encyclopedia Article",
            "url": "https://en.wikipedia.org/wiki/Turing_machine",
            "expected_outcome": "SUCCESS",
        },
        {
            "category": "Preprint Abstract Page",
            "url": "https://arxiv.org/abs/2103.00020",
            "expected_outcome": "SUCCESS",
        },
        {
            "category": "PDF Link",
            "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "expected_outcome": "ERROR_MEDIA_TYPE",
        },
        {
            "category": "News Article / Aggregator",
            "url": "https://news.ycombinator.com/",
            "expected_outcome": "SUCCESS",
        },
        {
            "category": "JavaScript-Heavy Page",
            "url": "https://react.dev/",
            "expected_outcome": "SUCCESS",
        },
        {
            "category": "Documentation Page",
            "url": "https://docs.python.org/3/tutorial/index.html",
            "expected_outcome": "SUCCESS",
        },
        {
            "category": "Non-English Page",
            "url": "https://fr.wikipedia.org/wiki/Tour_Eiffel",
            "expected_outcome": "SUCCESS",
        },
        {
            "category": "A 404 Not Found Page",
            "url": "https://en.wikipedia.org/wiki/SecondOpinionNonExistent_404_Test_987",
            "expected_outcome": "ERROR_404",
        },
        {
            "category": "Login Page",
            "url": "https://github.com/login",
            "expected_outcome": "SUCCESS_OR_EMPTY",
        },
        {
            "category": "Image URL",
            "url": "https://en.wikipedia.org/static/images/icons/wikipedia.png",
            "expected_outcome": "ERROR_MEDIA_TYPE",
        },
        {
            "category": "URL Shortener / Redirect",
            "url": "https://w.wiki/3",  # Official Wikimedia shortener redirecting to wikimediafoundation.org
            "expected_outcome": "SUCCESS_REDIRECT",
        },
        {
            "category": "A Very Long Page",
            "url": "https://www.w3.org/TR/html401/",
            "expected_outcome": "SUCCESS_OR_OVERSIZED",
        },
        {
            "category": "Page with Tracking Parameters",
            "url": "https://en.wikipedia.org/wiki/Alan_Turing?utm_source=secondopinion&utm_medium=audit&session_id=9876",
            "expected_outcome": "SUCCESS",
        },
    ]

    results = []
    for tc in test_cases:
        t0 = time.perf_counter()
        url = tc["url"]
        category = tc["category"]
        try:
            doc, chunks = await fetch_and_parse_url(url, check_robots=True)
            elapsed = time.perf_counter() - t0
            results.append({
                "category": category,
                "url": url,
                "outcome": "SUCCESS",
                "length": doc.character_count,
                "chunks": len(chunks),
                "elapsed_sec": round(elapsed, 2),
                "notes": f"Clean extraction, doc title: {doc.filename[:30]}"
            })
        except SecondOpinionException as e:
            elapsed = time.perf_counter() - t0
            results.append({
                "category": category,
                "url": url,
                "outcome": f"BLOCKED/REJECTED ({e.detail['code']})",
                "length": 0,
                "chunks": 0,
                "elapsed_sec": round(elapsed, 2),
                "notes": e.detail["message"][:60]
            })
        except Exception as e:
            elapsed = time.perf_counter() - t0
            results.append({
                "category": category,
                "url": url,
                "outcome": f"FAILED ({type(e).__name__})",
                "length": 0,
                "chunks": 0,
                "elapsed_sec": round(elapsed, 2),
                "notes": str(e)[:60]
            })

    print("\n--- REAL URL AUDIT RESULTS ---")
    for r in results:
        print(f"[{r['category']}] -> {r['outcome']} | {r['length']} chars | {r['elapsed_sec']}s | {r['notes']}")
    
    # Assert expected outcomes
    for r in results:
        if r["category"] in ("Image URL", "PDF Link"):
            assert "REJECTED" in r["outcome"] or "UNSUPPORTED" in r["outcome"]
        elif r["category"] == "A 404 Not Found Page":
            assert "404" in r["notes"] or "REJECTED" in r["outcome"]
        elif r["category"] in ("Encyclopedia Article", "Documentation Page", "Non-English Page"):
            assert r["outcome"] == "SUCCESS"
            assert r["length"] > 100
