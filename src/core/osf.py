from typing import Any, Dict, Optional
from urllib.parse import quote, urlencode

import requests

from utils import sanitize_api_queries

from .providers import fetch_osf_providers, validate_provider


def fetch_osf_preprints(
    provider_id: Optional[str] = None,
    subjects: Optional[str] = None,
    date_published_gte: Optional[str] = None,
    query: Optional[str] = None,
) -> Dict[str, Any]:
    """
    NOTE: The OSF API only supports a limited set of filters. Many common filters
    like title, DOI, creator, etc. are NOT supported by the OSF API.

    When query is provided, uses the trove search endpoint which supports full-text search.

    Args:
        provider_id: The provider ID (e.g., 'psyarxiv', 'socarxiv')
        subjects: Subject filter (e.g., 'psychology', 'neuroscience')
        date_published_gte: Published date greater than or equal to (YYYY-MM-DD)
        query: Text search query for title, author, content (uses trove endpoint)

    Returns:
        Dictionary containing preprints data from OSF API or trove search
    """
    # If query is provided, use trove search endpoint
    if query:
        return fetch_osf_preprints_via_trove(query, provider_id)

    # Build query parameters (only using OSF API supported filters)
    filters = {}

    if provider_id:
        filters["filter[provider]"] = sanitize_api_queries(provider_id, max_length=50)
    if subjects:
        filters["filter[subjects]"] = sanitize_api_queries(subjects, max_length=100)
    if date_published_gte:
        filters["filter[date_published][gte]"] = date_published_gte  # Dates don't need cleaning

    # Build URL with filters
    base_url = "https://api.osf.io/v2/preprints/"
    if filters:
        query_string = urlencode(filters, safe="", quote_via=quote)
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
                    simple_filters["filter[provider]"] = sanitize_api_queries(provider_id, max_length=50)

                simple_query = urlencode(simple_filters, safe="", quote_via=quote)
                simple_url = f"{base_url}?{simple_query}"

                try:
                    simple_response = requests.get(simple_url, timeout=30)
                    simple_response.raise_for_status()
                    result = simple_response.json()

                    # Add a note about the simplified search
                    if "meta" not in result:
                        result["meta"] = {}
                    result["meta"][
                        "search_note"
                    ] = f"Original search failed (400 error), showing all results for provider '{provider_id}'. You may need to filter results manually."
                    return result
                except:
                    pass

            raise ValueError(f"Bad request (400) - The search parameters may be invalid. Original error: {str(e)}")
        else:
            raise e
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Request failed: {str(e)}")


