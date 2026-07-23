CREATE TABLE IF NOT EXISTS papers (
    pmid TEXT PRIMARY KEY,
    title TEXT,
    abstract TEXT,
    journal TEXT,
    pub_year INTEGER,
    authors TEXT
);
