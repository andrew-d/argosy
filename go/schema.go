package main

var schema = `
CREATE TABLE IF NOT EXISTS groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT
);

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
    FOREIGN KEY (group_id) REFERENCES groups(group_id)

    group_index INTEGER NULL,
);

CREATE TABLE IF NOT EXISTS tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS item_tags (
    -- Foreign key for item
    item_id    INTEGER NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(item_id)

    -- Foreign key for tag
    tag_id    INTEGER NOT NULL,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)

    -- Composite primary key.
    PRIMARY KEY (item_id, tag_id);
);
`
