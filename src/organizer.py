#!/usr/bin/env python3
f"""
File Organizer — Automatically sort files into folders by type.

Usage:
    python -m src.organizer /path/to/messy/folder
    python -m src.organizer /path/to/messy/folder --dry-run
    python -m src.organizer /path/to/messy/folder --undo
    python -m src.organizer /path/to/messy/folder --recursive
"""
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Category mapping — add or tweak as you like
# ---------------------------------------------------------------------------
CATEGORIES: dict[str, list[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".pptx", ".csv"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "Video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z", ".bz2"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rs", ".rb"],
    "Data": [".json", ".xml", ".yaml", ".yml", ".sql", ".db", ".sqlite"],
    "Executables": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm", ".sh", ".bat"],
}

def load_categories(config_path: Path) -> dict[str, list[str]]:
    """Load custom categories from a YAML config file."""
    if not HAS_YAML:
        print("✗ PyYAML is required for --config. Install it with: pip install pyyaml")
        raise SystemExit(1)
    data = yaml.safe_load(config_path.read_text())
    return data.get("categories", CATEGORIES)
def get_category(extension: str) -> str:
    """Return the category name for a given file extension."""
    ext = extension.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"

def build_move_plan(source_dir: Path, *, recursive: bool = False, min_size: int = 0) -> list[dict]:    """
    Scan *source_dir* and return a list of planned moves.

    Each entry: {"src": <original path>, "dest": <target path>, "category": <str>}
    If recursive is False, only top-level files are considered.
    If recursive is True, files in subdirectories are also organized.
    """
    plan = []
    items = sorted(source_dir.rglob("*")) if recursive else sorted(source_dir.iterdir())

    for item in items:
        # Skip directories, hidden files, and our own log
        if item.is_dir() or item.name.startswith(".") or item.name == "organizer_log.json":
            continue
# Skip files smaller than min_size
        if min_size > 0 and item.stat().st_size < min_size:
            continue

        # Skip files already inside a category folder
        if item.parent != source_dir and item.parent.name in CATEGORIES:
            continue

        category = get_category(item.suffix)
        dest_dir = source_dir / category
        dest_file = dest_dir / item.name

        # Handle name collisions
        if dest_file.exists():
            stem = item.stem
            suffix = item.suffix
            counter = 1
            while dest_file.exists():
                dest_file = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        plan.append({
            "src": str(item),
            "dest": str(dest_file),
            "category": category,
        })
    return plan


def execute_plan(plan: list[dict], *, dry_run: bool = False) -> None:
    """Move files according to *plan*. If *dry_run*, only print what would happen."""
    if not plan:
        print("✓ Nothing to organize — folder is already clean!")
        return

    for entry in plan:
        src = Path(entry["src"])
        dest = Path(entry["dest"])

        if dry_run:
            print(f"  [DRY RUN] {src.name}  →  {dest.parent.name}/{dest.name}")
        else:
            dest.parent.mkdir(exist_ok=True)
            shutil.move(str(src), str(dest))
            print(f"  ✓ {src.name}  →  {dest.parent.name}/{dest.name}")


def save_log(source_dir: Path, plan: list[dict]) -> Path:
    """Save a JSON log so the operation can be undone later."""
    log_path = source_dir / "organizer_log.json"
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "source_dir": str(source_dir),
        "moves": plan,
    }
    log_path.write_text(json.dumps(log_data, indent=2))
    return log_path

def print_summary(plan: list[dict]) -> None:
    """Print a breakdown of files organized by category."""
    from collections import Counter
    counts = Counter(entry["category"] for entry in plan)
    print("\n  Category        Files")
    print("  ─────────────── ─────")
    for category, count in sorted(counts.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"  {category:<17} {count:>3}  {bar}")
    print()
def undo(source_dir: Path) -> None:
    """Reverse the last organize operation using the saved log."""
    log_path = source_dir / "organizer_log.json"
    if not log_path.exists():
        print("✗ No organizer_log.json found — nothing to undo.")
        return

    log_data = json.loads(log_path.read_text())
    for entry in log_data["moves"]:
        dest = Path(entry["dest"])
        src = Path(entry["src"])
        if dest.exists():
            shutil.move(str(dest), str(src))
            print(f"  ↩ {dest.name}  →  {src.name}")

    # Clean up empty category folders
    for entry in log_data["moves"]:
        cat_dir = Path(entry["dest"]).parent
        if cat_dir.exists() and not any(cat_dir.iterdir()):
            cat_dir.rmdir()

    log_path.unlink()
    print("✓ Undo complete!")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Organize files in a directory by type.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python -m src.organizer ~/Downloads\n"
               "  python -m src.organizer ~/Downloads --dry-run\n"
               "  python -m src.organizer ~/Downloads --undo",
    )
    parser.add_argument("directory", type=Path, help="Target directory to organize")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    parser.add_argument("--undo", action="store_true", help="Reverse the last organize operation")
    parser.add_argument("--recursive", action="store_true", help="Scan subdirectories recursively")
    parser.add_argument("--config", type=Path, default=None, help="Path to YAML config file for custom categories")
    parser.add_argument("--summary", action="store_true", help="Show category breakdown after organizing")
    parser.add_argument("--min-size", type=int, default=0, help="Only organize files larger than N bytes (e.g. 1024 for 1KB)")


    args = parser.parse_args()
    source_dir = args.directory.resolve()

    if not source_dir.is_dir():
        print(f"✗ '{source_dir}' is not a valid directory.")
        return

    if args.undo:
        undo(source_dir)
        return
    global CATEGORIES
    if args.config:
        CATEGORIES = load_categories(args.config)
        print(f"📋 Using custom categories from: {args.config.name}")
    print(f"\n📂 Scanning: {source_dir}\n")
    plan = build_move_plan(source_dir, recursive=args.recursive, min_size=args.min_size)

    if args.dry_run:
        print(f"Found {len(plan)} file(s) to organize:\n")
        execute_plan(plan, dry_run=True)
        print(f"\nRun without --dry-run to apply changes.")
    else:
        execute_plan(plan)
        if plan:
            log_path = save_log(source_dir, plan)
            total_size = sum(Path(e["src"]).stat().st_size for e in plan)
if total_size < 1024:
    size_str = f"{total_size} B"
elif total_size < 1024 * 1024:
    size_str = f"{total_size / 1024:.1f} KB"
else:
    size_str = f"{total_size / (1024 * 1024):.1f} MB"
print(f"\n✓ Organized {len(plan)} file(s) ({size_str}). Log saved to {log_path.name}")
            print("  Run with --undo to reverse.")
if args.summary:
            print_summary(plan)


if __name__ == "__main__":
    main()
