import argparse
import json
from pathlib import Path

from .diff import find_suspects, git_diff
from .index import build_index, save_index
from .ollama import review_section
from .parsers import discover
from .repair import apply_repairs, generate_repair, validate_repair


def main() -> int:
    parser = argparse.ArgumentParser(description="Find documentation sections linked to changed Python code.")
    parser.add_argument("command", choices=["index", "check", "repair"])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path(".self-healing/docs-index.json"))
    parser.add_argument("--base", default="HEAD~1")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--ollama", action="store_true", help="Review suspects with a local Ollama model")
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--apply", action="store_true", help="Apply repairs with confidence >= 0.8")
    args = parser.parse_args()

    root = args.root.resolve()
    if args.command == "index":
        code, docs = discover(root)
        save_index(build_index(code, docs), root / args.output)
        print(f"Indexed {len(code)} code chunks and {len(docs)} documentation sections.")
        return 0

    code, docs = discover(root)
    index = build_index(code, docs)
    findings = find_suspects(index, git_diff(root, args.base))
    result = []
    for finding in findings:
        item = {"section": finding.section.stable_id, "reason": finding.reason, "confidence": finding.confidence}
        if args.ollama or args.command == "repair":
            linked_code = [chunk for chunk in code if chunk.path in finding.changed_paths]
            item["review"] = review_section(finding.section, linked_code, model=args.model)
        if args.command == "repair" and item.get("review", {}).get("stale"):
            linked_code = [chunk for chunk in code if chunk.path in finding.changed_paths]
            item["repair"] = generate_repair(finding.section, linked_code, item["review"], model=args.model)
            item["repair"]["validation"] = validate_repair(finding.section, item["repair"], linked_code, model=args.model)
            item["path"] = finding.section.path
            item["start_line"] = finding.section.start_line
            item["end_line"] = finding.section.end_line
        result.append(item)
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.json_output:
        args.json_output.write_text(json.dumps(result) + "\n", encoding="utf-8")
    if args.command == "repair":
        repairs = [item | item.pop("repair") for item in result if "repair" in item]
        repair_file = root / ".self-healing/repair.json"
        repair_file.parent.mkdir(parents=True, exist_ok=True)
        repair_file.write_text(json.dumps(repairs, indent=2) + "\n", encoding="utf-8")
        if args.apply:
            print(f"Applied repairs to: {', '.join(apply_repairs(root, repairs)) or 'none'}")
        else:
            print(f"Wrote proposed repairs to {repair_file}; rerun with --apply to modify files.")
    return 1 if findings else 0
