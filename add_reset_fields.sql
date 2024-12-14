.backup 'books.db.backup2'

CREATE TABLE users_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(200) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reset_token VARCHAR(100) UNIQUE,
    reset_token_expiry DATETIME
);

INSERT INTO users_new (id, username, email, password, created_at)
SELECT id, username, email, password, created_at FROM users;

DROP TABLE users;
ALTER TABLE users_new RENAME TO users; 