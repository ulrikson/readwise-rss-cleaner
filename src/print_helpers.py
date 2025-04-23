from rich.console import Console

CONSOLE = Console()


def print_warning(msg: str) -> None:
    CONSOLE.print(f"[yellow]Warning:[/yellow] {msg}")


def print_error(msg: str) -> None:
    CONSOLE.print(f"[bold red]Error:[/bold red] {msg}")


def print_success(msg: str) -> None:
    CONSOLE.print(f"[green]Success:[/green] {msg}")


def print_info(msg: str) -> None:
    CONSOLE.print(f"[cyan]Info:[/cyan] {msg}")


def print_bold(msg: str) -> None:
    CONSOLE.print(f"[bold]{msg}[/bold]")


def print_neutral(msg: str) -> None:
    CONSOLE.print(msg)
