#!/usr/bin/env python3
"""Quick Prompter - Fill in prompt templates via CLI."""

import os
import re
import sys
import pyperclip
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

console = Console()

QUESTION_STYLE = "cyan"
RESPONSE_STYLE = "green"


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


def is_directory_question(text: str) -> bool:
    """Check if the question is about a directory or folder."""
    text_lower = text.lower()
    keywords = ["where", "directory", "folder", "which folder"]
    return any(keyword in text_lower for keyword in keywords)


def print_folder_tree(base_path: Path = None, max_depth: int = 2):
    """Print a 2-level deep tree showing only folders."""
    if base_path is None:
        base_path = Path.cwd()

    def print_tree(path: Path, prefix: str = "", depth: int = 0):
        if depth >= max_depth:
            return

        try:
            items = sorted([p for p in path.iterdir() if p.is_dir()])
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                console.print(
                    f"{prefix}{current_prefix}[bold blue]📁 {item.name}/[/bold blue]"
                )

                if depth < max_depth - 1:
                    extension = "    " if is_last else "│   "
                    print_tree(item, prefix + extension, depth + 1)
        except PermissionError:
            pass

    console.print(f"\n[bold]📁 Current folders:[/bold] ({base_path})\n")
    print_tree(base_path)
    console.print()


def build_prompt(content: str, answers: list[tuple[str, str]]) -> str:
    """Replace placeholders with their answers in order."""
    result = content
    for placeholder, answer in answers:
        result = result.replace(placeholder, answer, 1)
    return result


def create_bold_preview(content: str, answers: list[tuple[str, str]]) -> str:
    """Create preview with answers bolded and colored."""
    result = content
    for placeholder, answer in answers:
        if answer != placeholder:  # Only bold/color filled answers
            # Use rich colored bold for the answer
            result = result.replace(placeholder, f"[**green**]{answer}[/**green**]", 1)
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
            default_choice = choices[0] if choices else ""
            console.print(f"\n[{QUESTION_STYLE}]Select:[/]\n")
            for idx, choice in enumerate(choices, 1):
                console.print(f"  [bold]{idx}[/bold] {choice}")

            while True:
                user_input = Prompt.ask(
                    f"\n[{RESPONSE_STYLE}]Enter number[/] [{RESPONSE_STYLE}](default: {default_choice})[/]",
                    default=default_choice,
                    console=console,
                )
                if not user_input.strip():
                    answer = default_choice
                    break
                try:
                    choice_idx = int(user_input) - 1
                    if 0 <= choice_idx < len(choices):
                        answer = choices[choice_idx]
                        break
                    else:
                        console.print(
                            f"[red]Please enter a number between 1 and {len(choices)}[/red]"
                        )
                except ValueError:
                    console.print(f"[red]Please enter a valid number[/red]")
        else:
            # Check if it's a directory question
            if is_directory_question(text):
                print_folder_tree()

                # Find default path containing .planning
                default_path = ""
                try:
                    for root, dirs, _ in os.walk(Path.cwd()):
                        for d in dirs:
                            if ".planning" in d:
                                default_path = str(Path(root) / d)
                                break
                        if default_path:
                            break
                except Exception:
                    pass

                # Clean up the question text (remove trailing ? if present for display)
                question = text.rstrip("?").strip()
                if default_path:
                    answer = Prompt.ask(
                        f"[{QUESTION_STYLE}]{question}[/{QUESTION_STYLE}]?",
                        default=default_path,
                        console=console,
                    )
                else:
                    answer = Prompt.ask(
                        f"[{QUESTION_STYLE}]{question}[/{QUESTION_STYLE}]?",
                        console=console,
                    )
            else:
                answer = Prompt.ask(
                    f"[{QUESTION_STYLE}]{text}[/{QUESTION_STYLE}]?",
                    console=console,
                )

        if answer.strip() and answer != placeholder:
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

    # Show full preview with bolded answers
    bold_preview = create_bold_preview(content, answers)

    # Color the questions and answers in preview
    # Questions are in [brackets], answers are bolded
    preview_styled = bold_preview
    console.print(f"\n[dim]Preview:[/dim]\n")
    console.print(Markdown(preview_styled))


if __name__ == "__main__":
    main()
