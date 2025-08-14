"""
Core package for paperclip MCP server.
"""

from .arxiv import (
    fetch_arxiv_papers,
    fetch_single_arxiv_paper_metadata,
)
from .osf import (
    fetch_osf_preprints,
    fetch_osf_providers,
    fetch_single_osf_preprint_metadata,
)
from .openalex import (
    fetch_openalex_papers,
    fetch_single_openalex_paper_metadata,
)


from .providers import get_all_providers, validate_provider, fetch_osf_providers

__all__ = [
    "fetch_arxiv_papers",
    "fetch_osf_preprints",
    "fetch_osf_providers",
    "fetch_single_arxiv_paper_metadata",
    "fetch_single_osf_preprint_metadata",
    "fetch_openalex_papers",
    "fetch_single_openalex_paper_metadata",
    "get_all_providers",
    "validate_provider",
    "fetch_osf_providers",
]
