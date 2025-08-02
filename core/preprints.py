import re
from typing import Any, Dict, Optional
from urllib.parse import quote, urlencode

import requests

from .providers import fetch_osf_providers, validate_provider


def clean_api_text(text: str, max_length: int = 200) -> str:
    """
    Clean text input for API compatibility by removing/replacing problematic characters.
    
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


def fetch_osf_preprints(
    provider_id: Optional[str] = None,
    subjects: Optional[str] = None,
    date_published_gte: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fetch preprints metadata from OSF with supported filtering options.
    
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
            # Try a simpler search if the complex one fails
            if len(filters) > 1:
                # Retry with just the provider filter to see if that works
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
