from typing import Annotated
from fastmcp import FastMCP

from core import fetch_osf_preprints, get_all_providers, download_preprint_pdf

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
    description="Search for preprints using supported filters.",
)
async def search_preprints(
    provider: Annotated[str | None, "Provider ID to filter preprints (e.g., psyarxiv, socarxiv, biohackrxiv)"] = None,
    subjects: Annotated[str | None, "Subject categories to filter by (e.g., psychology, neuroscience)"] = None,
    date_published_gte: Annotated[str | None, "Filter preprints published on or after this date (e.g., 2024-01-01)"] = None,
) -> dict:
    return fetch_osf_preprints(
        provider_id=provider,
        subjects=subjects,
        date_published_gte=date_published_gte,
    )

@mcp.tool(
    name="download_preprint_pdf",
    description="Download a specific preprint PDF by ID",
)
async def download_preprint_paper_pdf(preprint_id: str) -> dict:
    return download_preprint_pdf(preprint_id)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
