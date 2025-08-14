"""
Core package for paperclip MCP server.
"""

from .arxiv import (
    download_arxiv_paper_and_parse_to_markdown,
    fetch_arxiv_papers,
    fetch_single_arxiv_paper_metadata,
)
from .osf import (
    download_osf_preprint_and_parse_to_markdown,
    fetch_osf_preprints,
    fetch_osf_providers,
    fetch_single_osf_preprint_metadata,
)


from .providers import get_all_providers, validate_provider, fetch_osf_providers

__all__ = [
    "fetch_arxiv_papers",
    "fetch_osf_preprints",
    "fetch_osf_providers",
    "fetch_single_arxiv_paper_metadata",
    "fetch_single_osf_preprint_metadata",
    "download_arxiv_paper_and_parse_to_markdown",
    "download_osf_preprint_and_parse_to_markdown",
    "get_all_providers",
    "validate_provider",
    "fetch_osf_providers",
]
