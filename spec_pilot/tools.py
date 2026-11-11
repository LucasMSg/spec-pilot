"""Read-only file tools, sandboxed to one directory."""
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".pytest_cache"}
MAX_CHARS = 20_000


class Workspace:
    def __init__(self, root):
        self.root = Path(root).resolve()

    def _safe(self, rel: str) -> Path:
        path = (self.root / rel).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError(f"path escapes workspace: {rel}")
        return path

    def list_files(self, subdir: str = ".") -> str:
        base = self._safe(subdir)
        files = []
        for p in sorted(base.rglob("*")):
            rel = p.relative_to(self.root)
            if p.is_file() and not SKIP_DIRS.intersection(rel.parts):
                files.append(str(rel))
        return "\n".join(files) or "(no files)"

    def read_file(self, path: str) -> str:
        text = self._safe(path).read_text(encoding="utf-8", errors="replace")
        numbered = "\n".join(f"{i:4}| {line}"
                             for i, line in enumerate(text.splitlines(), 1))
        if len(numbered) > MAX_CHARS:
            numbered = numbered[:MAX_CHARS] + "\n... [truncated]"
        return numbered

    def handlers(self):
        return {"list_files": self.list_files, "read_file": self.read_file}


READ_TOOLS = [
    {"type": "function", "function": {
        "name": "list_files",
        "description": "List all files in the codebase (or in a subdirectory).",
        "parameters": {"type": "object", "properties": {
            "subdir": {"type": "string",
                       "description": "Relative directory, default '.'"}}},
    }},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a file. Lines are prefixed with line numbers.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Relative file path"}},
            "required": ["path"]},
    }},
]