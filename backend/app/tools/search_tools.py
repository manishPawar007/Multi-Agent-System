import os
import requests
import wikipedia
import arxiv
from typing import Optional, Dict, Any, List
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from backend.app.utils.logger import logger

def search_duckduckgo(query: str, max_results: int = 5) -> str:
    """Performs web search using DuckDuckGo Free API."""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get("title", "No Title")
                snippet = r.get("body", "")
                link = r.get("href", "")
                results.append(f"Title: {title}\nURL: {link}\nSnippet: {snippet}\n")

        if not results:
            return f"No DuckDuckGo web results found for query: '{query}'"

        return f"DuckDuckGo Search Results for '{query}':\n\n" + "\n---\n".join(results)
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return f"DuckDuckGo search fallback: unable to fetch web results."

def search_wikipedia(query: str, max_results: int = 3) -> str:
    """Searches Wikipedia free encyclopedia."""
    try:
        results = []
        search_hits = wikipedia.search(query, results=max_results)
        for title in search_hits:
            try:
                summary = wikipedia.summary(title, sentences=3)
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
    """Searches GitHub public open source repository API."""
    try:
        url = f"https://api.github.com/search/repositories?q={requests.utils.quote(query)}&sort=stars&order=desc"
        res = requests.get(url, headers={"User-Agent": "OmniAgentAI/1.0"}, timeout=10)
        if res.status_code == 200:
            data = res.json()
            items = data.get("items", [])[:max_results]
            results = []
            for item in items:
                name = item.get("full_name", "")
                desc = item.get("description", "")
                stars = item.get("stargazers_count", 0)
                link = item.get("html_url", "")
                results.append(f"Repository: {name} (Stars: {stars})\nURL: {link}\nDescription: {desc}\n")
            if results:
                return "GitHub Repository Search Results:\n\n" + "\n---\n".join(results)
        return "No GitHub repositories found."
    except Exception as e:
        return f"GitHub search notice: {e}"

def search_stackoverflow(query: str, max_results: int = 3) -> str:
    """Searches Stack Overflow public questions API."""
    try:
        url = f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={requests.utils.quote(query)}&site=stackoverflow"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            items = res.json().get("items", [])[:max_results]
            results = []
            for item in items:
                title = item.get("title", "")
                link = item.get("link", "")
                score = item.get("score", 0)
                is_answered = item.get("is_answered", False)
                results.append(f"Question: {title} (Answered: {is_answered}, Score: {score})\nURL: {link}\n")
            if results:
                return "Stack Overflow Search Results:\n\n" + "\n---\n".join(results)
        return "No Stack Overflow discussions found."
    except Exception as e:
        return f"Stack Overflow search notice: {e}"

def multi_free_web_search(query: str) -> str:
    """Aggregates all free open-source search tools (DuckDuckGo, Wikipedia, Arxiv, GitHub, StackOverflow)."""
    ddg = search_duckduckgo(query, max_results=4)
    wiki = search_wikipedia(query, max_results=2)
    arxiv_res = search_arxiv(query, max_results=2)
    github_res = search_github(query, max_results=2)

    return f"{ddg}\n\n{wiki}\n\n{arxiv_res}\n\n{github_res}"
