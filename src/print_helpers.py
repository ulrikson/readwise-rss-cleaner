from rich.console import Console

CONSOLE = Console()


def print_warning(msg: str) -> None:
    CONSOLE.print(f"[yellow]Warning: {msg}[/yellow]")


def print_error(msg: str) -> None:
    CONSOLE.print(f"[bold red]Error: {msg}[/bold red]")


def print_success(msg: str) -> None:
    CONSOLE.print(f"[bold green]Success: {msg}[/bold green]")


def print_info(msg: str) -> None:
    CONSOLE.print(f"[blue]Info:[/blue] {msg}")


def print_bold(msg: str) -> None:
    CONSOLE.print(f"[bold]{msg}[/bold]")


def print_neutral(msg: str) -> None:
    CONSOLE.print(msg)
