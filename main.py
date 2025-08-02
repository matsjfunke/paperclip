import tempfile
import os
from typing import Optional
from urllib.parse import quote


import fitz
import requests
from fastmcp import FastMCP

app = FastMCP("paperclip MCP Server")

def get_osf_providers() -> list:
    """Fetch current list of valid OSF preprint providers"""
    url = "https://api.osf.io/v2/preprint_providers/"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    # Create provider objects from the response
    providers = []
    for provider in data['data']:
        provider_obj = {
            'id': provider['id'],
            'type': "osf",
            'description': provider['attributes']['description'],
            'taxonomies': provider['relationships']['taxonomies']['links']['related']['href'],
            'preprints': provider['relationships']['preprints']['links']['related']['href']
        }
        providers.append(provider_obj)
    print(providers)
    return sorted(providers, key=lambda p: p['id'])

def get_osf_provider_preprints_metadata(provider: str):
    # Get current valid providers
    valid_providers = get_osf_providers()
    
    # Extract provider IDs for validation
    valid_provider_ids = [p['id'] for p in valid_providers]
    
    # Validate provider
    if provider not in valid_provider_ids:
        raise ValueError(f"Invalid provider: {provider}. Allowed providers: {valid_provider_ids}")

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
        Dictionary containing the list of provider objects and total count
    """
    osf_providers = get_osf_providers()
    
    # Add the additional providers as simple objects
    # additional_providers = [
    #     {"id": "arxiv", "type": "external", "description": "ArXiv preprint server"},
    #     {"id": "biorxiv", "type": "external", "description": "BioRxiv preprint server"},
    #     {"id": "medrxiv", "type": "external", "description": "MedRxiv preprint server"},
    #     {"id": "chemrxiv", "type": "external", "description": "ChemRxiv preprint server"}
    # ]
    # all_providers = osf_providers + additional_providers

    return {
        "providers": sorted(osf_providers, key=lambda p: p['id'].lower()),
        "total_count": len(osf_providers),
    }

@app.tool
def get_preprint(
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
