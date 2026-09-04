"""Live opportunity discovery using Groq GPT-OSS 20B browser search.

STRICT RULE:
An opportunity is accepted only when its URL is present in the web-search
results returned by Groq for the same discovery response. A URL merely written
by the model is never considered proof.

This module is intentionally separate from the normal EduPilot AI service so
existing Chat, Study, Career, Resume and Interview functionality is not changed.
"""

from __future__ import annotations

import json
import re
from datetime import date
from urllib.parse import urlparse

from config import settings
from database.repositories import opportunity_repository as repo


_ALLOWED_CATEGORIES = {
    "Scholarship", "Internship", "Job", "Fellowship", "Competition", "Programme"
}
_ALLOWED_TYPES = {
    "Undergraduate", "Master's", "PhD", "Internship", "Full-time",
    "Part-time", "Fellowship", "Competition", "Programme", "Other"
}

# Hard cap on opportunities returned per discovery call. Enforced in discover()
# regardless of what a caller passes in, so this can never be bypassed.
MAX_RESULTS = 8

# Domains that are typically news coverage, aggregators, or social platforms
# rather than an opportunity's own official source. Opportunities from these
# domains are never rejected outright (sometimes they are the only source
# that surfaces), but they are sorted behind official-looking domains so that
# when more than MAX_RESULTS candidates are found, official sources win the
# cutoff first.
_NEWS_AGGREGATOR_DOMAIN_MARKERS = (
    "news", "medium.com", "blogspot.", "wordpress.com", "substack.com",
    "reddit.com", "quora.com", "facebook.com", "twitter.com", "x.com",
    "linkedin.com/pulse", "youtube.com", "tiktok.com", "pinterest.",
)


def _clean(value, max_len=500):
    return "" if value is None else str(value).strip()[:max_len]


def _valid_url(value):
    value = _clean(value, 500)
    if not value:
        return ""
    try:
        parsed = urlparse(value)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            return value
    except Exception:
        pass
    return ""


def _url_key(value):
    return _valid_url(value).rstrip("/").lower()


def _is_news_or_aggregator_domain(url: str) -> bool:
    """Heuristic only — used purely to order results, never to reject one."""
    key = _url_key(url)
    if not key:
        return False
    netloc = urlparse(key).netloc
    return any(marker in netloc or marker in key for marker in _NEWS_AGGREGATOR_DOMAIN_MARKERS)


