"""
matsjfunke
"""

import tempfile
from typing import Optional

import requests
import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()


def get_arxiv_paper(paper_id: str) -> str:
    url = f"https://arxiv.org/pdf/{paper_id}"
    response = requests.head(url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="arXiv paper not found")

    return download_pdf(url)


def get_medrxiv_paper(digital_object_id: str) -> str:
    url = f"https://www.medrxiv.org/content/{digital_object_id}.full.pdf"
    response = requests.head(url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="medRrxiv paper not found")

    return download_pdf(url)


def get_biorxiv_paper(digital_object_id: str) -> str:
    url = f"https://www.biorxiv.org/content/{digital_object_id}.full.pdf"
    response = requests.head(url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="bioRrxiv paper not found")

    return download_pdf(url)


def download_pdf(url: str) -> bytes:
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise HTTPException(status_code=404, detail="PDF not found")


@app.get("/medrxiv/papers/text")
def get_medrxiv_paper_text(
    digital_object_id: str = Query(..., description="The medRrxiv digital object identifier of the paper"),
    max_pages: Optional[int] = Query(None, description="Maximum number of pages to return"),
):

    # text = process_pdf_to_text(pdf_content, max_pages)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdf_content)
        temp_file_path = temp_file.name

    try:
        total_pages = len(fitz.open(temp_file_path))
    finally:
        os.unlink(temp_file_path)

    returned_pages = min(max_pages, total_pages) if max_pages else total_pages

    return {"digital_object_id": digital_object_id, "content": text, "total_pages": total_pages, "returned_pages": returned_pages, "format": "text"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
