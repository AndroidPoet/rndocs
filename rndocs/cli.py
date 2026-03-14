import json
import sys

import click

from .db import doc_count, get_doc, list_docs, search_docs


@click.group()
def cli():
    """rndocs — React Native docs, offline."""


@cli.command()
@click.option("--quiet", "-q", is_flag=True, help="Suppress progress output.")
@click.option("--delay", default=0.25, show_default=True, help="Seconds between requests.")
def sync(quiet: bool, delay: float):
    """Download all React Native docs to local SQLite database."""
    from .scraper import sync as do_sync
    success, errors = do_sync(verbose=not quiet, delay=delay)
    click.echo(f"\nDone. {success} pages stored, {errors} errors.")


@cli.command()
@click.argument("query")
@click.option("--limit", "-n", default=10, show_default=True, help="Max results.")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def search(query: str, limit: int, as_json: bool):
    """Search React Native docs."""
    results = search_docs(query, limit)

    if not results:
        click.echo(f"No results for '{query}'.", err=True)
        sys.exit(1)

    if as_json:
        click.echo(json.dumps(results, indent=2))
        return

    click.echo(f"\n{len(results)} result(s) for '{query}':\n")
    for r in results:
        section = f"  [{r['section']}]" if r.get("section") else ""
        click.echo(click.style(f"  {r['title']}", fg="cyan", bold=True) + click.style(section, fg="yellow"))
        click.echo(f"  slug: {r['slug']}  →  {r['url']}")
        click.echo(f"  ...{r['snippet']}...")
        click.echo()


@cli.command()
@click.argument("slug")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def get(slug: str, as_json: bool):
    """Get full content of a doc page by slug (e.g. 'flatlist', 'animated')."""
    doc = get_doc(slug)

    if not doc:
        click.echo(f"No doc found for '{slug}'. Try: rndocs search {slug}", err=True)
        sys.exit(1)

    if as_json:
        click.echo(json.dumps(doc, indent=2))
        return

    section = f" [{doc['section']}]" if doc.get("section") else ""
    click.echo(click.style(f"\n# {doc['title']}", fg="cyan", bold=True) + click.style(section, fg="yellow"))
    click.echo(click.style(f"URL: {doc['url']}", fg="bright_black"))
    click.echo(click.style(f"Synced: {doc['synced_at']}\n", fg="bright_black"))
    click.echo(doc["content"])


@cli.command()
@click.option("--section", "-s", default=None, help="Filter by section.")
def ls(section: str):
    """List all stored doc pages."""
    docs = list_docs(section)
    if not docs:
        msg = f"No docs in section '{section}'." if section else "No docs stored. Run: rndocs sync"
        click.echo(msg, err=True)
        sys.exit(1)

    current_section = None
    for d in docs:
        sec = d.get("section") or "Other"
        if sec != current_section:
            current_section = sec
            click.echo(click.style(f"\n{sec}", fg="yellow", bold=True))
        click.echo(f"  {d['slug']:<45} {d['title']}")


@cli.command()
def stats():
    """Show database stats."""
    count = doc_count()
    if count == 0:
        click.echo("No docs stored. Run: rndocs sync")
    else:
        click.echo(f"{count} docs stored at ~/.rndocs/docs.db")
