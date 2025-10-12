"""CLI interface for EuroCV."""

import json
from pathlib import Path
from typing import Literal, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from eurocv.core.converter import convert_to_europass
from eurocv.core.models import ConversionResult
from eurocv.core.validate.schema_validator import SchemaValidator

app = typer.Typer(
    name="eurocv",
    help="Convert resumes (PDF/DOCX) to Europass XML/JSON format",
    add_completion=False,
)
console = Console()


@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="Input resume file (PDF or DOCX)", exists=True),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Output JSON file path"),
    out_json: Optional[Path] = typer.Option(None, "--out-json", help="Output JSON file path"),
    out_xml: Optional[Path] = typer.Option(None, "--out-xml", help="Output XML file path"),
    locale: str = typer.Option("en-US", "--locale", "-l", help="Locale (e.g., nl-NL, en-US)"),
    no_photo: bool = typer.Option(False, "--no-photo", help="Exclude photo (GDPR-friendly)"),
    use_ocr: bool = typer.Option(False, "--ocr", help="Use OCR for scanned PDFs"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validate output"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
) -> None:
    """Convert a resume file to Europass format.

    Examples:
        eurocv convert resume.pdf --out output.json
        eurocv convert resume.docx --out-json out.json --out-xml out.xml
        eurocv convert cv.pdf --locale nl-NL --no-photo
    """
    # Determine output format
    output_format: Literal["json", "xml", "both"] = "json"
    if out_xml and not (out or out_json):
        output_format = "xml"
    elif (out or out_json) and out_xml:
        output_format = "both"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Converting resume...", total=None)

        try:
            result = convert_to_europass(
                str(input_file),
                locale=locale,
                include_photo=not no_photo,
                output_format=output_format,
                use_ocr=use_ocr,
                validate=validate,
            )

            progress.update(task, description="[green]Conversion complete!")

        except Exception as e:
            progress.update(task, description="[red]Conversion failed!")
            console.print(f"[red]Error: {str(e)}[/red]")
            raise typer.Exit(1)

    # Handle output
    if output_format == "both":
        # Type guard: result must be ConversionResult when output_format is "both"
        if not isinstance(result, ConversionResult):
            console.print("[red]Error: Expected ConversionResult but got dict[/red]")
            raise typer.Exit(1)
        
        # Save JSON
        json_path = out or out_json
        if json_path:
            if result.json_data:
                _save_json(result.json_data, json_path, pretty)
                console.print(f"[green]✓[/green] JSON saved to: {json_path}")
        else:
            if result.json_data:
                _print_json(result.json_data, pretty)

        # Save XML
        if out_xml and result.xml_data:
            _save_xml(result.xml_data, out_xml)
            console.print(f"[green]✓[/green] XML saved to: {out_xml}")

        # Show validation results
        if validate and result.validation_errors:
            console.print("[yellow]⚠ Validation warnings:[/yellow]")
            for error in result.validation_errors:
                console.print(f"  • {error}")

    elif output_format == "json":
        if out or out_json:
            json_path = out or out_json
            if json_path and isinstance(result, dict):
                _save_json(result, json_path, pretty)
            console.print(f"[green]✓[/green] Saved to: {json_path}")
        else:
            if isinstance(result, dict):
                _print_json(result, pretty)

    elif output_format == "xml":
        if out_xml:
            if isinstance(result, str):
                _save_xml(result, out_xml)
            console.print(f"[green]✓[/green] Saved to: {out_xml}")
        else:
            console.print(result)


