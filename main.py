from fastmcp import FastMCP

from core import fetch_osf_preprints, get_all_providers

app = FastMCP("paperclip MCP Server")


@app.tool
def list_preprint_providers() -> dict:
    """
    Get the complete list of all available preprint providers (OSF + external).

    Returns:
        Dictionary containing the list of all provider objects and total count
    """
    providers = get_all_providers()

    return {
        "providers": providers,
        "total_count": len(providers),
    }


@app.tool
def get_preprint(
    provider: str,
) -> dict:
    """
    Get metadata for preprints from an OSF provider.

    Args:
        provider: The provider of the paper. Use list_preprint_providers() to see available OSF providers.
    """
    return fetch_osf_preprints(provider)


if __name__ == "__main__":
    app.run(transport="http", host="0.0.0.0", port=8000)
