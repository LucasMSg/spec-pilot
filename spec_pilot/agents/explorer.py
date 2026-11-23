"""Explorer agent: reads an unfamiliar codebase and writes structured notes."""
import sys
from pathlib import Path

from spec_pilot.llm import log, run_agent
from spec_pilot.tools import READ_TOOLS, Workspace

SYSTEM = """You are a senior engineer onboarding onto an unfamiliar codebase.
Use the tools to list and read files. Read every source file before answering.
Do not guess: base every statement on code you have read, citing file:line.

When done, reply with Markdown notes containing exactly these sections:
## Overview
## Modules
(one entry per module: purpose, public classes/functions with signatures)
## Behaviors
(what each public function does, including return values and errors raised)
## Edge cases and suspicious behavior
(inputs the code does not validate, possible bugs, surprising behavior)
"""


def explore(root: str) -> str:
    ws = Workspace(root)
    log(f"[explorer] exploring {ws.root}")
    return run_agent(SYSTEM, "Explore this codebase and write your notes.",
                     READ_TOOLS, ws.handlers())


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "sample_target"
    notes = explore(root)
    out = Path("out")
    out.mkdir(exist_ok=True)
    (out / "notes.md").write_text(notes, encoding="utf-8")
    print(notes)