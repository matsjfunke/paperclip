import tempfile
import os
from typing import Optional
from urllib.parse import quote


import fitz
import requests
from fastmcp import FastMCP

app = FastMCP("paperclip MCP Server")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def download_pdf(url: str) -> bytes:
    """Download PDF from URL"""
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"PDF not found at {url}")

def get_arxiv_paper(paper_id: str) -> bytes:
    """Download ArXiv paper by ID"""
    url = f"https://arxiv.org/pdf/{paper_id}"
    response = requests.head(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"arXiv paper not found: {paper_id}")

    return download_pdf(url)


def process_pdf_to_text(pdf_content: bytes, max_pages: Optional[int]) -> (str, int, int):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdf_content)
        temp_file_path = temp_file.name

    try:
        doc = fitz.open(temp_file_path)
        total_pages = len(doc)

        returned_pages = min(max_pages, total_pages) if max_pages else total_pages

        text = ""
        for page_num in range(returned_pages):
            page = doc.load_page(page_num)
            text += page.get_text()

    finally:
        os.unlink(temp_file_path)

    return text, total_pages, returned_pages


@app.tool
def get_arxiv_paper_text(
    paper_id: str,
    max_pages: Optional[int] = None
) -> dict:
    """
    Download and extract text from an ArXiv paper.
    
    Args:
        paper_id: The arXiv paper identifier (e.g., "2301.12345")
        max_pages: Maximum number of pages to return (optional)
    
    Returns:
        Dictionary containing paper ID, extracted text content, total pages, and returned pages
    """
    pdf_content = get_arxiv_paper(paper_id)
    text, total_pages, returned_pages = process_pdf_to_text(pdf_content, max_pages)

    return {
        "paper_id": paper_id, 
        "content": text, 
        "total_pages": total_pages, 
        "returned_pages": returned_pages, 
        "format": "text"
    }


def get_osf_providers() -> list:
    """Fetch current list of valid OSF preprint providers"""
    url = "https://api.osf.io/v2/preprint_providers/"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    # Extract provider IDs from the response
    providers = [provider['id'] for provider in data['data']]
    return sorted(providers)

def get_osf_provider_preprints_metadata(provider: str):
    # Get current valid providers
    valid_providers = get_osf_providers()
    
    # Validate provider
    if provider not in valid_providers:
        raise ValueError(f"Invalid provider: {provider}. Allowed providers: {valid_providers}")

    # Build query parameter and encode it
    param = quote('filter[provider]')
    url = f"https://api.osf.io/v2/preprints/?{param}={quote(provider)}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

@app.tool
def list_preprint_providers() -> dict:
    """
    Get the current list of available preprint providers in the paperclip MCP server.
    
    Returns:
        Dictionary containing the list of valid provider IDs and total count
    """
    providers = get_osf_providers()
    providers += ["arxiv", "biorxiv", "medrxiv", "chemrxiv"]
    providers.sort(key=str.lower)
    return {
        "providers": providers,
        "total_count": len(providers),
    }

@app.tool
def get_osf_provider_preprints_metadata(
    provider: str,
) -> dict:
    """
    Get metadata for preprints from an OSF provider.

    Args:
        provider: The provider of the paper. Use list_osf_providers() to see available options.
    """
    return get_osf_provider_preprints_metadata(provider)


if __name__ == "__main__":
    app.run(transport="http", host="0.0.0.0", port=8000)
