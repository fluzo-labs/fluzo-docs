import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from check_docs import validate_backlog


ROOT = Path(__file__).resolve().parents[1]
OWNER = "fluzo-labs"
REPOSITORIES = ("fluzo", "fluzo-docs")
METADATA = {
    "ORG-01": ("chore", "governance", "1, 33", "A01"),
    "ORG-02": ("chore", "governance", "45, 46", "A08"),
    "DOC-01": ("docs", "docs", "1, 34, 53", "A01-A10"),
    "DOC-02": ("docs", "docs", "46", "A08"),
    "FND-01": ("chore", "core", "32, 33, 51, 52", "A01, A02"),
    "FND-02": ("feature", "config", "26, 27, 43", "A06"),
    "FND-03": ("feature", "runtime", "17, 23, 51", "A02, A07"),
    "FND-04": ("chore", "tests", "45.2, 53", "A01, A08"),
    "SIM-01": ("feature", "tests", "45.1, 45.2", "A08"),
    "UI-01": ("feature", "tui", "29, 30, 31", "A07"),
    "UI-02": ("feature", "tui", "29.1, 29.2.1, 29.2.2", "A06, A07"),
    "UI-03": ("feature", "config", "26, 29, 30", "A06, A07"),
    "UI-04": ("feature", "tui", "12, 17, 29, 30", "A05, A07"),
    "UI-05": ("design", "tui", "29.4, 33.1, 49", "A07"),
    "DAT-01": ("feature", "storage", "21, 22, 23, 24", "A03"),
    "DAT-02": ("feature", "storage", "22.2, 44.5", "A03"),
    "OBS-01": ("feature", "observability", "44", "A09"),
    "OBS-02": ("feature", "observability", "44.7", "A09"),
    "RUN-01": ("feature", "security", "21.1, 21.2", "A02, A05"),
    "RUN-02": ("feature", "security", "12, 26, 42", "A05, A06"),
    "RUN-03": ("feature", "runtime", "13, 17.2, 21.3", "A05"),
    "RUN-04": ("feature", "runtime", "17, 22.1, 24", "A02, A03"),
    "RUN-05": ("feature", "providers", "43.1, 43.3", "A04"),
    "AGT-01": ("feature", "providers", "8, 34, 42.1, 43", "A04, A08, A09"),
    "AGT-02": ("feature", "runtime", "16, 16.1, 20", "A06"),
    "AGT-03": ("feature", "providers", "10.1, 43.3, 44.4", "A04, A10"),
    "AGT-04": ("feature", "runtime", "34, 45.1, 53", "A03, A05, A08"),
    "REL-01": ("feature", "tui", "28, 29, 30, 53", "A02, A06, A07"),
    "REL-02": ("chore", "tests", "45, 53", "A01-A10"),
    "REL-03": ("chore", "tests", "29.4, 33.1, 49", "A07, A08"),
    "REL-04": ("chore", "packaging", "33.2, 45.2", "A01, A08"),
    "DOC-03": ("docs", "docs", "26, 28, 33, 42, 45", "A01-A10"),
    "REL-05": ("chore", "packaging", "33.2, 49, 53", "A01-A10"),
}


class GitHub:
    def __init__(self):
        self.environment = dict(os.environ, GH_PAGER="/bin/cat", PAGER="/bin/cat", GH_PROMPT_DISABLED="1")

    def request(self, path, method="GET", payload=None):
        command = ["/usr/bin/gh", "api", "--hostname", "github.com", "--method", method, path]
        if payload is not None:
            command += ["--input", "-"]
        response = subprocess.run(command, input=None if payload is None else json.dumps(payload), text=True, capture_output=True, env=self.environment)
        if response.returncode:
            raise RuntimeError(f"GitHub {method} {path}: {response.stderr.strip()}")
        return json.loads(response.stdout) if response.stdout.strip() else None

    def collection(self, path):
        records = []
        for page in range(1, 101):
            separator = "&" if "?" in path else "?"
            result = self.request(f"{path}{separator}per_page=100&page={page}")
            records.extend(result)
            if len(result) < 100:
                return records
        raise RuntimeError(f"Pagination safety limit reached: {path}")


