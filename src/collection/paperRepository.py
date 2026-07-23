"""SQLite persistence for normalized PubMed papers."""

from __future__ import annotations;

from pathlib import Path;
import sqlite3;

from .models import Paper;

DEFAULT_DATABASE_PATH = Path("data/pubmed.db");
MIGRATION_PATH = Path(__file__).resolve().parents[2] / "migrations" / "001_papers.sql";


def connectDatabase(databasePath: str | Path = DEFAULT_DATABASE_PATH) -> sqlite3.Connection:
    """Open the collection database and create the papers table when needed."""

    path = Path(databasePath);
    path.parent.mkdir(parents = True, exist_ok = True);
    connection = sqlite3.connect(path);
    ensurePapersTable(connection);
    return connection;


def ensurePapersTable(connection: sqlite3.Connection) -> None:
    """Apply the owned papers-table migration."""

    schema = MIGRATION_PATH.read_text(encoding = "utf-8");
    connection.executescript(schema);
    connection.commit();


def savePapers(connection: sqlite3.Connection, papers: list[Paper]) -> tuple[int, int]:
    """Save papers transactionally and return inserted and skipped counts."""

    insertedCount = 0;
    skippedCount = 0;

    with connection:
        for paper in papers:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO papers (
                    pmid, title, abstract, journal, pub_year, authors
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    paper.pmid,
                    paper.title,
                    paper.abstract,
                    paper.journal,
                    paper.pubYear,
                    paper.authors,
                ),
            );

            if cursor.rowcount == 1:
                insertedCount += 1;
            else:
                skippedCount += 1;

    return insertedCount, skippedCount;
