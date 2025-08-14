from typing import Annotated

from fastmcp import FastMCP

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
        This server provides tools to interact with academic preprint papers.
        Call list_preprint_providers() to get the complete list of all available preprint providers via the paperclip MCP server.
        Call search_preprints() to search for preprints using OSF API supported filters.
    """,
)


@mcp.tool(
    name="list_preprint_providers",
    description="Get the complete list of all available preprint providers via the paperclip MCP server.",
)
async def list_preprint_providers() -> dict:
    """
    Call the osf api and hardcode other supported providers.

    """
    providers = get_all_providers()

    return {
        "providers": providers,
        "total_count": len(providers),
    }


@mcp.tool(
    name="search_preprints",
    description="Search for preprints using supported filters. And get its metadata.",
)
async def search_preprints(
    query: Annotated[str | None, "Text search query for title, author, content"] = None,
    provider: Annotated[str | None, "Provider ID to filter preprints (e.g., psyarxiv, socarxiv, arxiv)"] = None,
    subjects: Annotated[str | None, "Subject categories to filter by (e.g., psychology, neuroscience)"] = None,
    date_published_gte: Annotated[str | None, "Filter preprints published on or after this date (e.g., 2024-01-01)"] = None,
) -> dict:
    if provider and provider not in [p["id"] for p in get_all_providers()]:
        return {
            "error": f"Provider: {provider} not found. Please use list_preprint_providers to get the complete list of all available providers.",
        }
    if not provider:
        return {
            "error": "TODO implement search across all providers",
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
    description="Retrieve the content of a preprint paper by its ID (which can be found by the search_preprints tool).",
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
    name="get_paper_by_url",
    description="Retrieve the paper content as markdown from a PDF URL. Provide the direct URL (pdf_url, primary_location_url) to a PDF file.",
)
async def get_paper_by_url(pdf_url: str) -> dict:
    return await download_pdf_and_parse_to_markdown(pdf_url)


@mcp.tool(
    name="get_paper_metadata",
    description="Retrieve the metadata of a preprint paper by its ID (which can be found by the search_preprints tool).",
)
async def get_paper_metadata(preprint_id: str) -> dict:
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
    mcp.run(transport="http", host="0.0.0.0", port=8000)