def read_seed():
    text = (ROOT / "GITHUB_ORGANIZATION.md").read_text(encoding="utf-8")
    validate_backlog(text)
    issues = []
    delivery = None
    for line in text.splitlines():
        heading = re.match(r"^### 6\.\d (M\d): (.+)$", line)
        if heading:
            delivery = f"{heading.group(1)}: {heading.group(2)}"
        if not re.match(r"^\| [A-Z]+-\d{2} \|", line):
            continue
        issue_id, repository, priority, title, dependencies, acceptance = [cell.strip() for cell in line.split("|")[1:-1]]
        if issue_id not in METADATA or not delivery:
            raise ValueError(f"Missing metadata: {issue_id}")
        issues.append({"seed_id": issue_id, "repository": repository.strip("`"), "priority": priority, "delivery": delivery, "title": title, "dependencies": [] if dependencies == "-" else dependencies.split(", "), "acceptance": acceptance})
    return issues


def issue_body(issue, mapping, baseline):
    kind, area, sections, decisions = METADATA[issue["seed_id"]]
    source = f"https://github.com/{OWNER}/fluzo-docs/blob/{baseline}"
    dependencies = "\n".join(f"- {dependency}: {mapping[dependency]['url']}" for dependency in issue["dependencies"]) or "None."
    criteria = "\n".join(f"- [ ] {part.strip().rstrip('.')}" for part in re.split(r";\s+|(?<=\.)\s+(?=[A-Z])", issue["acceptance"]) if part.strip())
    verification = (
        "Documentation/source checks, site build and actual publication evidence as applicable. No model calls are required."
        if issue["repository"] == "fluzo-docs" else
        "Use focused deterministic tests and attach actual commands/results. Compose integration belongs in a Docker-capable job where applicable; live inference is opt-in and never a required CI or packaging gate."
    )
    return f"""<!-- fluzo-backlog:{issue['seed_id']} -->
## Goal

{issue['title']}

- Seed ID: **{issue['seed_id']}**
- Delivery: **{issue['delivery']}**
- Priority: **{issue['priority']}**
- Area: **{area}**

## Design Baseline

- [PRD v0.2]({source}/PRD.md), sections {sections}.
- [Architecture v0.1]({source}/ARCHITECTURE.md), decisions {decisions}.
- [Approved seed plan]({source}/GITHUB_ORGANIZATION.md).

## Acceptance Criteria

{criteria}
- [ ] Evidence and relevant documentation are linked from the completing PR or issue comment.

## Dependencies

{dependencies}

## Verification

{verification}

## Scope and Risks

Implement the cited contract without silently broadening the MVP. Preserve user data, authorization and audit boundaries. Do not put credentials, private endpoints or histories in issue attachments. Split this brief into linked child work before implementation if it cannot fit a reviewable increment.

No active Laya routing, public plugin loader, cross-instance inference coordinator, provider rate-limit recovery, sandbox guarantees or runtime release is implied by this issue. A documentation/demo result does not prove runtime behavior or performance.
"""


