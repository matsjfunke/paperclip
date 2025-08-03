"""
Core package for paperclip MCP server.
"""

from .providers import (
    fetch_osf_providers,
    get_external_providers, 
    get_all_providers,
    validate_provider
)

from .preprints import (
    fetch_osf_preprints,
    fetch_single_osf_preprint_metadata,
    download_osf_preprint_and_parse_to_markdown
)

__all__ = [
    "fetch_osf_providers",
    "get_external_providers",
    "get_all_providers", 
    "validate_provider",
    "fetch_osf_preprints",
    "fetch_single_osf_preprint_metadata",
    "download_osf_preprint_and_parse_to_markdown"
]