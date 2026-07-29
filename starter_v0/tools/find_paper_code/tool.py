from __future__ import annotations

import re
from typing import Any
import requests

from tools._shared import TIMEOUT, err


GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"


def find_paper_code(query: str = "", max_results: int = 5) -> dict[str, Any]:
    """Find official or community code implementations for a research paper on GitHub & PapersWithCode."""
    try:
        query_text = (query or "").strip()
        if not query_text:
            return {
                "tool": "find_paper_code",
                "query": query,
                "total_found": 0,
                "repositories": [],
                "message": "Query string is empty.",
            }

        max_results = max(1, min(int(max_results or 5), 10))
        repositories: list[dict[str, Any]] = []

        # Clean query for repository search
        clean_q = re.sub(r"[^\w\s-]", "", query_text)
        search_query = f"{clean_q} paper implementation"

        # Search GitHub Repositories API
        gh_resp = requests.get(
            GITHUB_SEARCH_URL,
            params={"q": search_query, "sort": "stars", "order": "desc", "per_page": max_results},
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Research-Paper-Scout/1.0"},
            timeout=TIMEOUT,
        )

        if gh_resp.status_code == 200:
            gh_data = gh_resp.json()
            gh_items = gh_data.get("items", [])
            for item in gh_items:
                desc = (item.get("description") or "").lower()
                repositories.append({
                    "name": item.get("full_name"),
                    "url": item.get("html_url"),
                    "stars": item.get("stargazers_count", 0),
                    "is_official": "official" in desc or "paper" in desc,
                    "framework": item.get("language") or "Python",
                    "source": "GitHub",
                })

        return {
            "tool": "find_paper_code",
            "query": query_text,
            "total_found": len(repositories),
            "repositories": repositories[:max_results],
        }

    except Exception as exc:
        return err("find_paper_code", exc)