def main():
    parser = argparse.ArgumentParser(description="Idempotently import Fluzo's approved seed issues; dry-run by default")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--baseline", help="Published immutable fluzo-docs commit")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--link-dependencies", action="store_true", help="Add missing native blocked-by relationships without removing existing ones")
    options = parser.parse_args()
    issues = read_seed()
    if not options.apply:
        for issue in issues:
            print(f"{issue['seed_id']:7} {OWNER}/{issue['repository']:10} {issue['priority']} {issue['delivery']} | {issue['title']}")
        print(f"DRY RUN: {len(issues)} issues; no GitHub requests or mutations.")
        return
    if not options.baseline or not re.fullmatch(r"[0-9a-f]{40}", options.baseline):
        raise ValueError("--apply requires a full published --baseline commit SHA")
    github = GitHub()
    github.request(f"repos/{OWNER}/fluzo-docs/commits/{options.baseline}")
    mapping = {}
    milestones = {}
    for repository in REPOSITORIES:
        path = f"repos/{OWNER}/{repository}"
        labels = {item["name"] for item in github.collection(path + "/labels")}
        desired = {"type:bug", "type:feature", "type:design", "type:spike", "type:docs", "type:chore"}
        for issue in issues:
            if issue["repository"] == repository:
                desired.add("area:" + METADATA[issue["seed_id"]][1])
        for label in sorted(desired - labels):
            github.request(path + "/labels", "POST", {"name": label, "color": "0969da" if label.startswith("area:") else "8250df", "description": "Fluzo work classification"})
        existing_milestones = github.collection(path + "/milestones?state=all")
        milestone = next((item for item in existing_milestones if item["title"] == "MVP"), None)
        if milestone is None:
            milestone = github.request(path + "/milestones", "POST", {"title": "MVP", "description": "Approved Linux MVP scope; delivery stages are recorded in each issue. No release date is implied."})
        milestones[repository] = milestone["number"]
        for item in github.collection(path + "/issues?state=all"):
            if "pull_request" in item:
                continue
            match = re.search(r"<!-- fluzo-backlog:([A-Z]+-\d{2}) -->", item.get("body") or "")
            if match:
                seed_id = match.group(1)
                if seed_id in mapping:
                    raise ValueError(f"Duplicate remote seed ID: {seed_id}")
                mapping[seed_id] = {"repository": repository, "number": item["number"], "url": item["html_url"], "node_id": item["node_id"], "id": item["id"]}
    pending = list(issues)
    while pending:
        progress = False
        for issue in pending[:]:
            seed_id = issue["seed_id"]
            if seed_id not in mapping and not all(dependency in mapping for dependency in issue["dependencies"]):
                continue
            if seed_id not in mapping:
                kind, area, _, _ = METADATA[seed_id]
                created = github.request(f"repos/{OWNER}/{issue['repository']}/issues", "POST", {"title": f"[{seed_id}] {issue['title']}", "body": issue_body(issue, mapping, options.baseline), "labels": [f"type:{kind}", f"area:{area}"], "milestone": milestones[issue["repository"]]})
                mapping[seed_id] = {"repository": issue["repository"], "number": created["number"], "url": created["html_url"], "node_id": created["node_id"], "id": created["id"]}
                print("CREATED", seed_id, created["html_url"], flush=True)
            else:
                if mapping[seed_id]["repository"] != issue["repository"]:
                    raise ValueError(f"Wrong repository for existing seed: {seed_id}")
                print("EXISTS", seed_id, mapping[seed_id]["url"], flush=True)
            pending.remove(issue)
            progress = True
        if not progress:
            raise ValueError("Unresolved dependency graph")
    dependency_count = 0
    if options.link_dependencies:
        for issue in issues:
            if not issue["dependencies"]:
                continue
            current = mapping[issue["seed_id"]]
            path = f"repos/{OWNER}/{current['repository']}/issues/{current['number']}/dependencies/blocked_by"
            existing = {item["id"] for item in github.collection(path)}
            for dependency in issue["dependencies"]:
                blocker = mapping[dependency]
                if blocker["id"] not in existing:
                    github.request(path, "POST", {"issue_id": blocker["id"]})
                    print("LINKED", issue["seed_id"], "blocked by", dependency, flush=True)
                dependency_count += 1
    report = {"organization": OWNER, "baseline": options.baseline, "native_dependency_count": dependency_count if options.link_dependencies else None, "issues": {issue['seed_id']: dict(mapping[issue['seed_id']], priority=issue['priority'], delivery=issue['delivery'], dependencies=issue['dependencies']) for issue in issues}}
    if options.report:
        options.report.parent.mkdir(parents=True, exist_ok=True)
        options.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"COMPLETE: {len(issues)} seed issues exist; pre-existing issue bodies and states were preserved.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError) as error:
        print(f"Backlog import failed: {error}", file=sys.stderr)
        raise SystemExit(1)