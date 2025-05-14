# PlayTingz Client

## Setup
 - Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
 - Install python 3.13
   ```bash
   uv python install 3.13
   ```
 - Install dependencies  
   
   ```bash
   uv sync
   ```
- add Anthropic API Key to ``.env`` file.


To interact with a unity project, make sure to
- install the [UnityMCPBridge](https://github.com/justinpbarnett/unity-mcp) (follow instructions)
- add location of the installed UnityMCPServer to the ``.env`` file. (Should be `"C:\\Users\\<USERNAME>\\AppData\\Local\\Programs\\UnityMCP\\UnityMcpServer\\src"`)

## Running the Client

You can run the client either using docker, or directly using ``uv``.

- **Docker:**
    ```bash
    docker build -t playtingz-client:1.0 .
    docker run -d -p 80:5000 --name api playtingz-client:1.0
    ```
 
    ```bash
    docker-compose build
    docker-compose up -d
    ```
- **uv**
  ````
  uv run src/app.py  
  ````

**NOTE**: A Unity Instance with the MCP Bridge active must be running.

### Chat CLI Interface

If you just want a simple command line interface instead of a webapp, run:

```bash
uv run src/client.py
```