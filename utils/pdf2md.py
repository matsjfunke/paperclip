"""
PDF processing utilities using pymupdf4llm.
"""

import os
from typing import Optional

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
        
        elif hasattr(file_input, 'read'):
            # File object (like FastAPI UploadFile)
            temp_filename = filename or getattr(file_input, 'filename', 'temp_pdf.pdf')
            temp_path = f"/tmp/{temp_filename}"
            
            # Handle both sync and async file objects
            if hasattr(file_input, '__aiter__') or hasattr(file_input.read, '__call__'):
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