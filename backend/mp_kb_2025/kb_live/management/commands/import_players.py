from __future__ import annotations

from pathlib import Path
from typing import Iterable

from django.core.management.base import BaseCommand, CommandError

from tablib import Dataset

from import_export.results import Result

from kb_live.resources import PlayerImportResource


class Command(BaseCommand):
    help = "Importuje zawodników z pliku korzystając z PlayerImportResource (jak w panelu admina)."

    def add_arguments(self, parser):
        parser.add_argument(
            "input_file",
            help="Ścieżka do pliku CSV z danymi zawodników (nagłówki jak w eksporcie).",
        )
        parser.add_argument(
            "--encoding",
            default="utf-8",
            help="Kodowanie pliku wejściowego (domyślnie utf-8).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Próba importu bez zapisu zmian w bazie danych.",
        )
        parser.add_argument(
            "--raise-errors",
            action="store_true",
            help="Natychmiast przerwij przy pierwszym błędzie (domyślnie tylko raportuje).",
        )
        parser.add_argument(
            "--no-transactions",
            dest="use_transactions",
            action="store_false",
            help="Wyłącz transakcje otaczające import.",
        )
        parser.set_defaults(use_transactions=True)

    def handle(self, *args, **options):
        file_path = Path(options["input_file"]).expanduser()
        if not file_path.exists() or not file_path.is_file():
            raise CommandError(f"Nie znaleziono pliku: {file_path}")

        encoding = options["encoding"]
        try:
            raw_data = file_path.read_text(encoding=encoding)
        except UnicodeDecodeError as exc:
            raise CommandError(f"Nie udało się odczytać pliku w kodowaniu '{encoding}': {exc}") from exc

        dataset = Dataset()
        try:
            dataset.load(raw_data, format="csv")
        except Exception as exc:  # noqa: BLE001 - chcemy pokazać info użytkownikowi
            raise CommandError(f"Błąd podczas wczytywania CSV: {exc}") from exc

        resource = PlayerImportResource()
        dry_run: bool = options["dry_run"]
        use_transactions: bool = options["use_transactions"]
        raise_errors: bool = options["raise_errors"]

        result = resource.import_data(
            dataset,
            dry_run=dry_run,
            use_transactions=use_transactions,
            raise_errors=raise_errors,
        )

        self._report_result(result)

        totals = result.totals or {}
        summary_bits = [
            f"nowe={totals.get('new', 0)}",
            f"zaktualizowane={totals.get('update', 0)}",
            f"pominiete={totals.get('skip', 0)}",
            f"wszystkie={totals.get('total', len(dataset))}",
        ]

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run zakończony. Brak zmian w bazie."))
            self.stdout.write(f"Podsumowanie (symulacja): {', '.join(summary_bits)}")
        else:
            self.stdout.write(self.style.SUCCESS("Import zakończony."))
            self.stdout.write(f"Podsumowanie: {', '.join(summary_bits)}")

    def _report_result(self, result: Result) -> None:
        if result.has_errors():
            self._print_row_errors(result.row_errors())
            for base_error in result.base_errors:
                self.stderr.write(f"Błąd ogólny: {base_error.error}")
            raise CommandError("Import zakończony niepowodzeniem z powodu błędów.")

        if result.invalid_rows:
            self.stderr.write("Wykryto niepoprawne wiersze:")
            for invalid in result.invalid_rows:
                self.stderr.write(
                    f"  wiersz {invalid.number}: {invalid.error_list}",
                )
            # Jeśli to tylko dry-run, pozwalamy zobaczyć błędy. W innym wypadku zatrzymujemy.
            if not result.dry_run:
                raise CommandError("Import przerwany z powodu niepoprawnych danych.")

    def _print_row_errors(self, row_errors: Iterable[tuple[int, list]]) -> None:
        self.stderr.write("Wystąpiły błędy w poszczególnych wierszach:")
        for row, errors in row_errors:
            for err in errors:
                message = getattr(err, "error", err)
                self.stderr.write(f"  wiersz {row}: {message}")
