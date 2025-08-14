from typing import Any, Dict, List

import requests


def fetch_osf_providers() -> List[Dict[str, Any]]:
    """Fetch current list of valid OSF preprint providers from API"""
    url = "https://api.osf.io/v2/preprint_providers/"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Create provider objects from the response
    providers = []
    for provider in data["data"]:
        provider_obj = {
            "id": provider["id"],
            "type": "osf",
            "description": provider["attributes"]["description"],
            "taxonomies": provider["relationships"]["taxonomies"]["links"]["related"]["href"],
            "preprints": provider["relationships"]["preprints"]["links"]["related"]["href"],
        }
        providers.append(provider_obj)

    return sorted(providers, key=lambda p: p["id"])


def get_external_providers() -> List[Dict[str, Any]]:
    """Get list of external (non-OSF) preprint providers"""
    return [
        {
            "id": "arxiv",
            "type": "standalone",
            "description": "arXiv is a free distribution service and an open-access archive for scholarly articles in physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering and systems science, and economics.",
        },
        {
            "id": "openalex",
            "type": "standalone",
            "description": "OpenAlex is a comprehensive index of scholarly works across all disciplines.",
        },
    ]


def get_all_providers() -> List[Dict[str, Any]]:
    """Get combined list of all available providers"""
    osf_providers = fetch_osf_providers()
    external_providers = get_external_providers()
    all_providers = osf_providers + external_providers
    return sorted(all_providers, key=lambda p: p["id"].lower())


def validate_provider(provider_id: str) -> bool:
    """Validate if a provider ID exists in the given providers list"""
    valid_ids = [p["id"] for p in get_all_providers()]
    return provider_id in valid_ids