def _object_get(obj, key, default=None):
    """Read a field from either an SDK object or a dictionary."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _grounded_urls(response) -> set[str]:
    """Extract URLs only from Groq web-search result objects.

    GPT-OSS browser-search responses can expose source URLs through tool/search
    metadata and annotations. We deliberately inspect only URL-bearing
    grounding metadata and never treat a URL merely written in model prose as evidence.
    """
    urls: set[str] = set()
    message = None

    choices = _object_get(response, "choices", []) or []
    if choices:
        message = _object_get(choices[0], "message")

    # Groq exposes executed tool metadata on chat-completion messages.
    # Different SDK/API versions can represent browser-search sources under
    # slightly different field names, so inspect only known grounding/source
    # metadata fields. Never scan arbitrary model prose for URLs.
    executed_tools = _object_get(message, "executed_tools", []) or []
    for tool in executed_tools:
        _collect_grounding_metadata(tool, urls)

    # Some responses expose source citations/annotations directly on the
    # message. These are grounding metadata, not model-generated prose.
    for key in ("annotations", "citations", "sources", "search_results"):
        _collect_grounding_metadata(_object_get(message, key), urls)

    return urls


def _collect_grounding_metadata(value, urls: set[str]):
    """Collect URLs only from recognized browser-search grounding metadata."""
    if value is None:
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _collect_grounding_metadata(item, urls)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            k = str(key).lower()
            if k in {"url", "uri", "link", "source_url", "source_uri"}:
                normalized = _url_key(item)
                if normalized:
                    urls.add(normalized)
            elif k in {
                "executed_tools", "search_results", "results", "items",
                "sources", "annotations", "citations", "references",
                "sources_used", "web_results", "browser_results",
            }:
                _collect_grounding_metadata(item, urls)
        return
    for key in (
        "url", "uri", "link", "source_url", "source_uri",
        "search_results", "results", "items", "sources",
        "annotations", "citations", "references", "sources_used",
        "web_results", "browser_results",
    ):
        item = getattr(value, key, None)
        if item is not None:
            if key in {"url", "uri", "link", "source_url", "source_uri"}:
                normalized = _url_key(item)
                if normalized:
                    urls.add(normalized)
            else:
                _collect_grounding_metadata(item, urls)


def _collect_search_result_urls(value, urls: set[str]):
    """Recursively collect URL fields from search-result structures only."""
    if value is None:
        return

    if isinstance(value, (list, tuple)):
        for item in value:
            _collect_search_result_urls(item, urls)
        return

    if isinstance(value, dict):
        for key, item in value.items():
            key_lower = str(key).lower()
            if key_lower in {"url", "uri", "link"}:
                normalized = _url_key(item)
                if normalized:
                    urls.add(normalized)
            elif key_lower in {"search_results", "results", "items", "sources"}:
                _collect_search_result_urls(item, urls)
        return

    for key in ("url", "uri", "link"):
        item = getattr(value, key, None)
        normalized = _url_key(item)
        if normalized:
            urls.add(normalized)

    for key in ("search_results", "results", "items", "sources"):
        item = getattr(value, key, None)
        if item is not None:
            _collect_search_result_urls(item, urls)


def _extract_text(response) -> str:
    choices = _object_get(response, "choices", []) or []
    if not choices:
        return ""
    message = _object_get(choices[0], "message")
    return _clean(_object_get(message, "content"), 20000)


def _extract_json(text: str):
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end <= start:
        return []

    try:
        data = json.loads(text[start:end + 1])
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _normalize(item: dict, grounded_urls: set[str]) -> dict | None:
    if not isinstance(item, dict):
        return None

    title = _clean(item.get("title"), 255)
    org = _clean(item.get("organization"), 255)
    desc = _clean(item.get("description"), 4000)
    url = _valid_url(item.get("external_url"))

    if not title or not org or not desc or not url:
        return None

    # HARD GATE:
    # The exact normalized URL must exist in Groq's actual search results.
    if _url_key(url) not in grounded_urls:
        return None

    category = _clean(item.get("category"), 100).title()
    if category not in _ALLOWED_CATEGORIES:
        category = "Programme"

    opp_type = _clean(item.get("opportunity_type"), 100)
    if opp_type not in _ALLOWED_TYPES:
        opp_type = "Other"

    deadline = _clean(item.get("deadline"), 20)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", deadline):
        deadline = None
    elif deadline < date.today().isoformat():
        return None

    requirements = []
    for req in item.get("requirements") or []:
        if isinstance(req, dict):
            description = _clean(req.get("description"), 1000)
            if description:
                requirements.append({
                    "requirement_type": _clean(req.get("requirement_type"), 100),
                    "description": description,
                })

    return {
        "title": title,
        "organization": org,
        "description": desc,
        "category": category,
        "opportunity_type": opp_type,
        "location": _clean(item.get("location"), 255) or "Not specified",
        "city": _clean(item.get("city"), 100),
        "province": _clean(item.get("province"), 100),
        "country": _clean(item.get("country"), 100),
        "region": _clean(item.get("region"), 100),
        "deadline": deadline,
        "external_url": url,
        "eligibility_summary": _clean(item.get("eligibility_summary"), 2000),
        "requirements": requirements[:10],
    }


def _dedupe(items):
    seen_titles = set()
    seen_urls = set()
    result = []

    for item in items:
        title_key = (
            _clean(item.get("title")).lower(),
            _clean(item.get("organization")).lower(),
        )
        url_key = _url_key(item.get("external_url"))

        if title_key in seen_titles or (url_key and url_key in seen_urls):
            continue

        seen_titles.add(title_key)
        if url_key:
            seen_urls.add(url_key)
        result.append(item)

    return result


def _prefer_official_sources(items: list[dict]) -> list[dict]:
    """Stable-sort so official/institutional domains are kept ahead of news,
    aggregator, and social-platform domains when the list is later truncated
    to MAX_RESULTS. Nothing is dropped here — only reordered.
    """
    return sorted(
        items,
        key=lambda item: _is_news_or_aggregator_domain(item.get("external_url", "")),
    )


def build_prompt(city: str, province: str, country: str, limit: int = MAX_RESULTS) -> str:
    limit = min(int(limit) if limit else MAX_RESULTS, MAX_RESULTS)
    location = ", ".join(x for x in (city, province, country) if x) or "Pakistan"

    return f"""You are EduPilot AI's LIVE opportunity discovery engine.