def fetch_osf_preprints_via_trove(query: str, provider_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch preprints using the trove search endpoint and transform to standard format.
    """
    from urllib.parse import quote_plus

    # Build trove search URL
    base_url = "https://share.osf.io/trove/index-card-search"
    params = {
        "cardSearchFilter[resourceType]": "Preprint",
        "cardSearchText[*,creator.name,isContainedBy.creator.name]": sanitize_api_queries(query, max_length=200),
        "page[size]": "20",  # Match our default page size
        "sort": "-relevance",
    }

    # Validate provider if specified (we'll filter results later)
    if provider_id:
        if not validate_provider(provider_id):
            osf_providers = fetch_osf_providers()
            valid_ids = [p["id"] for p in osf_providers]
            raise ValueError(f"Invalid OSF provider: {provider_id}. Valid OSF providers: {valid_ids}")

    # Build query string manually to handle complex parameter names
    query_parts = []
    for key, value in params.items():
        query_parts.append(f"{quote_plus(key)}={quote_plus(str(value))}")
    query_string = "&".join(query_parts)
    url = f"{base_url}?{query_string}"

    try:
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        trove_data = response.json()

        # Transform trove format to standard OSF API format
        transformed_data = []
        for item in trove_data.get("data", []):
            # Extract OSF ID from @id field
            osf_id = ""
            if "@id" in item and "osf.io/" in item["@id"]:
                osf_id = item["@id"].split("/")[-1]

            # Filter by provider if specified
            if provider_id:
                # Check if this item is from the specified provider
                publisher_info = item.get("publisher", [])
                if isinstance(publisher_info, list) and len(publisher_info) > 0:
                    publisher_id = publisher_info[0].get("@id", "")
                    # Extract provider ID from publisher URL (e.g., "https://osf.io/preprints/psyarxiv" -> "psyarxiv")
                    if provider_id not in publisher_id:
                        continue  # Skip this item if it doesn't match the provider
                else:
                    continue  # Skip if no publisher info

            # Transform to standard format
            transformed_item = {
                "id": osf_id,
                "type": "preprints",
                "attributes": {
                    "title": extract_first_value(item.get("title", [])),
                    "description": extract_first_value(item.get("description", [])),
                    "date_created": extract_first_value(item.get("dateCreated", [])),
                    "date_published": extract_first_value(item.get("dateAccepted", [])),
                    "date_modified": extract_first_value(item.get("dateModified", [])),
                    "doi": extract_doi_from_identifiers(item.get("identifier", [])),
                    "tags": [kw.get("@value", "") for kw in item.get("keyword", [])],
                    "subjects": [subj.get("prefLabel", [{}])[0].get("@value", "") for subj in item.get("subject", [])],
                },
                "relationships": {},
                "links": {"self": item.get("@id", "")},
            }
            transformed_data.append(transformed_item)

        # Return in standard OSF API format
        return {
            "data": transformed_data,
            "meta": {
                "version": "2.0",  # Match OSF API version
                "total": trove_data.get("meta", {}).get("total", len(transformed_data)),
                "search_note": f"Results from trove search for query: '{query}'",
            },
            "links": {
                "first": trove_data.get("links", {}).get("first", ""),
                "next": trove_data.get("links", {}).get("next", ""),
                "last": "",
                "prev": "",
                "meta": "",
            },
        }

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Trove search failed: {str(e)}")


def extract_first_value(field_list):
    """Extract the first @value from a field list."""
    if isinstance(field_list, list) and len(field_list) > 0:
        if isinstance(field_list[0], dict) and "@value" in field_list[0]:
            return field_list[0]["@value"]
        elif isinstance(field_list[0], str):
            return field_list[0]
    return ""


def extract_doi_from_identifiers(identifiers):
    """Extract DOI from identifier list."""
    for identifier in identifiers:
        if isinstance(identifier, dict) and "@value" in identifier:
            value = identifier["@value"]
            if "doi.org" in value or value.startswith("10."):
                return value
    return ""


def fetch_single_osf_preprint_metadata(preprint_id: str) -> Dict[str, Any]:
    try:
        preprint_url = f"https://api.osf.io/v2/preprints/{preprint_id}"
        response = requests.get(preprint_url, timeout=30)
        response.raise_for_status()
        preprint_data = response.json()

        primary_file_url = preprint_data["data"]["relationships"]["primary_file"]["links"]["related"]["href"]
        file_response = requests.get(primary_file_url, timeout=30)
        file_response.raise_for_status()
        file_data = file_response.json()

        # Get the download URL
        download_url = file_data["data"]["links"]["download"]

        # Prepare metadata first
        attributes = preprint_data["data"]["attributes"]
        metadata = {
            "id": preprint_id,
            "title": attributes.get("title", ""),
            "description": attributes.get("description", ""),
            "date_created": attributes.get("date_created", ""),
            "date_published": attributes.get("date_published", ""),
            "date_modified": attributes.get("date_modified", ""),
            "is_published": attributes.get("is_published", False),
            "is_preprint_orphan": attributes.get("is_preprint_orphan", False),
            "license_record": attributes.get("license_record", {}),
            "doi": attributes.get("doi", ""),
            "tags": attributes.get("tags", []),
            "subjects": attributes.get("subjects", []),
            "download_url": download_url,
        }

        if not download_url:
            return {"status": "error", "message": "Download URL not available", "metadata": metadata}

        return metadata
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch preprint metadata: {str(e)}")
