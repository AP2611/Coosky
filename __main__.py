import json
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .ollama_client import OllamaClient, call_recipes
from .video import normalize_and_validate, fallback_search_url
from .prompt import SYSTEM_PROMPT, build_user_prompt, JSON_SCHEMA_INSTRUCTIONS


app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def main(
    ingredients: str = typer.Option(..., "--ingredients", help="Comma-separated ingredients"),
    servings: int = typer.Option(2, "--servings", help="Number of servings"),
    diet: Optional[str] = typer.Option(None, "--diet", help="Dietary preference"),
    model: str = typer.Option("mistral", "--model", help="Ollama model name"),
    base_url: str = typer.Option("http://localhost:11434", "--base-url", help="Ollama base URL"),
):
    client = OllamaClient(base_url=base_url, model=model)

    user_prompt = (
        build_user_prompt(ingredients, servings, diet)
        + "\n\n"
        + JSON_SCHEMA_INSTRUCTIONS
    )

    console.print("[bold]Contacting local model...[/bold]")
    result = call_recipes(client, SYSTEM_PROMPT, user_prompt)

    dishes = result.get("dishes", [])
    if not dishes:
        console.print("[red]No structured dishes found. Try adjusting ingredients or model.[/red]")
        console.print_json(json.dumps(result, ensure_ascii=False))
        raise typer.Exit(code=1)

    for dish in dishes:
        console.rule(f"[bold green]{dish.get('title', 'Dish')}[/bold green]")
        info_table = Table(show_header=False)
        info_table.add_row("Suitability", str(dish.get("suitability", "")))
        info_table.add_row("Difficulty", str(dish.get("difficulty", "")))
        info_table.add_row("Servings", str(dish.get("servings", "")))
        info_table.add_row("Total Time (min)", str(dish.get("total_time_minutes", "")))
        if dish.get("cuisine"):
            info_table.add_row("Cuisine", str(dish.get("cuisine")))
        if dish.get("youtube_url"):
            normalized_url, ok = normalize_and_validate(str(dish.get("youtube_url")))
            info_table.add_row("YouTube", normalized_url or "Unavailable")
        console.print(info_table)

        if dish.get("missing_ingredients"):
            console.print("[yellow]Suggested additional ingredients:[/yellow]")
            for mi in dish["missing_ingredients"]:
                name = mi.get("name", "")
                qty = mi.get("quantity", "") or ""
                reason = mi.get("reason", "") or ""
                console.print(f"- {name} {f'({qty})' if qty else ''} {f'- {reason}' if reason else ''}")

        if dish.get("ingredients"):
            console.print("[bold]Ingredients:[/bold]")
            for ing in dish["ingredients"]:
                name = ing.get("name", "")
                qty = ing.get("quantity", "") or ""
                console.print(f"- {name}{f' - {qty}' if qty else ''}")

        if dish.get("steps"):
            console.print("[bold]Steps:[/bold]")
            for i, step in enumerate(dish["steps"], start=1):
                desc = step.get("description", "")
                dur = step.get("duration_minutes", "")
                console.print(f"{i}. {desc} ({dur} min)")

        # If video invalid, provide a search fallback
        if dish.get("youtube_url"):
            normalized_url, ok = normalize_and_validate(str(dish.get("youtube_url")))
            if not ok:
                query = dish.get("title") or "cooking tutorial"
                console.print(f"[yellow]Video unavailable. Try: {fallback_search_url(query)}[/yellow]")

    if result.get("notes"):
        console.rule("Notes")
        console.print(str(result["notes"]))


if __name__ == "__main__":
    app()


