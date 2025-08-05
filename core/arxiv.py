from typing import Any, Dict, Optional
from urllib.parse import quote, urlencode
import xml.etree.ElementTree as ET

import requests

from utils import sanitize_api_queries, extract_pdf_to_markdown


def fetch_arxiv_papers(
    query: Optional[str] = None,
    category: Optional[str] = None,
    author: Optional[str] = None,
    title: Optional[str] = None,
    max_results: int = 100,
    start_index: int = 0
) -> Dict[str, Any]:
    """
    Fetch papers from arXiv API using various search parameters.
    
    Args:
        query: General search query
        category: arXiv category (e.g., 'cs.AI', 'physics.gen-ph')
        author: Author name to search for
        title: Title keywords to search for
        max_results: Maximum number of results to return (default 100)
        start_index: Starting index for pagination (default 0)
    
    Returns:
        Dictionary containing papers data from arXiv API
    """
    # Build search query
    search_parts = []
    
    if query:
        search_parts.append(f"all:{sanitize_api_queries(query, max_length=200)}")
    if category:
        search_parts.append(f"cat:{sanitize_api_queries(category, max_length=50)}")
    if author:
        search_parts.append(f"au:{sanitize_api_queries(author, max_length=100)}")
    if title:
        search_parts.append(f"ti:{sanitize_api_queries(title, max_length=200)}")
    
    if not search_parts:
        # Default search if no parameters provided
        search_query = "all:*"
    else:
        search_query = " AND ".join(search_parts)
    
    # Build API URL
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": search_query,
        "start": start_index,
        "max_results": min(max_results, 20)
    }
    
    query_string = urlencode(params, safe=':', quote_via=quote)
    url = f"{base_url}?{query_string}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.content)
        
        # Extract namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            paper = _parse_arxiv_entry(entry, ns)
            papers.append(paper)
        
        return {
            "data": papers,
            "meta": {
                "total_results": len(papers),
                "start_index": start_index,
                "max_results": max_results,
                "search_query": search_query
            }
        }
        
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Request failed: {str(e)}")
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse arXiv response: {str(e)}")


def _parse_arxiv_entry(entry, ns):
    """Parse a single arXiv entry from XML."""
    # Extract basic info
    arxiv_id = entry.find('atom:id', ns).text.split('/')[-1] if entry.find('atom:id', ns) is not None else ""
    title = entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else ""
    summary = entry.find('atom:summary', ns).text.strip() if entry.find('atom:summary', ns) is not None else ""
    published = entry.find('atom:published', ns).text if entry.find('atom:published', ns) is not None else ""
    updated = entry.find('atom:updated', ns).text if entry.find('atom:updated', ns) is not None else ""
    
    # Extract authors
    authors = []
    for author in entry.findall('atom:author', ns):
        name_elem = author.find('atom:name', ns)
        if name_elem is not None:
            authors.append(name_elem.text)
    
    # Extract categories
    categories = []
    for category in entry.findall('atom:category', ns):
        term = category.get('term')
        if term:
            categories.append(term)
    
    # Extract links (PDF, abstract)
    pdf_url = ""
    abstract_url = ""
    for link in entry.findall('atom:link', ns):
        if link.get('type') == 'application/pdf':
            pdf_url = link.get('href', '')
        elif link.get('rel') == 'alternate':
            abstract_url = link.get('href', '')
    
    # Extract DOI if available
    doi = ""
    doi_elem = entry.find('arxiv:doi', ns)
    if doi_elem is not None:
        doi = doi_elem.text
    
    return {
        "id": arxiv_id,
        "title": title,
        "summary": summary,
        "authors": authors,
        "categories": categories,
        "published": published,
        "updated": updated,
        "pdf_url": pdf_url,
        "abstract_url": abstract_url,
        "doi": doi
    }


def fetch_single_arxiv_paper_metadata(paper_id: str) -> Dict[str, Any]:
    """
    Fetch metadata for a single arXiv paper by ID.
    
    Args:
        paper_id: arXiv paper ID (e.g., '2301.00001' or 'cs.AI/0001001')
    
    Returns:
        Dictionary containing paper metadata
    """
    # Validate paper exists first
    pdf_url = f"https://arxiv.org/pdf/{paper_id}"
    response = requests.head(pdf_url, timeout=10)
    if response.status_code != 200:
        raise ValueError(f"arXiv paper not found: {paper_id}")
    
    # Fetch metadata from API
    try:
        api_url = f"http://export.arxiv.org/api/query?id_list={paper_id}"
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}
        
        entry = root.find('atom:entry', ns)
        if entry is None:
            raise ValueError(f"No metadata found for paper: {paper_id}")
        
        metadata = _parse_arxiv_entry(entry, ns)
        metadata["download_url"] = pdf_url
        
        return metadata
        
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch paper metadata: {str(e)}")
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse arXiv response: {str(e)}")


async def download_arxiv_paper_and_parse_to_markdown(paper_id: str):
    """
    Download a specific arXiv paper PDF by ID and parse it to markdown.
    Returns paper metadata along with markdown content.
    """
    metadata = {}
    try:
        # Get paper metadata
        metadata = fetch_single_arxiv_paper_metadata(paper_id)
        
        # Download the PDF
        pdf_response = requests.get(metadata['download_url'], timeout=60)
        pdf_response.raise_for_status()
        
        # Parse PDF to markdown
        try:
            markdown_content = await extract_pdf_to_markdown(
                pdf_response.content,
                filename=f"{paper_id}.pdf",
                write_images=False
            )
            
        except Exception as pdf_error:
            return {
                "status": "error",
                "message": f"Error parsing PDF: {str(pdf_error)}",
                "metadata": metadata
            }
        
        file_size = len(pdf_response.content)
        
        return {
            "status": "success",
            "metadata": metadata,
            "content": markdown_content,
            "file_size": file_size,
            "message": f"Successfully parsed PDF content ({file_size} bytes)"
        }
            
    except ValueError as e:
        return {
            "status": "error", 
            "message": str(e),
            "metadata": metadata if metadata else {}
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error", 
            "message": f"Network error: {str(e)}",
            "metadata": metadata if metadata else {}
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing paper: {str(e)}",
            "metadata": metadata if metadata else {}
        }