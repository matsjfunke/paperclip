from typing import Annotated
import asyncio

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
from prompts import prompt_mcp
from tools import tools_mcp

mcp = FastMCP(
    name="Paperclip MCP Server",
    instructions="""
        This server provides tools to search, retrieve, and read academic papers from multiple sources.
        - Search papers across providers with filters for query text, subjects, and publication date
        - Read full paper content in markdown format
        - Retrieve paper metadata without downloading content (e.g. title, authors, abstract, publication date, journal info, and download URLs)
    """,
)


# Import subservers
async def setup():
    await mcp.import_server(prompt_mcp, prefix="prompt")
    await mcp.import_server(tools_mcp, prefix="research")

if __name__ == "__main__":
    asyncio.run(setup())
    mcp.run(transport="http", host="0.0.0.0", port=8000)
