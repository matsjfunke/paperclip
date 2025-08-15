# Contributing to Paperclip

Thank you for your interest in contributing to Paperclip! This guide will help you get started with development.

## Development Setup

### Prerequisites

- Python 3.12+
- pip

### Installation

1. **Fork and clone the repository**

   - Fork this repository on GitHub
   - Clone your fork:

   ```bash
   git clone https://github.com/YOUR_USERNAME/paperclip.git
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
fastmcp run src/server.py --transport http --host 0.0.0.0 --port 8000
# use docker compose
docker-compose up --build
```

The server will automatically restart when you make changes to any `.py` files.

## Testing

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

## Contributing Changes

### Creating a Pull Request

1. **Create a feature branch**

   ```bash
   git checkout -b feat/your-feature-name
   # or for bug fixes:
   git checkout -b fix/issue-description
   ```

2. **Make your changes**

   - Write your code following the existing style
   - Add tests for new functionality
   - Update documentation as needed

3. **Commit your changes and push to your fork**

   ```bash
   git push origin feat/your-feature-name
   ```

4. **Open a Pull Request**

   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch from your fork
   - Fill out the PR template with:
     - Clear description of changes
     - Link to related issues (if applicable)
     - Testing steps you've performed

### Pull Request Guidelines

- **Keep PRs focused**: One feature or fix per PR
- **Write clear descriptions**: Explain what changes you made and why
- **Test your changes**: Ensure all tests pass before submitting
- **Update documentation**: Add or update docs for new features
- **Be responsive**: Address feedback and questions promptly
