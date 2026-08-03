import os
import requests
import wikipedia
import arxiv
from typing import Optional, Dict, Any, List
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from backend.app.utils.logger import logger

def is_english_text(text: str) -> bool:
    """Helper to verify text is predominantly English / non-CJK."""
    if not text:
        return True
    cjk_count = len([c for c in text if '\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u30ff'])
    return cjk_count < (len(text) * 0.15)

def search_duckduckgo(query: str, max_results: int = 5) -> str:
    """Performs web search using DuckDuckGo Free API with English region filtering."""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, region="en-us", max_results=max_results * 2):
                title = r.get("title", "No Title")
                snippet = r.get("body", "")
                link = r.get("href", "")
                if is_english_text(title) and is_english_text(snippet):
                    results.append(f"Title: {title}\nURL: {link}\nSnippet: {snippet}\n")
                    if len(results) >= max_results:
                        break

        if not results:
            return f"No English web search results found for query: '{query}'"

        return f"DuckDuckGo Search Results for '{query}':\n\n" + "\n---\n".join(results)
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return f"DuckDuckGo search fallback: unable to fetch web results."

def search_wikipedia(query: str, max_results: int = 3) -> str:
    """Searches Wikipedia free encyclopedia."""
    try:
        wikipedia.set_lang("en")
        results = []
        search_hits = wikipedia.search(query, results=max_results)
        for title in search_hits:
            try:
                summary = wikipedia.summary(title, sentences=3)
                if is_english_text(title) and is_english_text(summary):
                    results.append(f"Title: {title}\nSummary: {summary}\n")
            except Exception:
                continue
        if not results:
            return "No Wikipedia results found."
        return "Wikipedia Search Results:\n\n" + "\n---\n".join(results)
    except Exception as e:
        return f"Wikipedia search notice: {e}"

def search_arxiv(query: str, max_results: int = 3) -> str:
    """Searches Arxiv open academic paper registry."""
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = []
        for paper in search.results():
            results.append(f"Title: {paper.title}\nAuthors: {', '.join([a.name for a in paper.authors])}\nURL: {paper.pdf_url}\nAbstract: {paper.summary[:400]}...\n")
        if not results:
            return "No Arxiv academic papers found."
        return "Arxiv Academic Search Results:\n\n" + "\n---\n".join(results)
    except Exception as e:
        return f"Arxiv search notice: {e}"

def search_github(query: str, max_results: int = 3) -> str:
    """Searches GitHub public code repositories."""
    try:
        url = f"https://api.github.com/search/repositories?q={query}&per_page={max_results}"
        res = requests.get(url, headers={"User-Agent": "OmniAgent-AI-Platform"}, timeout=5.0)
        if res.status_code == 200:
            items = res.json().get("items", [])
            results = []
            for item in items:
                results.append(f"Repo: {item.get('full_name')}\nURL: {item.get('html_url')}\nDescription: {item.get('description', 'No description')}\nStars: {item.get('stargazers_count')}\n")
            if results:
                return "GitHub Code Repository Results:\n\n" + "\n---\n".join(results)
        return "No GitHub repositories found."
    except Exception as e:
        return f"GitHub search notice: {e}"

def multi_free_web_search(query: str) -> str:
    """Orchestrates search across free public search tools."""
    logger.info(f"Executing Multi Free Web Search for: '{query}'")

    ddg_res = search_duckduckgo(query, max_results=4)
    wiki_res = search_wikipedia(query, max_results=2)

    combined = f"=== Live Web Search Results ===\n{ddg_res}\n\n=== Wikipedia Encyclopedia Results ===\n{wiki_res}"
    return combined
