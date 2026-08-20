# LinkedIn post draft

What if your documentation could notice when your code made it outdated?

I built a small GitHub Action that does exactly that.

When a pull request changes Python code, it finds the Markdown sections connected to that code and flags the ones that might now be stale—right inside the PR.

The demo is simple: I change a server’s default port from 8000 to 8100, leave the README unchanged, and the Action catches it. Once I update the README, the check goes green.

The parts I enjoyed building:

- A rules-first detector that works without an OpenAI API key
- Python AST parsing and Markdown section mapping
- Git diff-aware change detection
- Optional local Ollama review and repair generation
- A validation pass before anything is changed automatically
- A real GitHub Action workflow with PR checks

I wanted to build something that feels like a real engineering tool—not just a demo that runs locally.

Repository: https://github.com/rajaryan-14/self_healing_technical_documentation
