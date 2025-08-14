"""
PDF processing utilities using pymupdf4llm.

download_paper_and_parse_to_markdown()     download_pdf_and_parse_to_markdown()
(with metadata)                            (direct URL)
    |                                         |
    v                                         v
Extract PDF URL from metadata          Generate filename from URL
    |                                         |
    +-------------------+---------------------+
                        |
                        v
            _download_and_parse_pdf_core()
                        |
                        v
                requests.get(pdf_url)
                        |
                        v
            extract_pdf_to_markdown()
                        |
                        v
        Return (content, size, message)
                        |
            +-----------+-----------+
            |                       |
            v                       v
    Format response            Format response
    with metadata              with pdf_url

The shared core logic eliminates code duplication while maintaining 
distinct interfaces for metadata-based vs direct URL workflows.
"""

import os
from typing import Optional
import tempfile
import httpx
import requests

import pymupdf4llm as pdfmd


async def extract_pdf_to_markdown(file_input, filename: Optional[str] = None, write_images: bool = False) -> str:
    """
    Extract PDF content to markdown using pymupdf4llm.

    Args:
        file_input: Can be either:
                   - A file path (str) to an existing PDF
                   - File bytes/content (bytes) that will be written to temp file
                   - A file object with .read() method (for async file handling)
        filename: Optional filename to use for temp file (only used when file_input is bytes/file object)
        write_images: Whether to extract and write images (default: False)

    Returns:
        Markdown content as string
    """
    temp_path = None

    try:
        # Handle different input types
        if isinstance(file_input, str) and os.path.exists(file_input):
            # Direct file path
            md = pdfmd.to_markdown(file_input, write_images=write_images)
            return md

        elif isinstance(file_input, bytes):
            # File bytes - write to temp file
            temp_filename = filename or "temp_pdf.pdf"
            temp_path = f"/tmp/{temp_filename}"
            with open(temp_path, "wb") as f:
                f.write(file_input)
            md = pdfmd.to_markdown(temp_path, write_images=write_images)
            return md

        elif hasattr(file_input, "read"):
            # File object (like FastAPI UploadFile)
            temp_filename = filename or getattr(file_input, "filename", "temp_pdf.pdf")
            temp_path = f"/tmp/{temp_filename}"

            # Handle both sync and async file objects
            if hasattr(file_input, "__aiter__") or hasattr(file_input.read, "__call__"):
                try:
                    # Try async read first
                    content = await file_input.read()
                except TypeError:
                    # Fall back to sync read
                    content = file_input.read()
            else:
                content = file_input.read()

            with open(temp_path, "wb") as f:
                f.write(content)
            md = pdfmd.to_markdown(temp_path, write_images=write_images)
            return md

        else:
            raise ValueError(f"Unsupported file_input type: {type(file_input)}")

    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass  # Ignore cleanup errors


async def _download_and_parse_pdf_core(
    pdf_url: str, 
    filename: str = "paper.pdf",
    write_images: bool = False
) -> tuple[str, int, str]:
    # Download PDF
    pdf_response = requests.get(pdf_url, timeout=60)
    pdf_response.raise_for_status()
    
    # Parse PDF to markdown
    markdown_content = await extract_pdf_to_markdown(
        pdf_response.content, 
        filename=filename, 
        write_images=write_images
    )
    
    file_size = len(pdf_response.content)
    message = f"Successfully parsed PDF content ({file_size} bytes)"
    
    return markdown_content, file_size, message


async def download_paper_and_parse_to_markdown(
    metadata: dict, 
    pdf_url_field: str = "download_url",
    paper_id: str = "",
    write_images: bool = False
) -> dict:
    # Extract PDF URL from metadata
    pdf_url = metadata.get(pdf_url_field)
    if not pdf_url:
        return {
            "status": "error", 
            "message": f"No PDF URL found in metadata field '{pdf_url_field}'", 
            "metadata": metadata
        }

    try:
        filename = f"{paper_id}.pdf" if paper_id else "paper.pdf"
        markdown_content, file_size, message = await _download_and_parse_pdf_core(
            pdf_url, filename, write_images
        )
        
        return {
            "status": "success",
            "metadata": metadata,
            "content": markdown_content,
            "file_size": file_size,
            "message": message,
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error", 
            "message": f"Network error: {str(e)}", 
            "metadata": metadata
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Error parsing PDF: {str(e)}", 
            "metadata": metadata
        }


async def download_pdf_and_parse_to_markdown(pdf_url: str, write_images: bool = False) -> dict:
    try:
        filename = pdf_url.split('/')[-1] if '/' in pdf_url else "paper.pdf"
        if not filename.endswith('.pdf'):
            filename = "paper.pdf"
            
        markdown_content, file_size, message = await _download_and_parse_pdf_core(
            pdf_url, filename, write_images
        )
        
        return {
            "status": "success",
            "content": markdown_content,
            "file_size": file_size,
            "pdf_url": pdf_url,
            "message": message,
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error", 
            "message": f"Network error downloading PDF: {str(e)}", 
            "pdf_url": pdf_url
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Error parsing PDF: {str(e)}", 
            "pdf_url": pdf_url
        }