Today is {date.today().isoformat()}.
Student location: {location}.

Use Groq GPT-OSS 20B browser search for real-time web content. Find CURRENT, REAL opportunities
from across the public web.

IMPORTANT SEARCH STRATEGY — OPTIMIZED FOR A LIVE DEMO:
- Use ONE broad browser-search call first; do not perform a chain of separate searches.
- Make that single search query cover scholarships, internships, jobs, fellowships, training,
  competitions, hackathons and educational programmes in Lahore/Punjab/Pakistan and remote.
- Request enough search results to identify several distinct current opportunities.
- Do not stop at the first result; use the results returned by this single search to build the JSON.
- A single broad search is intentional: it keeps the live refresh fast and protects API quota.

Search broadly across:
- Government and public-sector websites
- Universities and educational institutions
- Official company career pages
- Scholarship providers and foundations
- NGOs and international organizations
- Reputable job and opportunity portals
- Training, fellowship and competition websites

LOCATION PRIORITY:
1. Student's city
2. Student's province
3. Pakistan
4. Remote opportunities
5. International opportunities relevant to the student

Find scholarships, internships, jobs, fellowships, competitions, training and
educational programmes.

STRICT ACCURACY RULES:
- You MUST perform real web search.
- Never use model memory as evidence.
- Never invent a title, organization, deadline, eligibility rule or URL.
- Every opportunity MUST use an external_url that appears in the web-search
  results for this response.
- If the URL was not returned by web search, OMIT the opportunity.
- Do not create or guess URLs.
- Do not use a generic search-results URL as an opportunity URL.
- Prefer the direct official opportunity/application page when available.
- STRONGLY prefer the opportunity's own official website, government page,
  institution page, or official application portal over a news article,
  blog post, aggregator listing, or social-media post ABOUT the
  opportunity. Only use a news/article/aggregator URL when no official
  page appeared in the search results for that opportunity.
- Only include opportunities that are open now or have a future deadline.
- For scholarships, fellowships, competitions, training and fixed-cycle programmes, a current/future
  deadline must be verified; otherwise OMIT the opportunity.
- For jobs and internships, a missing explicit deadline is acceptable only when the grounded page
  clearly shows that the vacancy/application is currently open or active.
- Reject pages whose content clearly belongs to an expired cycle (for example 2024 or 2025 when today
  is 2026-09-03), even if the page is still indexed.
- Do not claim Pakistan eligibility unless the source supports it.
- For this Pakistan-focused discovery, reject clearly non-Pakistan opportunity portals unless the
  specific opportunity is explicitly open to Pakistani students and the source supports that claim.
- Do not use scholarships.gov.in or other India-only portals for Pakistan opportunities.
- Try to return at least 5 genuinely useful opportunities when 5 or more can be verified.
- Return at most {limit} genuinely useful opportunities. Do not return more
  than {limit} items under any circumstance.

