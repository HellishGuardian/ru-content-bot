import os, hashlib, json, pathlib

EXCLUDE_DIRS = {
    '.git', '.venv', 'node_modules', '__pycache__',
    '.idea', '.vscode', 'keys', 'dist', 'build', '.github'
}
EXCLUDE_EXT = {'.pyc', '.pyo', '.log'}
EXCLUDE_FILES = {'.env', '.env.local', '.DS_Store', 'Thumbs.db'}

ROOT = pathlib.Path(__file__).resolve().parents[1]

def iter_files(root: pathlib.Path):
    for p in root.rglob('*'):
        # ВАЖНО: игнорируем любой путь, который содержит исключённые директории
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.is_dir():
            continue
        name = p.name
        if name in EXCLUDE_FILES or p.suffix in EXCLUDE_EXT:
            continue
        low = name.lower()
        if ('secret' in low or 'token' in low or 'key' in low) and p.suffix in {'.json', '.txt'}:
            continue
        yield p

def sha256_of(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    files = []
    tree_lines = ["# Project tree (snapshot)\n"]
    for p in sorted(iter_files(ROOT), key=lambda x: str(x).lower()):
        rel = p.relative_to(ROOT).as_posix()
        digest = sha256_of(p)
        size = p.stat().st_size
        files.append({"path": rel, "sha256": digest, "bytes": size})
        tree_lines.append(f"- `{rel}` ({size} B)")

    manifest = {"root": str(ROOT), "count": len(files), "files": files}
    (ROOT / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "TREE.md").write_text("\n".join(tree_lines) + "\n", encoding="utf-8")
    print(f"Generated MANIFEST.json and TREE.md at {ROOT}")

if __name__ == "__main__":
    main()
