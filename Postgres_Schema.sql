CREATE TABLE "quote" (
    --COL---------TYPE-------NULL
    "quote_id"    int       NOT NULL,
    "author_name" text      NOT NULL,
    "quote_text"  text      NOT NULL,
        ---SET KEYS
        PRIMARY KEY ("quote_id"),
        FOREIGN KEY("author_name")
            REFERENCES "author"("author_name")
    );

CREATE TABLE "author" (
    --COL------------------TYPE-------NULL
    "author_id"           serial    NOT NULL,
    "author_name"         text      NOT NULL,
    "birth_date"          int       NOT NULL,
    "birth_place"         text      NOT NULL,
    "author_description"  text      NOT NULL,
        ---SET KEYS
        PRIMARY KEY ("author_id")
    );

CREATE TABLE "tags" (
    ---COL------TYPE----NULL
    "quote_id"  int    NOT NULL,
    "tags"      text   NOT NULL,
        ---SET KEYS
        PRIMARY KEY ("quote_id"),
        FOREIGN KEY ("quote_id")
            REFERENCES "quotes"("quote_id")
    );

