# mtg-data-analysis

## Context
Project created by the Lord of Limited discord user to generate and maintain a database of real draft data that can be used to improve their user win % during Magic The Gathering drafts

## Scope
- Create a consistent DB of draft data
- Define metrics that can be used to inform better pick decisions in draft
- Build a platform to access and compute automatically these metrics

# Draft data importer

These instructions will have you set up a MySQL database loading in draft logs for analysis. It uses [SQLAlchemy](https://www.sqlalchemy.org/) as the ORM layer to turn Python objects into the relevant SQL data (`src/db/model.py` describes the mapping).

## Necessary Installation
1. Ensure Python3 and MariaDB / MySQL are installed (instructions will vary by OS).
1. Install the following python packages: sqlalchemy, mysql-connector-python, pymysql (`pip3 install sqlalchemy mysql-connector-python pymysql` should work.)

## Database setup
Set up a database and user as follows (replace `'this is a password'` with your own password):

```SQL
CREATE DATABASE mtg_draft_logs;
CREATE OR REPLACE USER 'draft_log_code'@'localhost' IDENTIFIED BY 'this is a password';
GRANT ALL PRIVILEGES ON mtg_draft_logs.* to 'draft_log_code'@localhost;
```

You'll also want to make a file named `.secret` and put your database password in it. Protect the file! (e.g. `chmod 600 .secret`)

## Getting data ready
1. Add any relevant JSON file to the `sets` directory. These can be obtained from [mtgjson](https://mtgjson.com/sets.html).
1. Add any draft logs (as exported by MTGO) to the logs directory.

## Running things
1. Run `update_data.sh` to load all the set and card information into the database and load any new draft logs into the database.