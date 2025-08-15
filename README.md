<div align="center">
  <img src="assets/paperclip.svg" alt="Paperclip Logo" width="48" height="48">
  
  # Paperclip MCP Server
</div>

> 📎 Paperclip is a Model Context Protocol (MCP) server that enables searching and retrieving research papers from Arxiv, the Open Science Framework (OSF) API, and OpenAlex.

## Getting Started

Setup the paperclip MCP server in your host via the server url `https://paperclip.matsjfunke.com/mcp` no authentication is needed.

Example JSON for cursor:

```json
{
  "mcpServers": {
    "paperclip": {
      "url": "https://paperclip.matsjfunke.com/mcp"
    }
  }
}
```

**Paperclip Usage:**

Crusor:

![Cursor Usage](assets/cursor-usage.png)

Langdock:

![Paperclip usage in Langdock](assets/langdock-usage.png)

## Supported Paper providers

- [AfricArXiv](https://africarxiv.org)
- [AgriXiv](https://agrirxiv.org)
- [ArabXiv](https://arabixiv.org)
- [arXiv](https://arxiv.org)
- [BioHackrXiv](http://guide.biohackrxiv.org/about.html)
- [BodoArXiv](https://bodoarxiv.wordpress.com)
- [COP Preprints](https://www.collegeofphlebology.com)
- [EarthArXiv](https://eartharxiv.org)
- [EcoEvoRxiv](https://www.ecoevorxiv.com)
- [ECSarxiv](https://ecsarxiv.org)
- [EdArXiv](https://edarxiv.org)
- [EngrXiv](https://engrxiv.org)
- [FocusArchive](https://osf.io/preprints/focusarchive)
- [Frenxiv](https://frenxiv.org)
- [INArxiv](https://rinarxiv.lipi.go.id)
- [IndiaRxiv](https://osf.io/preprints/indiarxiv)
- [Law Archive](https://library.law.yale.edu/research/law-archive)
- [LawArXiv](https://osf.io/preprints/lawarxiv)
- [LISSA](https://osf.io/preprints/lissa)
- [LiveData](https://osf.io/preprints/livedata)
- [MarXiv](https://osf.io/preprints/marxiv)
- [MediArXiv](https://mediarxiv.com)
- [MetaArXiv](https://osf.io/preprints/metaarxiv)
- [MindRxiv](https://osf.io/preprints/mindrxiv)
- [NewAddictionSx](https://osf.io/preprints/newaddictionsx)
- [NutriXiv](https://niblunc.org)
- [OpenAlex](https://openalex.org)
- [OSF Preprints](https://osf.io/preprints/osf)
- [PaleoRxiv](https://osf.io/preprints/paleorxiv)
- [PsyArXiv](https://psyarxiv.com)
- [SocArXiv](https://socopen.org/welcome)
- [SportRxiv](http://sportrxiv.org)
- [Thesis Commons](https://osf.io/preprints/thesiscommons)

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

4. **Add dependencies**
   ```bash
   pip install <new-lib>
   pip freeze > requirements.txt
   ```

### Running the Server with Hot Reload

```bash
# Run with hot reload
watchmedo auto-restart --patterns="*.py" --recursive -- python src/server.py
# Run Server using fastmcp
fastmcp run server.py --transport http --host 0.0.0.0 --port 8000
```

The server will automatically restart when you make changes to any `.py` files.

### Testing

Use the [MCP Inspector](https://inspector.modelcontextprotocol.io/) to interact with the server.

```bash
pnpx @modelcontextprotocol/inspector
```

### Unit Tests

Run the unit tests to verify the functionality of individual components:

```bash
# Run all tests
python -m unittest discover tests -v
```
