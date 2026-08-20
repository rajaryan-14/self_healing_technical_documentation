FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /action
COPY pyproject.toml README.md ./
COPY self_healing_docs ./self_healing_docs
COPY action_entrypoint.py ./action_entrypoint.py

ENTRYPOINT ["python", "/action/action_entrypoint.py"]
