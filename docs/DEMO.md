# 90-second demo script

## 0:00–0:15 — Problem

“Documentation becomes stale whenever code changes. This project turns that problem into a GitHub pull-request check.”

## 0:15–0:35 — Show the intentional change

Open `demo/service.py` and change the default port from `8000` to `8100`, leaving `demo/README.md` unchanged.

## 0:35–0:55 — Open the pull request

Push the branch and open a PR. The Documentation Check runs and identifies the affected Markdown section instead of scanning the entire repository blindly.

## 0:55–1:10 — Show the fix

Update `demo/README.md` to port `8100`, push again, and show the green check with no findings.

## 1:10–1:30 — Explain the design

“The default mode requires no OpenAI key. It uses Python AST parsing, Markdown heading sections, stable links, and Git diff ranges. Ollama is optional for review and validated repairs.”

