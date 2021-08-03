CREATE TABLE IF NOT EXISTS mainmenu (
    id integer PRIMARY KEY AUTOINCREMENT,
    title text NOT NULL,
    url text NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id integer PRIMARY KEY AUTOINCREMENT,
    username text NOT NULL,
    email text NOT NULL,
    phone text NOT NULL,
    psw text NOT NULL,
    avatar BLOB DEFAULT NULL,
    time text NOT NULL
);

