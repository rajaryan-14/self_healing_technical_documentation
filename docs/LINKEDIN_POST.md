# LinkedIn post draft

I built a GitHub Action that helps keep technical documentation synchronized with code changes.

When a pull request changes a Python function, configuration value, or API-related symbol, the Action identifies the Markdown sections that may now be stale and reports them directly in the PR.

What I focused on:

- Rules-first detection that works without an OpenAI API key
- Python AST parsing and Markdown section mapping
- Git diff-aware change detection
- Optional local Ollama review and repair generation
- Validation before any automated documentation change
- A real GitHub Action workflow with PR checks

The demo is intentionally small: change a server’s default port without updating its documentation, and the Action catches the mismatch. Update the docs, and the check goes green.

Repository: https://github.com/rajaryan-14/self_healing_technical_documentation

