import re
from typing import Any, Dict, Optional
from urllib.parse import quote, urlencode
import os
import tempfile

import requests
import fitz  # PyMuPDF
import pymupdf4llm as pdfmd

from .providers import fetch_osf_providers, validate_provider


def clean_api_text(text: str, max_length: int = 200) -> str:
    """
    Args:
        text: The text to clean
        max_length: Maximum allowed length (default 200)
        
    Returns:
        Cleaned text suitable for API queries
    """
    if not text:
        return text
    
    # Remove or replace problematic characters
    cleaned = text
    
    # Replace various quote types with simple quotes or remove them
    cleaned = cleaned.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
    
    # Remove or replace other problematic special characters
    cleaned = cleaned.replace('&nbsp;', ' ')  # Non-breaking space
    cleaned = cleaned.replace('\u00a0', ' ')  # Unicode non-breaking space
    cleaned = cleaned.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')  # Line breaks and tabs
    
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Handle length limits
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length-3] + "..."
    
    # Remove or replace characters that commonly cause URL encoding issues
    problematic_chars = ['<', '>', '{', '}', '|', '\\', '^', '`', '[', ']']
    for char in problematic_chars:
        cleaned = cleaned.replace(char, '')
    
    # Replace colons which seem to cause OSF API issues
    cleaned = cleaned.replace(':', ' -')
    
    # Replace other potentially problematic punctuation
    cleaned = cleaned.replace(';', ',')  # Semicolons to commas
    cleaned = cleaned.replace('?', '')   # Remove question marks
    cleaned = cleaned.replace('!', '')   # Remove exclamation marks
    cleaned = cleaned.replace('#', '')   # Remove hashtags
    cleaned = cleaned.replace('%', '')   # Remove percent signs
    
    # Clean up any double spaces created by replacements
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


async def extract_pdf_to_markdown(file_input, filename: Optional[str] = None, write_images: bool = False) -> str:
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


def fetch_osf_preprints(
    provider_id: Optional[str] = None,
    subjects: Optional[str] = None,
    date_published_gte: Optional[str] = None,
) -> Dict[str, Any]:
    """
    NOTE: The OSF API only supports a limited set of filters. Many common filters
    like title, DOI, creator, etc. are NOT supported by the OSF API.
    
    Args:
        provider_id: The provider ID (e.g., 'psyarxiv', 'socarxiv')
        subjects: Subject filter (e.g., 'psychology', 'neuroscience') 
        date_published_gte: Published date greater than or equal to (YYYY-MM-DD)
        is_published: Filter by publication status (true/false)
    
    Returns:
        Dictionary containing preprints data from OSF API
    """
    # Validate provider if specified
    if provider_id:
        osf_providers = fetch_osf_providers()
        if not validate_provider(provider_id, osf_providers):
            valid_ids = [p["id"] for p in osf_providers]
            raise ValueError(f"Invalid OSF provider: {provider_id}. Valid OSF providers: {valid_ids}")

    # Build query parameters (only using OSF API supported filters)
    filters = {}
    
    if provider_id:
        filters["filter[provider]"] = clean_api_text(provider_id, max_length=50)
    if subjects:
        filters["filter[subjects]"] = clean_api_text(subjects, max_length=100)
    if date_published_gte:
        filters["filter[date_published][gte]"] = date_published_gte  # Dates don't need cleaning

    # Build URL with filters
    base_url = "https://api.osf.io/v2/preprints/"
    if filters:
        query_string = urlencode(filters, safe='', quote_via=quote)
        url = f"{base_url}?{query_string}"
    else:
        url = base_url

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            if len(filters) > 1:
                simple_filters = {}
                if provider_id:
                    simple_filters["filter[provider]"] = clean_api_text(provider_id, max_length=50)
                
                simple_query = urlencode(simple_filters, safe='', quote_via=quote)
                simple_url = f"{base_url}?{simple_query}"
                
                try:
                    simple_response = requests.get(simple_url, timeout=30)
                    simple_response.raise_for_status()
                    result = simple_response.json()
                    
                    # Add a note about the simplified search
                    if 'meta' not in result:
                        result['meta'] = {}
                    result['meta']['search_note'] = f"Original search failed (400 error), showing all results for provider '{provider_id}'. You may need to filter results manually."
                    return result
                except:
                    pass
            
            raise ValueError(f"Bad request (400) - The search parameters may be invalid. Original error: {str(e)}")
        else:
            raise e
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Request failed: {str(e)}")


def fetch_single_osf_preprint_metadata(preprint_id: str) -> Dict[str, Any]:
    try:
        preprint_url = f'https://api.osf.io/v2/preprints/{preprint_id}'
        response = requests.get(preprint_url, timeout=30)
        response.raise_for_status()
        preprint_data= response.json()

        primary_file_url = preprint_data['data']['relationships']['primary_file']['links']['related']['href']
        file_response = requests.get(primary_file_url, timeout=30)
        file_response.raise_for_status()
        file_data = file_response.json()
        
        # Get the download URL
        download_url = file_data['data']['links']['download']
        
        # Prepare metadata first
        attributes = preprint_data['data']['attributes']
        metadata = {
            "id": preprint_id,
            "title": attributes.get('title', ''),
            "description": attributes.get('description', ''),
            "date_created": attributes.get('date_created', ''),
            "date_published": attributes.get('date_published', ''),
            "date_modified": attributes.get('date_modified', ''),
            "is_published": attributes.get('is_published', False),
            "is_preprint_orphan": attributes.get('is_preprint_orphan', False),
            "license_record": attributes.get('license_record', {}),
            "doi": attributes.get('doi', ''),
            "tags": attributes.get('tags', []),
            "subjects": attributes.get('subjects', []),
            "download_url": download_url
        }
        
        if not download_url:
            return {
                "status": "error",
                "message": "Download URL not available",
                "metadata": metadata
            }
        
        return metadata
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch preprint metadata: {str(e)}")


async def download_osf_preprint_and_parse_to_markdown(preprint_id):
    """
    Download a specific preprint PDF by ID and parse it to markdown.
    Returns paper metadata along with markdown content.
    """
    temp_file = None
    metadata = {}  # Initialize metadata to avoid undefined variable errors
    try:
        # Get preprint metadata using helper function
        preprint_data = fetch_single_osf_preprint_metadata(preprint_id)
        
        # If fetch_single_osf_preprint_metadata returns an error dict, handle it
        if isinstance(preprint_data, dict) and preprint_data.get('status') == 'error':
            return preprint_data
        
        # Extract metadata for error handling
        metadata = preprint_data
        
        # Download the PDF to a temporary file
        pdf_response = requests.get(preprint_data['download_url'], timeout=60)
        pdf_response.raise_for_status()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_response.content)
            temp_file_path = temp_file.name
        
        # Parse PDF to markdown using pymupdf4llm
        try:
            markdown_content = await extract_pdf_to_markdown(temp_file_path, write_images=False)
            
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
        # Error from fetch_single_osf_preprint helper function
        return {
            "status": "error", 
            "message": str(e),
            "metadata": {}
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error", 
            "message": f"Network error: {str(e)}",
            "metadata": metadata if 'metadata' in locals() else {}
        }
    except KeyError as e:
        return {
            "status": "error",
            "message": f"Unexpected API response structure: {str(e)}",
            "metadata": metadata if 'metadata' in locals() else {}
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing preprint: {str(e)}",
            "metadata": metadata if 'metadata' in locals() else {}
        }
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass  # Ignore cleanup errors
