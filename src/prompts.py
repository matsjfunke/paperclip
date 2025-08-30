from fastmcp import FastMCP


prompt_mcp = FastMCP()

@prompt_mcp.prompt  
def list_paper_providers() -> str:
    """List all available paper providers."""
    return "List all available paper providers."

@prompt_mcp.prompt
def find_attention_is_all_you_need() -> str:
    """Finds the Attention is all you need paper in arxiv."""
    return "Search for Attention is all you need in arxiv"

@prompt_mcp.prompt
def get_paper_by_id() -> str:
    """Prompt to use the get_paper_by_id tool."""
    return "Retrieve the full content (including abstract, sections, and references) of the paper with ID: 1706.03762"

@prompt_mcp.prompt
def get_paper_metadata_by_id() -> str:
    """Prompt to use the get_paper_metadata_by_id tool."""
    return "Retrieve the metadata of the paper with ID: 1706.03762"

@prompt_mcp.prompt
def get_paper_by_url() -> str:
    """Prompt to use the get_paper_by_url tool."""
    return "Retrieve the full content (including abstract, sections, and references) of the paper with URL: https://arxiv.org/pdf/1706.03762"