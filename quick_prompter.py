#!/usr/bin/env python3
"""Quick Prompter - Fill in prompt templates via CLI."""

import re
import sys
import pyperclip
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

console = Console()


def parse_placeholders(content: str) -> list[tuple[str, str, str]]:
    """Extract placeholders from content.

    Format: [content]
    Returns list of (placeholder_key, display_text, input_type) in order of appearance

    Input types:
    - "question" - if content contains "?"
    - "selection" - if content contains "OR" or "/"
    """
    pattern = r"\[([^\]]+)\]"
    matches = re.finditer(pattern, content)

    placeholders = []
    for match in matches:
        inner = match.group(1).strip()
        placeholder = match.group(0)

        # Determine input type
        if "?" in inner:
            input_type = "question"
        elif " OR " in inner or " / " in inner:
            input_type = "selection"
        else:
            input_type = "question"  # default to question

        placeholders.append((placeholder, inner, input_type))

    return placeholders


def get_choices(text: str) -> list[str]:
    """Split text by OR or / to get choices."""
    # Try splitting by OR first, then /
    if " OR " in text:
        return [c.strip() for c in text.split(" OR ")]
    elif " / " in text:
        return [c.strip() for c in text.split(" / ")]
    return []


def build_prompt(content: str, answers: list[tuple[str, str]]) -> str:
    """Replace placeholders with their answers in order."""
    result = content
    for placeholder, answer in answers:
        result = result.replace(placeholder, answer, 1)
    return result


def main():
    if len(sys.argv) != 2:
        console.print("[red]Usage:[/red] python quick_prompter.py <prompt_file.md>")
        console.print("[dim]Placeholders: [question?] or [choice1 OR choice2][/dim]")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        console.print(f"[red]Error:[/red] File not found: {file_path}")
        sys.exit(1)

    content = file_path.read_text()
    placeholders = parse_placeholders(content)

    if not placeholders:
        console.print("[yellow]No placeholders found in file.[/yellow]")
        console.print("[dim]Use [question?] or [choice1 OR choice2] format[/dim]")
        sys.exit(0)

    # Show header
    console.print()
    console.print(
        Panel.fit(f"[bold cyan]📝 {file_path.name}[/bold cyan]", border_style="cyan")
    )

    answers = []

    # Ask questions in rounds
    for i, (placeholder, text, input_type) in enumerate(placeholders, 1):
        console.print(f"\n[dim]Step {i}/{len(placeholders)}[/dim]")

        if input_type == "selection":
            choices = get_choices(text)
            console.print(f"[bold]Select:[/bold] {text}")
            answer = Prompt.ask("Choose", choices=choices, console=console)
        else:
            # Clean up the question text (remove trailing ? if present for display)
            question = text.rstrip("?").strip()
            answer = Prompt.ask(f"[bold]{question}[/bold]?", console=console)

        if answer.strip():
            answers.append((placeholder, answer.strip()))
        else:
            # Keep placeholder if no answer
            answers.append((placeholder, placeholder))

    # Build final prompt
    final_prompt = build_prompt(content, answers)

    # Copy to clipboard
    pyperclip.copy(final_prompt)

    # Show preview
    console.print()
    console.print(
        Panel.fit(
            "[bold green]✓ Copied to clipboard![/bold green]", border_style="green"
        )
    )

    # Show truncated preview
    preview = final_prompt[:500] + "..." if len(final_prompt) > 500 else final_prompt
    console.print(f"\n[dim]Preview (first 500 chars):[/dim]")
    console.print(Markdown(preview))


if __name__ == "__main__":
    main()
