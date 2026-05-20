# TCRIA MCP Production Runbook

This runbook defines the recommended path from pull request to production for the TCRIA MCP Gateway.

## 1. Merge readiness

Before merging:

- Confirm CI checks are green.
- Review `mcp_server.py`.
- Review `api/mcp_gateway.py`.
- Confirm no real secrets were committed.
- Confirm production secrets are available in the target platform.
- Confirm audit log retention requirements.
- Confirm artifact signing policy.

## 2. Required production secrets

Configure these outside Git:

```bash
TCRIA_MCP_REQUIRE_AUTH=true
TCRIA_MCP_JWT_SECRET=<long-random-secret>
TCRIA_MCP_SIGNING_SECRET=<different-long-random-secret>
TCRIA_MCP_PUBLIC_URL=https://<production-host>/mcp
```

Optional observability:

```bash
TCRIA_OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=https://<otel-collector-endpoint>
TCRIA_LOG_LEVEL=INFO
```

## 3. Local production smoke test

```bash
cp .env.mcp.example .env
# edit secrets before running in production-like mode

docker compose -f docker-compose.mcp.yml up --build
curl http://localhost:8000/health
```

Expected result:

```json
{
  "status": "ok",
  "service": "tcria-mcp-http-gateway"
}
```

## 4. Railway deployment path

1. Create a Railway project.
2. Connect this repository.
3. Railway will use `railway.json` and `Dockerfile.mcp`.
4. Configure secrets in Railway Variables.
5. Deploy.
6. Run `/health`.
7. Run a smoke audit request with a controlled fixture.

## 5. Render deployment path

1. Create a Render Web Service.
2. Select Docker runtime.
3. Render will use `render.yaml` and `Dockerfile.mcp`.
4. Configure environment variables as secrets.
5. Deploy.
6. Validate `/health`.

## 6. Kubernetes deployment path

Create secrets first:

```bash
kubectl create secret generic tcria-mcp-secrets \
  --from-literal=jwt-secret='<long-random-secret>' \
  --from-literal=signing-secret='<different-long-random-secret>'
```

Apply manifests:

```bash
kubectl apply -f deploy/kubernetes/tcria-mcp-gateway.yaml
kubectl rollout status deployment/tcria-mcp-gateway
```

## 7. ECS/Fargate deployment path

1. Build and push `Dockerfile.mcp` image to ECR.
2. Replace placeholder ARNs in `deploy/ecs/task-definition.mcp.json`.
3. Store secrets in SSM Parameter Store or AWS Secrets Manager.
4. Register the task definition.
5. Create/update ECS service behind an ALB.
6. Validate `/health`.

## 8. OpenAI Responses API integration

Use the production MCP gateway URL as the MCP server URL.

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    tools=[
        {
            "type": "mcp",
            "server_url": "https://<production-host>/mcp"
        }
    ],
    input="Run a governed TCRIA audit for this evidence bundle."
)

print(response.output_text)
```

## 9. Production validation checklist

- `/health` returns `ok`.
- JWT validation is enabled.
- Secrets are externalized.
- Audit logs are being written.
- Artifact signing works.
- OpenTelemetry export is configured if enabled.
- Rollback path is documented.
- Human review remains mandatory for high-risk legal outputs.

## 10. Rollback

Rollback options:

- Railway: redeploy previous successful deployment.
- Render: redeploy previous deploy.
- Kubernetes: `kubectl rollout undo deployment/tcria-mcp-gateway`.
- ECS: update service to previous task definition revision.

## Governance note

TCRIA must not be used to autonomously determine guilt, liability, or legal responsibility. The MCP gateway only exposes governed audit and traceability functions. Human validation remains mandatory.
