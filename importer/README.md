# Draft data importer

These instructions will have you set up a MySQL database loading in draft logs for analysis. It uses [SQLAlchemy](https://www.sqlalchemy.org/) as the ORM layer to turn Python objects into the relevant SQL data (`model.py` describes the mapping).

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
1. Run `python3 set_importer.py` to load all the set and card information into the database.
1. Run `python3 log_importer.py` to load draft logs into the database.