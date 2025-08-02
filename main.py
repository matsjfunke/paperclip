import tempfile
import os
from typing import Optional

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


if __name__ == "__main__":
    app.run(transport="http", host="0.0.0.0", port=8000)
