import json
import os
import subprocess
import sys
from urllib.request import Request, urlopen
from pathlib import Path


def command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def post_pr_comment(findings: list[dict]) -> None:
    token = os.environ.get("GITHUB_TOKEN")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not token or not event_path or not repository or os.environ.get("INPUT_COMMENT", "true").lower() != "true":
        return
    try:
        event = json.loads(Path(event_path).read_text(encoding="utf-8"))
        number = event["number"]
        if not findings:
            body = "## Documentation Check\n\n✅ No linked documentation sections were affected by this change."
        else:
            rows = "\n".join(f"- `{item['section']}` — {item['reason']}" for item in findings)
            body = f"## Documentation Check\n\n⚠️ Found **{len(findings)}** documentation section(s) linked to changed Python code:\n\n{rows}\n\nThis is a rules-first finding; review the sections before updating them."
        api = os.environ.get("GITHUB_API_URL", "https://api.github.com")
        request = Request(f"{api}/repos/{repository}/issues/{number}/comments", data=json.dumps({"body": body}).encode(), headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=30):
            pass
    except (OSError, KeyError, json.JSONDecodeError) as error:
        print(f"Could not post pull request comment: {error}", file=sys.stderr)


def create_repair_pr(workspace: Path, base: str) -> None:
    if os.environ.get("INPUT_AUTO-REPAIR", "false").lower() != "true":
        return
    token = os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repository:
        print("auto-repair requested but GITHUB_TOKEN or GITHUB_REPOSITORY is missing", file=sys.stderr)
        return
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    branch = f"self-healing-docs/{run_id}"
    commands = [
        ("git", "config", "user.name", "self-healing-docs[bot]"),
        ("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"),
        ("git", "switch", "-c", branch),
        (sys.executable, "-m", "self_healing_docs", "repair", "--root", str(workspace), "--base", base, "--ollama", "--apply"),
    ]
    for args in commands:
        result = command(*args)
        if result.returncode not in (0, 1):
            print(result.stdout + result.stderr, file=sys.stderr)
            return
    changed = command("git", "status", "--porcelain", "--", "*.md")
    if not changed.stdout.strip():
        print("No validated documentation repairs were generated.")
        return
    if command("git", "add", "--", "*.md").returncode != 0 or command("git", "commit", "-m", "docs: apply validated self-healing repairs").returncode != 0 or command("git", "push", "--set-upstream", "origin", branch).returncode != 0:
        print("Could not publish the repair branch.", file=sys.stderr)
        return
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    base_ref = base
    if event_path:
        try:
            base_ref = json.loads(Path(event_path).read_text(encoding="utf-8"))["pull_request"]["base"]["ref"]
        except (OSError, KeyError, json.JSONDecodeError):
            pass
    api = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    payload = {"title": "docs: apply validated self-healing repairs", "head": branch, "base": base_ref, "body": "Automated draft PR containing only repairs that passed the local-model validation gate.", "draft": True}
    request = Request(f"{api}/repos/{repository}/pulls", data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=30) as response:
            created = json.loads(response.read().decode("utf-8"))
        print(f"Created draft repair PR: {created.get('html_url', 'unknown URL')}")
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not create draft repair PR: {error}", file=sys.stderr)


def main() -> int:
    workspace = Path(os.environ.get("GITHUB_WORKSPACE", "."))
    output_file = workspace / ".self-healing" / "findings.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    base = os.environ.get("GITHUB_BASE_SHA") or "HEAD~1"
    result = command(
        sys.executable,
        "-m",
        "self_healing_docs",
        "check",
        "--root",
        str(workspace),
        "--base",
        base,
        "--json-output",
        str(output_file),
    )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")

    findings = []
    if output_file.exists():
        findings = json.loads(output_file.read_text(encoding="utf-8"))
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as stream:
            stream.write("findings<<EOF\n")
            stream.write(json.dumps(findings))
            stream.write("\nEOF\n")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as stream:
            stream.write("## Documentation Check\n\n")
            if findings:
                stream.write(f"Found **{len(findings)}** documentation section(s) linked to changed Python code.\n\n")
                for finding in findings:
                    stream.write(f"- `{finding['section']}` — {finding['reason']}\n")
            else:
                stream.write("No linked documentation sections were affected.\n")

    post_pr_comment(findings)
    if os.environ.get("INPUT_AUTO-REPAIR", "false").lower() == "true":
        create_repair_pr(workspace, base)

    if result.returncode not in (0, 1):
        return result.returncode
    return 1 if findings and len(sys.argv) > 1 and sys.argv[1].lower() == "true" else 0


if __name__ == "__main__":
    raise SystemExit(main())
