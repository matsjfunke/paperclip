from fastmcp import FastMCP


prompt_mcp = FastMCP()

@prompt_mcp.prompt
def find_attention_is_all_you_need() -> str:
    """finds the Attention is all you need paper in arxiv."""
    return "Search for Attention is all you need in arxiv"