@app.command()
def batch(
    input_pattern: str = typer.Argument(..., help="Input file pattern (e.g., '*.pdf')"),
    out_dir: Path = typer.Option(Path("output"), "--out-dir", "-d", help="Output directory"),
    locale: str = typer.Option("en-US", "--locale", "-l", help="Locale"),
    no_photo: bool = typer.Option(False, "--no-photo", help="Exclude photos"),
    use_ocr: bool = typer.Option(False, "--ocr", help="Use OCR for scanned PDFs"),
    parallel: int = typer.Option(1, "--parallel", "-p", help="Number of parallel workers"),
    format: Literal["json", "xml", "both"] = typer.Option("json", "--format", "-f", help="Output format (json/xml/both)"),
) -> None:
    """Batch convert multiple resume files.

    Examples:
        eurocv batch "resumes/*.pdf" --out-dir output/
        eurocv batch "*.docx" --parallel 4 --format both
    """
    from glob import glob

    # Find matching files
    files = glob(input_pattern)

    if not files:
        console.print(f"[yellow]No files found matching: {input_pattern}[/yellow]")
        raise typer.Exit(0)

    # Create output directory
    out_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[blue]Found {len(files)} file(s) to convert[/blue]")

    # Process files
    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Converting files...", total=len(files))

        success_count = 0
        error_count = 0

        for file_str in files:
            file_path = Path(file_str)
            progress.update(task, description=f"[cyan]Converting: {file_path.name}")

            try:
                # Convert
                result = convert_to_europass(
                    str(file_path),
                    locale=locale,
                    include_photo=not no_photo,
                    output_format=format if format != "both" else "both",
                    use_ocr=use_ocr,
                    validate=False,  # Skip validation for batch to speed up
                )

                # Save output
                base_name = file_path.stem

                if format in ["json", "both"]:
                    json_path = out_dir / f"{base_name}.europass.json"
                    if format == "both" and isinstance(result, ConversionResult):
                        if result.json_data:
                            _save_json(result.json_data, json_path, pretty=True)
                    elif isinstance(result, dict):
                        _save_json(result, json_path, pretty=True)

                if format in ["xml", "both"]:
                    xml_path = out_dir / f"{base_name}.europass.xml"
                    if format == "both" and isinstance(result, ConversionResult):
                        if result.xml_data:
                            _save_xml(result.xml_data, xml_path)
                    elif isinstance(result, str):
                        _save_xml(result, xml_path)

                success_count += 1

            except Exception as e:
                console.print(f"[red]✗[/red] {file_path.name}: {str(e)}")
                error_count += 1

            progress.advance(task)

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  [green]✓[/green] Successful: {success_count}")
    if error_count > 0:
        console.print(f"  [red]✗[/red] Failed: {error_count}")


@app.command()
def validate(
    input_file: Path = typer.Argument(..., help="Europass JSON or XML file", exists=True),
    schema: Optional[Path] = typer.Option(None, "--schema", help="Custom schema file"),
) -> None:
    """Validate a Europass JSON or XML file against the schema.

    Examples:
        eurocv validate europass.json
        eurocv validate europass.xml
    """
    console.print(f"[blue]Validating: {input_file}[/blue]")

    try:
        with open(input_file, encoding="utf-8") as f:
            content = f.read()

        validator = SchemaValidator()

        # Determine format
        if input_file.suffix.lower() == ".json":
            data = json.loads(content)
            is_valid, errors = validator.validate_json(data)
        else:
            is_valid, errors = validator.validate_xml(content)

        if is_valid:
            console.print("[green]✓ Validation passed![/green]")
        else:
            console.print("[red]✗ Validation failed:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
) -> None:
    """Start the HTTP API server.

    Examples:
        eurocv serve
        eurocv serve --port 8080 --reload
    """
    try:
        import uvicorn

        console.print(f"[blue]Starting server on {host}:{port}[/blue]")
        console.print(f"[blue]API docs: http://{host}:{port}/docs[/blue]")

        uvicorn.run(
            "eurocv.api.main:app",
            host=host,
            port=port,
            reload=reload,
        )

    except ImportError:
        console.print(
            "[red]FastAPI/uvicorn not installed. Install with: pip install eurocv[api][/red]"
        )
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from eurocv import __version__

    console.print(f"eurocv version {__version__}")


def _save_json(data: dict, path: Path, pretty: bool = True) -> None:
    """Save JSON data to file."""
    with open(path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, f, ensure_ascii=False)


def _print_json(data: dict, pretty: bool = True) -> None:
    """Print JSON data to console."""
    if pretty:
        rprint(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        rprint(json.dumps(data, ensure_ascii=False))


def _save_xml(data: str, path: Path) -> None:
    """Save XML data to file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)


if __name__ == "__main__":
    app()
