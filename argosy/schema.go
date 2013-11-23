package main

var schema = []string{`
CREATE TABLE IF NOT EXISTS groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT
);
`, `
CREATE TABLE IF NOT EXISTS items (
    hash        CHAR(32) PRIMARY KEY,
    created_on  INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
    file_size   INTEGER NOT NULL,
    width       INTEGER NOT NULL,
    height      INTEGER NOT NULL,

    -- Is an animated GIF?
    is_animated BOOLEAN NOT NULL,

    -- Foreign key for group
    group_id    INTEGER NULL,

    -- Index in group
    group_index INTEGER NULL,

    FOREIGN KEY (group_id) REFERENCES groups(group_id)
);
`, `
CREATE TABLE IF NOT EXISTS tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT NOT NULL
);
`, `
CREATE TABLE IF NOT EXISTS item_tags (
    -- Foreign key for item
    item_hash    CHAR(32) NOT NULL,

    -- Foreign key for tag
    tag_id    INTEGER NOT NULL,

    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
    FOREIGN KEY (item_hash) REFERENCES items(hash)

    -- Composite primary key.
    PRIMARY KEY (item_hash, tag_id)
);
`}
