import wikipedia
import arxiv

def search_wikipedia(query: str, sentences: int = 3) -> str:
    """Searches Wikipedia and returns article summary."""
    try:
        summary = wikipedia.summary(query, sentences=sentences)
        return f"Wikipedia Summary for '{query}':\n{summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Wikipedia Disambiguation Error for '{query}'. Possible topics: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return f"Wikipedia Page not found for query '{query}'."
    except Exception as e:
        return f"Wikipedia Search Error: {str(e)}"

def search_arxiv(query: str, max_results: int = 3) -> str:
    """Searches Arxiv scientific research papers database."""
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        results = []
        for paper in client.results(search):
            authors = ", ".join([a.name for a in paper.authors])
            results.append(
                f"Paper Title: {paper.title}\n"
                f"Authors: {authors}\n"
                f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
                f"URL: {paper.entry_id}\n"
                f"Summary: {paper.summary[:500]}...\n"
            )

        if not results:
            return f"No Arxiv research papers found for query '{query}'."

        return f"Arxiv Search Results for '{query}':\n\n" + "\n---\n".join(results)
    except Exception as e:
        return f"Arxiv Search Error: {str(e)}"
