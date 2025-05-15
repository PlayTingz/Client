# PlayTingz Client

A powerful client for creating Unity Games through the PlayTingz interface.

## ✨ Features

- Unity Game creation with LLMs
- Web interface for interactive development
- Command-line interface for quick interactions
- Docker support for containerized deployment

## 🚀 Getting Started

### Prerequisites

- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.13
- [UnityMCPBridge](https://github.com/justinpbarnett/unity-mcp) (for Unity project integration)
- Anthropic API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/playtingz-client.git
   cd playtingz-client
   ```

2. Install Python 3.13:
   ```bash
   uv python install 3.13
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Create a `.env` file in the project root and add:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   UNITY_MCP_SERVER_PATH="C:\\Users\\<USERNAME>\\AppData\\Local\\Programs\\UnityMCP\\UnityMcpServer\\src"
   ```
   See ``src/.env.example`` for a complete list of fields.

### Unity Integration Setup

1. Install the [UnityMCPBridge](https://github.com/justinpbarnett/unity-mcp) following their installation instructions
2. Add the location of the installed UnityMCPServer to your `.env` file.
3. Make sure to have a Unity instance with the MCP Bridge active when running the client

## 🖥️ Running the Client

> **IMPORTANT**: A Unity Instance with the MCP Bridge active must be running for any client mode.

### Web Interface

You can run the client either using Docker or directly with `uv`.

#### Using Docker

Option 1:
```bash
docker build -t playtingz-client:1.0 .
docker run -d -p 80:5000 --name api playtingz-client:1.0
```

Option 2:
```bash
docker-compose build
docker-compose up -d
```

#### Using uv

```bash
uv run src/app.py
```

### Command Line Interface

For a simple CLI experience:

```bash
uv run src/client.py
```