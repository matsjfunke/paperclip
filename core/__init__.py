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
    download_preprint_pdf
)

__all__ = [
    "fetch_osf_providers",
    "get_external_providers",
    "get_all_providers", 
    "validate_provider",
    "fetch_osf_preprints",
    "download_preprint_pdf"
]