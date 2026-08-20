# Video voiceover script

This script is written for the silent 58-second demo video. Read it naturally at roughly 125–140 words per minute, or use it as captions.

## 0:00–0:06 — Opening

“What if your documentation could notice when your code made it outdated?”

## 0:06–0:16 — The change

“Here, the server’s default port changes from 8000 to 8100. The code is updated, but the README still says 8000.”

## 0:16–0:26 — Detection

“When the pull request opens, the Documentation Check finds the specific Markdown section connected to that code change.”

## 0:26–0:36 — Review

“The default workflow is rules-first and doesn’t need an OpenAI API key. An optional local Ollama model can review the finding and suggest a focused fix.”

## 0:36–0:46 — Validation

“Before anything is changed automatically, the repair goes through a second validation pass. Low-confidence suggestions stay proposals.”

## 0:46–0:58 — Result

“Once the README is updated to 8100, the check goes green. The project connects Python parsing, Markdown mapping, Git diffs, and pull request feedback in one small workflow.”
