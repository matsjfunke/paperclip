from typing import Any, Dict
from urllib.parse import quote

import requests

from .providers import fetch_osf_providers, validate_provider


def fetch_osf_preprints(provider_id: str) -> Dict[str, Any]:
    """Fetch preprints metadata for a specific OSF provider"""
    # Validate provider exists in OSF providers
    osf_providers = fetch_osf_providers()
    if not validate_provider(provider_id, osf_providers):
        valid_ids = [p["id"] for p in osf_providers]
        raise ValueError(f"Invalid OSF provider: {provider_id}. Valid OSF providers: {valid_ids}")

    # Build query parameter and encode it
    param = quote("filter[provider]")
    url = f"https://api.osf.io/v2/preprints/?{param}={quote(provider_id)}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
