# Paperclip MCP Server

An Model Context Protocol (MCP) Server for searching & retrieving research papers.

## Architecture

A python based mcp server build with FastAPI and FastMCP find docs via [fast-mcp.txt](fast-mcp.txt) framework.

Deployed to a VPS using Docker Swarm run locally with Docker Compose.

Traefik as reverse proxy.

## Development Setup

### Prerequisites

- Python 3.12+
- pip

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd paperclip
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server with Hot Reload

```bash
# Run with hot reload
watchmedo auto-restart --patterns="*.py" --recursive -- python main.py
```

The server will automatically restart when you make changes to any `.py` files.

### Testing

Use the [MCP Inspector](https://inspector.modelcontextprotocol.io/) to interact with the server.

```bash
pnpx @modelcontextprotocol/inspector
```