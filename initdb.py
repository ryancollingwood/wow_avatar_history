import os
import csv
from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy import DateTime, Float, Integer, String

meta = MetaData()

os_env_db_url = os.environ.get('DATABASE_URL', '')
connection = os_env_db_url or "sqlite:///db.sqlite"


print("connection to databse")
print("os env", os.environ.get('DATABASE_URL', ''))
engine = create_engine(connection)

if not engine.has_table("avatar_history"):
    print("Creating Table")

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

    seed_data = list()

    with open('data/wowah_sample.csv', newline='') as File: #the csv file is stored in a File object

        reader = csv.DictReader(File)       #csv.reader is used to read a file
        for row in reader:
            seed_data.append(row)
    
    with engine.connect() as conn:
        conn.execute(new_table.insert(), seed_data)

    print("Seed Data Imported")
else:
    print("Table already exists")

print("initdb complete")