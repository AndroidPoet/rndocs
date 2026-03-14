"""
MCP server for rndocs — exposes React Native docs to Claude Code and other AI assistants.

Add to ~/.claude/claude_desktop_config.json (or Claude Code MCP settings):
{
  "mcpServers": {
    "rndocs": {
      "command": "python3",
      "args": ["/Users/ranbirsingh/projects/rndocs/rndocs/mcp_server.py"]
    }
  }
}
"""

from mcp.server.fastmcp import FastMCP

from .db import doc_count, get_doc, list_docs, search_docs

mcp = FastMCP(
    "rndocs",
    instructions=(
        "Search and retrieve React Native documentation stored locally. "
        "Run `rndocs sync` first to populate the database. "
        "Use search_react_native_docs to find pages, then get_react_native_doc for full content."
    ),
)


@mcp.tool()
def search_react_native_docs(query: str, limit: int = 10) -> str:
    """
    Search React Native documentation by keyword or concept.

    Args:
        query: Search terms (e.g. 'FlatList', 'navigation', 'StyleSheet flex')
        limit: Maximum number of results to return (default 10)
    """
    if doc_count() == 0:
        return "No docs stored. Run `rndocs sync` in your terminal first."

    results = search_docs(query, limit)

    if not results:
        return f"No results for '{query}'. Try different terms or run `rndocs sync` to refresh."

    lines = [f"Found {len(results)} result(s) for '{query}':\n"]
    for r in results:
        section = f" [{r['section']}]" if r.get("section") else ""
        lines.append(f"**{r['title']}**{section}")
        lines.append(f"slug: `{r['slug']}`  |  {r['url']}")
        lines.append(f"...{r['snippet']}...")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def get_react_native_doc(slug: str) -> str:
    """
    Get the full content of a React Native doc page by its slug.

    Args:
        slug: The doc page slug (e.g. 'flatlist', 'animated', 'getting-started', 'stylesheet')
              Find slugs using search_react_native_docs first.
    """
    if doc_count() == 0:
        return "No docs stored. Run `rndocs sync` in your terminal first."

    doc = get_doc(slug)

    if not doc:
        # Try a fuzzy search to suggest alternatives
        results = search_docs(slug, 5)
        if results:
            suggestions = ", ".join(f"`{r['slug']}`" for r in results[:3])
            return f"No doc found for slug '{slug}'. Did you mean: {suggestions}?"
        return f"No doc found for slug '{slug}'. Try search_react_native_docs first."

    section = f" [{doc['section']}]" if doc.get("section") else ""
    header = f"# {doc['title']}{section}\n\nURL: {doc['url']}\n\n"
    return header + doc["content"]


@mcp.tool()
def list_react_native_docs(section: str = "") -> str:
    """
    List all available React Native doc pages, optionally filtered by section.

    Args:
        section: Filter by section name (e.g. 'Components', 'APIs', 'Guides'). Leave empty for all.
    """
    if doc_count() == 0:
        return "No docs stored. Run `rndocs sync` in your terminal first."

    docs = list_docs(section or None)

    if not docs:
        return f"No docs found{f' in section {section!r}' if section else ''}."

    lines = [f"{len(docs)} doc(s):\n"]
    current_section = None
    for d in docs:
        sec = d.get("section") or "Other"
        if sec != current_section:
            current_section = sec
            lines.append(f"\n**{sec}**")
        lines.append(f"  `{d['slug']}` — {d['title']}")

    return "\n".join(lines)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
