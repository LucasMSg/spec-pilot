"""Spec writer agent: turns explorer notes into a testable specification."""
import sys
from pathlib import Path

from spec_pilot.llm import log, run_agent
from spec_pilot.tools import READ_TOOLS, Workspace

SYSTEM = """You are a QA-minded engineer writing a behavioral specification.
You are given an engineer's notes about a codebase. The notes may contain
mistakes: verify every claim against the source with the tools before using it.

Write the spec as Markdown in exactly this format:

# Specification: <package name>

## Scope
One short paragraph.

## Requirements
One entry per observable behavior of the public API:

### REQ-001: <short title>
- **Given** <starting state>
- **When** <call with concrete example values>
- **Then** <exact expected result or exception type>
- **Source:** <file:line>

## Suspected defects
Same format, numbered DEF-001, DEF-002, ... for behavior that is probably a bug.
In **Then**, describe what a user would most likely expect, and add a line
- **Currently:** <what the code actually does, verified against the source>

Rules:
- Every requirement must be checkable by one small unit test.
- Use concrete values (e.g. sku "apple", qty 3), not placeholders.
- Cover normal cases, boundaries (0, 1, the threshold value) and every error path.
- Describe behavior only through the public API; never mention private attributes.
"""


def write_spec(root: str, notes: str) -> str:
    ws = Workspace(root)
    log("[spec_writer] writing specification")
    task = f"Notes from the explorer:\n\n{notes}\n\nWrite the specification."
    return run_agent(SYSTEM, task, READ_TOOLS, ws.handlers())


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "sample_target"
    notes = Path("out/notes.md").read_text(encoding="utf-8")
    spec = write_spec(root, notes)
    Path("out/SPEC.md").write_text(spec, encoding="utf-8")
    print(spec)