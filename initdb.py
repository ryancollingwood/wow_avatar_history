import os
import csv
from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy import DateTime, Float, Integer, String

"""
This script is used to create the postgres database and
populate it with data. This is often referred to as 'seeding'.
"""

"""
We'll be using the SQLAlchemy ORM approach to defining, creating,
and inserting into our database. For this we'll need an instance 
the SQLAlchemy of `MetaData` object - for more detail see:
https://docs.sqlalchemy.org/en/13/core/metadata.html
"""
meta = MetaData()

"""
For deployment purposes we'll be using an environment variable
for storing the details of our database connection. This way
we can keep the login and password of our database outside of our
code.
"""
os_env_db_url = os.environ.get('DATABASE_URL', '')

"""
If we don't have an environment variable 'DATABASE_URL' the value in
`os_env_db_url` will be an empty string. In which case we will use
a sqlite database - this allows us to do development without having to
configure a SQL Database. I wouldn't advise using a sqlite database in
the case you're expecting multiple concurrent access to the database,
but for development purposes it should be fine.
"""
connection = os_env_db_url or "sqlite:///db.sqlite"

"""
Let's establish a connection to our database.
"""
print("connection to databse")
print("os env", os.environ.get('DATABASE_URL', ''))
engine = create_engine(connection)

"""
If the database table already exists we will not be adding to the 
database.
"""
if not engine.has_table("avatar_history"):
    print("Creating Table")

    """
    Here we'll define the table using the SQLAlchemy ORM interface
    https://docs.sqlalchemy.org/en/13/core/metadata.html#creating-and-dropping-database-tables
    """
    new_table = Table(
        'avatar_history', meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('level', Integer),
        Column('guild', String),
        Column('race', String),
        Column('char_class', String),
        Column('region', String),
    )

    meta.create_all(engine)
    
    print("Table created")

    """
    Let's read in the csv data and put into a list to read into
    our newly created table
    """
    seed_data = list()

    with open('data/wowah_sample.csv', newline='') as input_file:
        reader = csv.DictReader(input_file)       #csv.reader is used to read a file
        for row in reader:
            seed_data.append(row)
    
    """
    With our newly created table let's insert the row we've read in
    and with that we're done
    """
    with engine.connect() as conn:
        conn.execute(new_table.insert(), seed_data)

    print("Seed Data Imported")
else:
    print("Table already exists")

print("initdb complete")