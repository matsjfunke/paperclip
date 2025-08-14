import requests
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from utils import sanitize_api_queries, extract_pdf_to_markdown


def fetch_openalex_papers(
    query: Optional[str] = None,
    author: Optional[str] = None,
    title: Optional[str] = None,
    publisher: Optional[str] = None,
    institution: Optional[str] = None,
    concepts: Optional[str] = None,
    date_published_gte: Optional[str] = None,
    max_results: int = 20,
    page: int = 1,
) -> Dict[str, Any]:
    """
    Fetch papers from the OpenAlex API using various search parameters.

    Args:
        query: General search query (full-text search)
        author: Author name to search for
        title: Title keywords to search for
        publisher: Publisher name to search for
        institution: Institution name to search for
        concepts: Concepts to filter by (e.g., 'computer science', 'artificial intelligence')
        date_published_gte: Published date greater than or equal to (YYYY-MM-DD)
        max_results: Maximum number of results to return (default 20, max 200)
        page: Page number for pagination (default 1)

    Returns:
        Dictionary containing papers data from OpenAlex API
    """
    base_url = "https://api.openalex.org/works"
    filters = {}

    if query:
        filters["search"] = sanitize_api_queries(query, max_length=500)
    if author:
        filters["filter"] = f"authors.author_name.search:{sanitize_api_queries(author, max_length=200)}"
    if title:
        if "filter" in filters:
            filters["filter"] += f",{sanitize_api_queries(title, max_length=500)}"
        else:
            filters["filter"] = f"title.search:{sanitize_api_queries(title, max_length=500)}"
    if publisher:
        if "filter" in filters:
            filters["filter"] += f",publisher.search:{sanitize_api_queries(publisher, max_length=200)}"
        else:
            filters["filter"] = f"publisher.search:{sanitize_api_queries(publisher, max_length=200)}"
    if institution:
        if "filter" in filters:
            filters["filter"] += f",institutions.institution_name.search:{sanitize_api_queries(institution, max_length=200)}"
        else:
            filters["filter"] = f"institutions.institution_name.search:{sanitize_api_queries(institution, max_length=200)}"
    if concepts:
        # OpenAlex concepts can be tricky, simple search might work for now
        if "filter" in filters:
            filters["filter"] += f",concepts.display_name.search:{sanitize_api_queries(concepts, max_length=200)}"
        else:
            filters["filter"] = f"concepts.display_name.search:{sanitize_api_queries(concepts, max_length=200)}"
    if date_published_gte:
        if "filter" in filters:
            filters["filter"] += f",publication_date:>{date_published_gte}"
        else:
            filters["filter"] = f"publication_date:>{date_published_gte}"

    # Add pagination and results limit
    filters["per_page"] = min(max_results, 200)  # OpenAlex max per_page is 200
    filters["page"] = page

    try:
        query_string = urlencode(filters, safe=":,") # Allow colons and commas in filter values
        url = f"{base_url}?{query_string}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        papers = []
        for result in data.get("results", []):
            paper = _parse_openalex_work(result)
            papers.append(paper)

        return {
            "data": papers,
            "meta": {
                "total_results": data.get("meta", {}).get("count", 0),
                "page": page,
                "per_page": filters["per_page"],
                "search_query": query, # Only include general query for simplicity
            },
            "links": data.get("meta", {}).get("next_page", ""),
        }

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Request failed: {str(e)}")


