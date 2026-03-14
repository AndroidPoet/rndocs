import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path.home() / ".rndocs" / "docs.db"


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> sqlite3.Connection:
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS docs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            slug      TEXT    UNIQUE NOT NULL,
            title     TEXT    NOT NULL,
            content   TEXT    NOT NULL,
            section   TEXT,
            url       TEXT    NOT NULL,
            synced_at TEXT    DEFAULT (datetime('now'))
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
            title,
            content,
            content='docs',
            content_rowid='id',
            tokenize='porter unicode61'
        );

        CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON docs BEGIN
            INSERT INTO docs_fts(rowid, title, content)
            VALUES (new.id, new.title, new.content);
        END;

        CREATE TRIGGER IF NOT EXISTS docs_au AFTER UPDATE ON docs BEGIN
            INSERT INTO docs_fts(docs_fts, rowid, title, content)
            VALUES ('delete', old.id, old.title, old.content);
            INSERT INTO docs_fts(rowid, title, content)
            VALUES (new.id, new.title, new.content);
        END;

        CREATE TRIGGER IF NOT EXISTS docs_ad AFTER DELETE ON docs BEGIN
            INSERT INTO docs_fts(docs_fts, rowid, title, content)
            VALUES ('delete', old.id, old.title, old.content);
        END;
    """)
    conn.commit()
    return conn


def upsert_doc(conn: sqlite3.Connection, slug: str, title: str, content: str,
               section: Optional[str], url: str) -> None:
    conn.execute("""
        INSERT INTO docs (slug, title, content, section, url, synced_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(slug) DO UPDATE SET
            title     = excluded.title,
            content   = excluded.content,
            section   = excluded.section,
            url       = excluded.url,
            synced_at = excluded.synced_at
    """, (slug, title, content, section, url))
    conn.commit()


def search_docs(query: str, limit: int = 10) -> list[dict]:
    conn = init_db()
    rows = conn.execute("""
        SELECT d.slug, d.title, d.section, d.url,
               snippet(docs_fts, 1, '[', ']', '...', 40) AS snippet
        FROM docs_fts
        JOIN docs d ON d.id = docs_fts.rowid
        WHERE docs_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """, (query, limit)).fetchall()
    return [dict(r) for r in rows]


def get_doc(slug: str) -> Optional[dict]:
    conn = init_db()
    row = conn.execute(
        "SELECT slug, title, content, section, url, synced_at FROM docs WHERE slug = ?",
        (slug,)
    ).fetchone()
    return dict(row) if row else None


def doc_count() -> int:
    conn = init_db()
    return conn.execute("SELECT COUNT(*) FROM docs").fetchone()[0]


def list_docs(section: Optional[str] = None) -> list[dict]:
    conn = init_db()
    if section:
        rows = conn.execute(
            "SELECT slug, title, section, url FROM docs WHERE section = ? ORDER BY title",
            (section,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT slug, title, section, url FROM docs ORDER BY section, title"
        ).fetchall()
    return [dict(r) for r in rows]
