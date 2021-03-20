CREATE TABLE "author" (
    "author_id" serial   NOT NULL,
    "author_name" text   NOT NULL unique,
    "birth_date" text   NOT NULL,
    "birth_place" text   NOT NULL,
    "description" text   NOT NULL,
    CONSTRAINT "pk_author" PRIMARY KEY (
        "author_id"
     )
);

CREATE TABLE "quote" (
    "quote_id" int   NOT NULL unique,
    "author_name" text   NOT NULL,
    "quote_text" text   NOT NULL,
    CONSTRAINT "pk_quote" PRIMARY KEY (
        "quote_id"
     )
);

CREATE TABLE "tags" (
    "quote_id" int   NOT NULL,
    "tags_list" text   NOT NULL,
    CONSTRAINT "pk_tags" PRIMARY KEY (
        "quote_id", "tags_list"
     )
);

ALTER TABLE "tags" ADD CONSTRAINT "fk_tags_quote_id" FOREIGN KEY("quote_id")
REFERENCES "quote" ("quote_id");

ALTER TABLE "quote" ADD CONSTRAINT "fk_quote_author_name" FOREIGN KEY("author_name")
REFERENCES "author" ("author_name");