def _parse_openalex_work(work_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a single OpenAlex work entry."""
    # Extract authors
    authors = []
    for authorship in work_data.get("authorships", []):
        author = authorship.get("author", {})
        if author and author.get("display_name"):
            authors.append(author["display_name"])

    # Extract concepts
    concepts = []
    for concept in work_data.get("concepts", []):
        if concept.get("display_name"):
            concepts.append(concept["display_name"])

    # Extract PDF URL from primary location or alternative locations
    pdf_url = ""
    primary_location = work_data.get("primary_location", {})
    if primary_location and primary_location.get("pdf_url"):
        pdf_url = primary_location["pdf_url"]
    else:
        # Check all locations for a PDF URL if primary doesn't have one
        for location in work_data.get("locations", []):
            if location.get("pdf_url"):
                pdf_url = location["pdf_url"]
                break

    # Extract abstract from inverted index
    abstract = ""
    abstract_inverted_index = work_data.get("abstract_inverted_index", {})
    if abstract_inverted_index:
        abstract = _reconstruct_abstract_from_inverted_index(abstract_inverted_index)

    # Extract OpenAlex ID from URL
    openalex_id = work_data.get("id", "")
    if openalex_id.startswith("https://openalex.org/"):
        openalex_id = openalex_id.replace("https://openalex.org/", "")

    # Get primary location source info
    primary_location = work_data.get("primary_location", {})
    primary_source = ""
    if primary_location and primary_location.get("source"):
        primary_source = primary_location["source"].get("display_name", "")

    return {
        "id": openalex_id,
        "doi": work_data.get("doi", ""),
        "title": work_data.get("title", "") or work_data.get("display_name", ""),
        "abstract": abstract,
        "authors": authors,
        "publication_date": work_data.get("publication_date", ""),
        "publication_year": work_data.get("publication_year"),
        "cited_by_count": work_data.get("cited_by_count", 0),
        "concepts": concepts,
        "primary_location_url": work_data.get("primary_location", {}).get("landing_page_url", ""),
        "primary_source": primary_source,
        "pdf_url": pdf_url,
        "open_access_status": work_data.get("open_access", {}).get("oa_status", "closed"),
        "is_open_access": work_data.get("primary_location", {}).get("is_oa", False),
        "type": work_data.get("type", ""),
        "relevance_score": work_data.get("relevance_score", 0),
    }


def _reconstruct_abstract_from_inverted_index(inverted_index: Dict[str, Any]) -> str:
    """Reconstruct abstract text from OpenAlex's inverted index format."""
    if not inverted_index:
        return ""
    
    try:
        # Create a list to hold words at their positions
        word_positions = []
        
        for word, positions in inverted_index.items():
            if isinstance(positions, list):
                for position in positions:
                    word_positions.append((position, word))
        
        # Sort by position and reconstruct text
        word_positions.sort(key=lambda x: x[0])
        abstract_words = [word for _, word in word_positions]
        
        return " ".join(abstract_words)
    except Exception:
        # If reconstruction fails, return empty string
        return ""


def fetch_single_openalex_paper_metadata(paper_id: str) -> Dict[str, Any]:
    """
    Fetch metadata for a single OpenAlex paper by ID.

    Args:
        paper_id: OpenAlex paper ID (e.g., 'W2741809809')

    Returns:
        Dictionary containing paper metadata
    """
    base_url = "https://api.openalex.org/works"
    url = f"{base_url}/{paper_id}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        work_data = response.json()

        if not work_data.get("id"):
            raise ValueError(f"No metadata found for paper: {paper_id}")

        metadata = _parse_openalex_work(work_data)
        return metadata

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch paper metadata: {str(e)}")


async def download_openalex_paper_and_parse_to_markdown(paper_id: str):
    """
    Download a specific OpenAlex paper PDF by ID and parse it to markdown.
    Returns paper metadata along with markdown content.
    """
    metadata = {}
    try:
        # Get paper metadata
        metadata = fetch_single_openalex_paper_metadata(paper_id)

        pdf_url = metadata.get("pdf_url")
        if not pdf_url:
            return {"status": "error", "message": "No PDF URL found for this OpenAlex paper.", "metadata": metadata}

        # Download the PDF
        pdf_response = requests.get(pdf_url, timeout=60)
        pdf_response.raise_for_status()

        # Parse PDF to markdown
        try:
            markdown_content = await extract_pdf_to_markdown(pdf_response.content, filename=f"{paper_id}.pdf", write_images=False)

        except Exception as pdf_error:
            return {"status": "error", "message": f"Error parsing PDF: {str(pdf_error)}", "metadata": metadata}

        file_size = len(pdf_response.content)

        return {
            "status": "success",
            "metadata": metadata,
            "content": markdown_content,
            "file_size": file_size,
            "message": f"Successfully parsed PDF content ({file_size} bytes)",
        }

    except ValueError as e:
        return {"status": "error", "message": str(e), "metadata": metadata if metadata else {}}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Network error: {str(e)}", "metadata": metadata if metadata else {}}
    except Exception as e:
        return {"status": "error", "message": f"Error processing paper: {str(e)}", "metadata": metadata if metadata else {}}