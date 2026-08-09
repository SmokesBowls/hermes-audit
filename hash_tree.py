from pathlib import Path
import hashlib
import sys

root = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
rows = []
for path in sorted(root.rglob("*")):
    relative = path.relative_to(root)
    if relative.parts and relative.parts[0] == ".git":
        continue
    stat = path.lstat()
    if path.is_symlink():
        rows.append(f"SYMLINK\t{relative.as_posix()}\t{path.readlink()}")
    elif path.is_file():
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        rows.append(
            f"FILE\t{relative.as_posix()}\t{stat.st_mode:o}\t{stat.st_size}\t{digest.hexdigest()}"
        )
    elif path.is_dir():
        rows.append(f"DIR\t{relative.as_posix()}\t{stat.st_mode:o}")
out.write_text("\n".join(rows) + "\n", encoding="utf-8")
print(f"{len(rows)} entries written to {out}")
