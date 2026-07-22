"""Typer-powered CLI for Dopemux session orchestration."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from chatx.dopemux.factory import SessionFactory
from chatx.dopemux.session import ProfileOverlay, SessionMode

app = typer.Typer(
    name="dopemux",
    help="Start and manage Dopemux orchestration sessions.",
    add_completion=False,
)

_console = Console()


def _resolve_mode(alt_routing: bool, mobile: bool) -> SessionMode:
    """Determine the session mode from CLI flags."""

    if alt_routing or mobile:
        return SessionMode.HAPPY
    return SessionMode.STANDARD


@app.command()
def start(
    alt_routing: bool = typer.Option(
        False,
        "--alt-routing",
        help="Legacy flag. Starts the mobile-control (happy) session.",
        rich_help_panel="Routing",
    ),
    mobile: bool = typer.Option(
        False,
        "--mobile",
        help="Alias for --alt-routing. Starts the mobile-control (happy) session.",
        rich_help_panel="Routing",
    ),
    profile_overlay: Path | None = typer.Option(
        None,
        "--profile-overlay",
        "-p",
        help="Path to an optional JSON overlay applied to the session profile.",
        rich_help_panel="Session",
    ),
) -> None:
    """Start a Dopemux session."""

    mode = _resolve_mode(alt_routing=alt_routing, mobile=mobile)
    overlay = None
    if profile_overlay:
        try:
            overlay = ProfileOverlay.from_path(profile_overlay)
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            _console.print(f"[bold red]Error:[/bold red] {exc}")
            raise typer.Exit(1) from exc

    if alt_routing and not mobile:
        _console.print(
            "[yellow]`--alt-routing` is legacy and now maps to the mobile-control happy session.[/yellow]",
        )

    if mobile and alt_routing:
        _console.print("[cyan]`--mobile` alias acknowledged.[/cyan]")

    factory = SessionFactory()
    session = factory.create_session(mode=mode, profile_overlay=overlay)

    descriptor = "happy (mobile-control)" if mode is SessionMode.HAPPY else "standard"
    _console.print(f"[bold green]Started {descriptor} session[/bold green]")
    _console.print(f"Router: {session.router.__class__.__name__}")
    if session.profile_overlay:
        _console.print(f"Profile overlay: {session.profile_overlay.name}")
