# 📂 File Organizer

A command-line tool that automatically sorts messy files into categorized folders. Built with pure Python — no external dependencies.

## Features

- **Smart categorization** — sorts files into Images, Documents, Audio, Video, Code, Data, Archives, and more
- **Dry run mode** — preview changes before anything moves
- **Undo support** — reverse any organize operation with `--undo`
- **Collision handling** — auto-renames files if a name conflict exists
- **Zero dependencies** — uses only Python standard library

## Quick start

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/file-organizer.git
cd file-organizer

# Preview what would happen
python -m src.organizer ~/Downloads --dry-run

# Organize for real
python -m src.organizer ~/Downloads

# Changed your mind? Undo it
python -m src.organizer ~/Downloads --undo

# Organize including subdirectories
python -m src.organizer ~/Downloads --recursive
```

## Example

**Before:**
```
~/Downloads/
├── report.pdf
├── vacation.jpg
├── song.mp3
├── script.py
├── data.csv
└── archive.zip
```

**After:**
```
~/Downloads/
├── Documents/
│   ├── report.pdf
│   └── data.csv
├── Images/
│   └── vacation.jpg
├── Audio/
│   └── song.mp3
├── Code/
│   └── script.py
└── Archives/
    └── archive.zip
```

## Supported categories

| Category    | Extensions                                           |
|-------------|------------------------------------------------------|
| Images      | .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .tiff   |
| Documents   | .pdf, .doc, .docx, .txt, .rtf, .xls, .xlsx, .pptx   |
| Audio       | .mp3, .wav, .flac, .aac, .ogg, .wma, .m4a           |
| Video       | .mp4, .mkv, .avi, .mov, .wmv, .flv, .webm           |
| Archives    | .zip, .tar, .gz, .rar, .7z, .bz2                    |
| Code        | .py, .js, .ts, .html, .css, .java, .cpp, .go, .rs   |
| Data        | .json, .xml, .yaml, .yml, .sql, .db, .sqlite        |
| Executables | .exe, .msi, .dmg, .app, .deb, .sh, .bat             |

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

## Project structure

```
file-organizer/
├── src/
│   ├── __init__.py
│   └── organizer.py      # Core logic + CLI
├── tests/
│   ├── __init__.py
│   └── test_organizer.py  # Unit tests
├── .gitignore
├── LICENSE
└── README.md
```
## Technologies

- Python 3.11 (standard library only, no external dependencies)
- argparse for CLI
- pathlib for cross-platform file handling
- shutil for file operations
- Optional: PyYAML for custom config support

## Roadmap

- [x] Recursive mode for nested directories
- [x] Custom category config via YAML file
- [ ] Watch mode — auto-organize new files as they appear
- [ ] Size-based filtering (e.g., move files > 100MB)
- [ ] Export organization report as JSON
- [ ] Add colored terminal output with rich library

## License

MIT

## Author

Vaishnav Venkatesh - [GitHub](https://github.com/Vaishnav0777)

## Status

![Maintained](https://img.shields.io/badge/maintained-yes-green)
