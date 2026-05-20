# TCRIA MCP Server Setup

## Install dependencies

```bash
pip install mcp
pip install -r requirements.txt
```

## Run the MCP server

```bash
python mcp_server.py
```

## Available MCP tools

- `health`
- `audit_paths`
- `run_governance_pipeline`
- `read_audit_artifact`

## Example OpenAI Responses API integration

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    tools=[
        {
            "type": "mcp",
            "server_url": "http://localhost:8000/mcp"
        }
    ],
    input="Run a governance audit for the uploaded evidence bundle"
)

print(response.output_text)
```

## Example local MCP client configuration

```json
{
  "mcpServers": {
    "tcria": {
      "command": "python",
      "args": ["mcp_server.py"]
    }
  }
}
```

## Recommended next step

Expose the MCP server through:

- FastAPI
- SSE transport
- Streamable HTTP
- Railway
- Render
- Docker

## Suggested production stack

- FastAPI
- uvicorn
- JWT authentication
- audit logging
- immutable governance events
- signed artifacts
- RBAC
- OpenTelemetry

## Security note

This MCP server intentionally preserves the governance-first constraints already defined by TCRIA.
It does not autonomously determine guilt, liability, or legal responsibility.
Human validation remains mandatory.
