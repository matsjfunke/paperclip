# Paperclip MCP Server

An Model Context Protocol (MCP) Server for searching & retrieving research papers.

## Architecture

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
watchmedo auto-restart --patterns="*.py" --recursive -- python server.py
# Run Server using fastmcp
fastmcp run server.py --transport http --host 0.0.0.0 --port 8000      
```

The server will automatically restart when you make changes to any `.py` files.

### Testing

Use the [MCP Inspector](https://inspector.modelcontextprotocol.io/) to interact with the server.

```bash
pnpx @modelcontextprotocol/inspector
```

## Preprint Providers to be added

[List of preprint repositorys](https://en.wikipedia.org/wiki/List_of_preprint_repositories)

- bioRxiv & medRxiv both share the underlying api structure (https://api.biorxiv.org/pubs/[server]/[interval]/[cursor] where [server] can be "biorxiv" or "medrxiv")
- ChemRxiv
- [hal open science](https://hal.science/?lang=en)
- [research square](https://www.researchsquare.com/)
- [osf preprints](https://osf.io/preprints)
- [preprints.org](https://preprints.org)
- [science open](https://www.scienceopen.com/)
- [SSRN](https://www.ssrn.com/index.cfm/en/the-lancet/)
- [synthical](https://synthical.com/feed/new)
