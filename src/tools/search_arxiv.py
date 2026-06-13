import arxiv

def search_arxiv(query: str, max_results: int = 3) -> str:
    """
    Searches ArXiv for relevant papers.
    
    Args:
        query: Search query e.g. 'momentum trading strategy equities'
        max_results: Number of papers to return (default 3)
    
    Returns:
        String summary of papers found
    """
    try:
        client = arxiv.Client()
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = list(client.results(search))
        
        if not results:
            return f"No papers found for query: {query}"
        
        output = f"Found {len(results)} papers for '{query}':\n\n"
        
        for i, paper in enumerate(results, 1):
            output += f"""Paper {i}:
- Title: {paper.title}
- Authors: {', '.join(str(a) for a in paper.authors[:3])}
- Published: {paper.published.strftime('%Y-%m-%d')}
- Summary: {paper.summary[:300]}...
- URL: {paper.entry_id}

"""
        return output.strip()
    
    except Exception as e:
        return f"Error searching ArXiv: {str(e)}"