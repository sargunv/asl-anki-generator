"""Generate an Anki ASL deck from words.json."""

import json
from pathlib import Path

import genanki
from pydantic import ValidationError
from rich.table import Table

from . import console
from .generate import generate_decks
from .models import WordsConfig

WORD_LIST = Path("words.json")


def main() -> None:
    if not WORD_LIST.exists():
        console.print(f"[bold red]Error:[/bold red] {WORD_LIST} not found.")
        raise SystemExit(1)

    try:
        raw = json.loads(WORD_LIST.read_text())
    except json.JSONDecodeError as exc:
        console.print(f"[bold red]Error:[/bold red] Invalid JSON in {WORD_LIST}: {exc}")
        raise SystemExit(1)

    try:
        config = WordsConfig.model_validate(raw)
    except ValidationError as exc:
        console.print(f"[bold red]Error:[/bold red] Invalid config in {WORD_LIST}:\n{exc}")
        raise SystemExit(1)

    decks, video_files, failures = generate_decks(config)

    my_package = genanki.Package(decks)
    my_package.media_files = video_files
    my_package.write_to_file(config.export_filename)

    total_cards = sum(len(deck.notes) for deck in decks)

    table = Table(title="Export Summary", show_header=False, border_style="dim")
    table.add_column(style="bold")
    table.add_column()
    table.add_row("Output", f"[cyan]{config.export_filename}[/cyan]")
    table.add_row("Decks", str(len(decks)))
    table.add_row("Cards", str(total_cards))
    if failures:
        table.add_row("Failures", f"[bold red]{failures}[/bold red]")
    else:
        table.add_row("Failures", "[green]0[/green]")
    console.print(table)


if __name__ == "__main__":
    main()
