import argparse
import json
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ("PRD.md", "ARCHITECTURE.md", "GITHUB_ORGANIZATION.md")
SEED_PATTERN = re.compile(r"^\| ([A-Z]+-\d{2}) \|")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_backlog(text):
    issues = {}
    for line in text.splitlines():
        if not SEED_PATTERN.match(line):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        require(len(cells) == 6, "Invalid seed issue table")
        issue_id, repository, priority, title, dependencies, acceptance = cells
        require(issue_id not in issues, f"Duplicate seed ID: {issue_id}")
        require(repository in {"`fluzo`", "`fluzo-docs`"}, f"Invalid repository: {issue_id}")
        require(priority in {"P0", "P1", "P2"}, f"Invalid priority: {issue_id}")
        require(bool(title and acceptance), f"Incomplete issue: {issue_id}")
        issues[issue_id] = [] if dependencies == "-" else dependencies.split(", ")
    require(len(issues) == 33, "Expected the approved 33 seed issues")
    visited = set()
    visiting = set()

    def visit(issue_id):
        require(issue_id in issues, f"Unknown dependency: {issue_id}")
        require(issue_id not in visiting, f"Dependency cycle: {issue_id}")
        if issue_id in visited:
            return
        visiting.add(issue_id)
        for dependency in issues[issue_id]:
            visit(dependency)
        visiting.remove(issue_id)
        visited.add(issue_id)

    for issue_id in issues:
        visit(issue_id)


def validate_source(path):
    text = path.read_text(encoding="utf-8")
    require(len(re.findall(r"^```", text, re.M)) % 2 == 0, f"Unbalanced fences: {path.name}")
    for language, block in re.findall(r"^```(toml|json)\n(.*?)^```", text, re.M | re.S):
        tomllib.loads(block) if language == "toml" else json.loads(block)
    for target in re.findall(r"\]\(([^)]+)\)", text):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        destination = (path.parent / unquote(parsed.path)).resolve()
        require(destination.is_file(), f"Missing local link in {path.name}: {target}")
    for target in re.findall(r"\{\{#include ([^}\n]+)\}\}", text):
        require((path.parent / target.strip()).is_file(), f"Missing include: {path.name}")
    sensitive_patterns = (
        r"(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        r"https?://(?:[A-Za-z0-9-]+\.)+duckdns\.org\b",
        r"/home/[A-Za-z0-9_.-]+/",
    )
    for pattern in sensitive_patterns:
        require(not re.search(pattern, text), f"Potential private data in {path.name}; inspect locally")
    return text


def main():
    parser = argparse.ArgumentParser(description="Check Fluzo documentation and optional build output")
    parser.add_argument("--book", type=Path)
    options = parser.parse_args()
    documents = {name: validate_source(ROOT / name) for name in CANONICAL}
    for path in list(ROOT.glob("*.md")) + list((ROOT / "src").glob("*.md")):
        validate_source(path)
    config = tomllib.loads((ROOT / "book.toml").read_text(encoding="utf-8"))
    require(config["book"]["src"] == "src", "Book must not publish repository-private files")
    require(config["build"]["create-missing"] is False, "Missing chapters must fail")
    validate_backlog(documents["GITHUB_ORGANIZATION.md"])
    decisions = dict(re.findall(r"^\| (A\d{2}) \| (Accepted|Proposed) \|", documents["ARCHITECTURE.md"], re.M))
    require(decisions == {f"A{number:02d}": "Accepted" for number in range(1, 11)}, "Architecture decision baseline changed; review explicitly")
    for name in CANONICAL:
        require((ROOT / "src" / name).read_text().strip() == "{{#include ../" + name + "}}", f"Duplicate canonical body: {name}")
    if options.book:
        for filename in ("index.html", "PRD.html", "ARCHITECTURE.html", "GITHUB_ORGANIZATION.html", "mermaid.min.js", "mermaid-init.js"):
            require((options.book / filename).is_file(), f"Missing built asset: {filename}")
        architecture = (options.book / "ARCHITECTURE.html").read_text(encoding="utf-8")
        require('class="mermaid"' in architecture, "Architecture diagrams were not preprocessed")
        require("{{#include" not in architecture, "Unresolved book include")
        require(not (options.book / ".git").exists(), "Git metadata must not be published")
    checks = "canonical documents, TOML/JSON, local links, privacy scan and 33 issue dependencies"
    if options.book:
        checks += ", plus generated book assets"
    print(f"PASS: {checks}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"Documentation check failed: {error}", file=sys.stderr)
        raise SystemExit(1)