Before returning the JSON, actually use browser search for several distinct queries.
Example query themes (adapt as needed):
1. current Pakistan scholarships 2026 undergraduate
2. Lahore Punjab internships jobs students 2026
3. Pakistan fellowships training programmes 2026
4. Pakistan student competitions hackathons 2026
5. remote internships students 2026
These are examples only; choose queries that produce real current opportunities.

Return ONLY a JSON array. Do not add markdown or commentary. Keep each field concise so the response is fast.

Each item must contain:
title, organization, description, category, opportunity_type, location, city,
province, country, region, deadline, external_url, eligibility_summary,
requirements.

category must be one of:
Scholarship, Internship, Job, Fellowship, Competition, Programme.

requirements must be an array of objects with:
requirement_type, description.
"""


def discover(
    city: str = "",
    province: str = "",
    country: str = "Pakistan",
    limit: int = MAX_RESULTS,
) -> list[dict]:
    if not settings.GROQ_API_KEY:
        raise RuntimeError("Groq API key is not configured")

    # Hard cap — enforced here regardless of what any caller passes in.
    limit = min(int(limit) if limit else MAX_RESULTS, MAX_RESULTS)

    try:
        from groq import Groq
        import groq as groq_sdk
    except ImportError as exc:
        raise RuntimeError(
            "Groq package is not installed. Run: python -m pip install groq"
        ) from exc

    client = Groq(api_key=settings.GROQ_API_KEY)

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict live opportunity research engine. "
                        "Use one broad browser search covering multiple opportunity categories and locations before answering. "
                        "Never fabricate sources and use the returned search results to identify several opportunities."
                    ),
                },
                {
                    "role": "user",
                    "content": build_prompt(city, province, country, limit),
                },
            ],
            tool_choice="required",
            tools=[{"type": "browser_search"}],
            reasoning_effort="low",
        )
    except groq_sdk.RateLimitError as exc:
        raise RuntimeError(
            "Groq rate limit reached. Please wait a minute and try again."
        ) from exc
    except groq_sdk.AuthenticationError as exc:
        raise RuntimeError(
            "Groq API key was rejected. Check GROQ_API_KEY in your .env file."
        ) from exc
    except (groq_sdk.APIConnectionError, groq_sdk.APITimeoutError) as exc:
        raise RuntimeError(
            "Could not reach Groq right now. Check your internet connection and try again."
        ) from exc
    except groq_sdk.APIStatusError as exc:
        # Any other non-2xx status Groq returns (5xx, 400s not covered above, etc.)
        raise RuntimeError(
            f"Groq returned an error (status {exc.status_code}). Please try again shortly."
        ) from exc
    except groq_sdk.GroqError as exc:
        raise RuntimeError(
            "Live opportunity discovery is temporarily unavailable. Please try again shortly."
        ) from exc

    grounded_urls = _grounded_urls(response)

    # No search evidence = zero candidates. Nothing can reach the database.
    if not grounded_urls:
        return []

    raw_items = _extract_json(_extract_text(response))
    items = [_normalize(item, grounded_urls) for item in raw_items]
    items = _dedupe([item for item in items if item])
    items = _prefer_official_sources(items)

    return items[:limit]


def sync_to_database(items: list[dict]) -> tuple[int, int]:
    """Insert only verified new opportunities; never delete/update existing rows."""
    inserted = 0
    skipped = 0

    for item in items:
        url = _url_key(item.get("external_url"))
        if not url:
            skipped += 1
            continue

        if repo.find_existing_opportunity(
            item["title"], item["organization"], item["external_url"]
        ):
            skipped += 1
            continue

        opp_id = repo.insert_discovered_opportunity(item)

        if opp_id:
            inserted += 1
            for req in item.get("requirements", []):
                repo.insert_requirement(
                    opp_id,
                    req["requirement_type"] or "General",
                    req["description"],
                )
        else:
            skipped += 1

    return inserted, skipped
