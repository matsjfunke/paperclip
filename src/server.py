from typing import Annotated

from fastmcp import FastMCP
from prompts import prompt_mcp
import asyncio

from core import (
    fetch_arxiv_papers,
    fetch_openalex_papers,
    fetch_osf_preprints,
    fetch_single_arxiv_paper_metadata,
    fetch_single_openalex_paper_metadata,
    fetch_single_osf_preprint_metadata,
    fetch_osf_providers,
    get_all_providers,
)
from utils.pdf2md import download_pdf_and_parse_to_markdown, download_paper_and_parse_to_markdown, extract_pdf_to_markdown

mcp = FastMCP(
    name="Paperclip MCP Server",
    instructions="""
        This server provides tools to search, retrieve, and read academic papers from multiple sources.
        - Search papers across providers with filters for query text, subjects, and publication date
        - Read full paper content in markdown format
        - Retrieve paper metadata without downloading content (e.g. title, authors, abstract, publication date, journal info, and download URLs)
    """,
)


@mcp.tool(
    name="list_providers",
    description="Get the complete list of all available academic paper providers. Includes preprint servers (ArXiv, Open Science Framework (OSF) discipline-specific servers). Returns provider IDs for use with search_papers.",
)
async def list_providers() -> dict:
    """
    Call the osf api and hardcode other supported providers.

    """
    providers = get_all_providers()

    return {
        "providers": providers,
        "total_count": len(providers),
    }


@mcp.tool(
    name="search_papers",
    description="Find papers using supported filters. And retrieve their metadata.",
)
async def search_papers(
    query: Annotated[str | None, "Text search query for title, author, content"] = None,
    provider: Annotated[str | None, "Provider ID to filter preprints (e.g., psyarxiv, socarxiv, arxiv, openalex, osf)"] = None,
    subjects: Annotated[str | None, "Subject categories to filter by (e.g., psychology, neuroscience)"] = None,
    date_published_gte: Annotated[str | None, "Filter preprints published on or after this date (e.g., 2024-01-01)"] = None,
) -> dict:
    if provider and provider not in [p["id"] for p in get_all_providers()]:
        return {
            "error": f"Provider: {provider} not found. Please use list_preprint_providers to get the complete list of all available providers.",
        }
    if not provider:
        all_results = []
        
        arxiv_results = fetch_arxiv_papers(query=query, category=subjects)
        all_results.append(arxiv_results)
    
        openalex_results = fetch_openalex_papers(
            query=query, 
            concepts=subjects, 
            date_published_gte=date_published_gte
        )
        all_results.append(openalex_results)
    
        osf_results = fetch_osf_preprints(
            provider_id="osf",
            subjects=subjects,
            date_published_gte=date_published_gte,
            query=query,
        )
        all_results.append(osf_results)
        
        return {
            "papers": all_results,
            "total_count": len(all_results),
            "providers_searched": ["arxiv", "openalex", "osf"],
        }
    if provider == "osf" or provider in [p["id"] for p in fetch_osf_providers()]:
        return fetch_osf_preprints( provider_id=provider,
            subjects=subjects,
            date_published_gte=date_published_gte,
            query=query,
        )
    elif provider == "arxiv":
        return fetch_arxiv_papers(
            query=query,
            category=subjects,
        )
    elif provider == "openalex":
        return fetch_openalex_papers(
            query=query,
            concepts=subjects,
            date_published_gte=date_published_gte,
        )


@mcp.tool(
    name="get_paper_by_id",
    description="Download and convert an academic paper to markdown format by its ID. Returns full paper content including title, abstract, sections, and references. Supports ArXiv (e.g., '2407.06405v1'), OpenAlex (e.g., 'W4385245566'), and OSF IDs.",
)
async def get_paper_by_id(paper_id: str) -> dict:
    try:
        # Check if it's an OpenAlex paper ID (starts with 'W' followed by numbers)
        if paper_id.startswith("W") and paper_id[1:].isdigit():
            # OpenAlex paper ID format (e.g., "W4385245566")
            metadata = fetch_single_openalex_paper_metadata(paper_id)
            return await download_paper_and_parse_to_markdown(
                metadata=metadata,
                pdf_url_field="pdf_url",
                paper_id=paper_id,
                write_images=False
            )
        # Check if it's an arXiv paper ID (contains 'v' followed by version number or matches arXiv format)
        elif "." in paper_id and ("v" in paper_id or len(paper_id.split(".")[0]) == 4):
            # arXiv paper ID format (e.g., "2407.06405v1" or "cs.AI/0001001")
            metadata = fetch_single_arxiv_paper_metadata(paper_id)
            return await download_paper_and_parse_to_markdown(
                metadata=metadata,
                pdf_url_field="download_url",
                paper_id=paper_id,
                write_images=False
            )
        else:
            # OSF paper ID format
            metadata = fetch_single_osf_preprint_metadata(paper_id)
            # Handle error case from OSF metadata function
            if isinstance(metadata, dict) and metadata.get("status") == "error":
                return metadata
            return await download_paper_and_parse_to_markdown(
                metadata=metadata,
                pdf_url_field="download_url",
                paper_id=paper_id,
                write_images=False
            )
    except ValueError as e:
        return {"status": "error", "message": str(e), "metadata": {}}

@mcp.tool(
    name="get_paper_content_by_url",
    description="Download and convert a PDF paper to markdown format from a direct PDF URL. Returns full paper content parsed from the PDF including title, abstract, sections, and references.",
)
async def get_paper_content_by_url(pdf_url: str) -> dict:
    return await download_pdf_and_parse_to_markdown(pdf_url)


@mcp.tool(
    name="get_paper_metadata_by_id",
    description="Get metadata for an academic paper by its ID without downloading full content. Returns title, authors, abstract, publication date, journal info, and download URLs. Supports ArXiv, OpenAlex, and OSF IDs.",
)
async def get_paper_metadata_by_id(preprint_id: str) -> dict:
    # Check if it's an OpenAlex paper ID (starts with 'W' followed by numbers)
    if preprint_id.startswith("W") and preprint_id[1:].isdigit():
        # OpenAlex paper ID format (e.g., "W4385245566")
        return fetch_single_openalex_paper_metadata(preprint_id)
    # Check if it's an arXiv paper ID (contains 'v' followed by version number or matches arXiv format)
    elif "." in preprint_id and ("v" in preprint_id or len(preprint_id.split(".")[0]) == 4):
        # arXiv paper ID format (e.g., "2407.06405v1" or "cs.AI/0001001")
        return fetch_single_arxiv_paper_metadata(preprint_id)
    else:
        # OSF paper ID format
        return fetch_single_osf_preprint_metadata(preprint_id)


if __name__ == "__main__":
    async def setup():
        await mcp.import_server(prompt_mcp, prefix="prompt")

    asyncio.run(setup())
    mcp.run(transport="http", host="0.0.0.0", port=8000)
