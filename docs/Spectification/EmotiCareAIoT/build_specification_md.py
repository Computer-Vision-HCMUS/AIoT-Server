from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "Specification.md"


def numbered_markdown_files() -> list[Path]:
    return sorted(
        path
        for path in BASE_DIR.glob("*.md")
        if path.name[:2].isdigit() and path.name[2:3] == "_"
    )


def main() -> None:
    files = numbered_markdown_files()
    if not files:
        raise SystemExit("No numbered markdown files found.")

    parts: list[str] = []
    for index, path in enumerate(files):
        content = path.read_text(encoding="utf-8").strip()
        if index:
            parts.append("\n\n---\n\n")
        parts.append(content)

    OUTPUT_FILE.write_text("".join(parts) + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT_FILE.name} from {len(files)} files.")


if __name__ == "__main__":
    main()
