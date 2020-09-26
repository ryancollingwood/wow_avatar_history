# import necessary libraries
import os
from sqlalchemy.sql import select, column, text
from sqlalchemy.sql.expression import func
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
from models import create_classes
import simplejson
from flask_sqlalchemy import SQLAlchemy

"""
Let's setup our Flask application.
"""
app = Flask(__name__)

"""
Next database connection setup.

Lets look for an environment variable 'DATABASE_URL' if there isn't one 
then we'll use a connection to a sqlite database.
"""
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', '') or "sqlite:///db.sqlite"

# Remove tracking modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

"""
Using the `flask_sqlalchemy` library we'll creating our
variable `db` that is the connection to our database
"""
db = SQLAlchemy(app)

"""
from `models.py` we call `create_classes` that we will have 
a reference to the class we defined `AvatarHistory` that is 
bound to the underylying database table.
"""
AvatarHistory = create_classes(db)

# create route that renders index.html template
@app.route("/")
def home():
    """
    Render the index.html template
    """
    return render_template("index.html")

def query_results_to_dicts(results):
    """
    A helper method for converting SQLAlchemy Query objects 
    (https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query)
    to a format that is json serialisable 
    """
    return simplejson.dumps(results)

@app.route("/api/all")
def all():
    """
    This route will return all of data in the database as follows:

    [
        {
            "level": 5, "guild": "Guild Guild -1", "race": "Orc", 
            "char_class": "Warrior", "region": "Durotar"
        }, 
        {
            "level": 9, "guild": "Guild Guild -1", "race": "Orc", 
            "char_class": "Shaman", "region": "Durotar"
        },
    ]
    """
    results = db.session.query(
        AvatarHistory.level,
        AvatarHistory.guild,
        AvatarHistory.race,
        AvatarHistory.char_class,
        AvatarHistory.region
    ).all()

    return query_results_to_dicts(results)

def get_selected_race():
    """
    Helper method for extracting the passed value to `race`
    in the query string - for example.

    http://localhost:5000/api/values/char_class/?race=troll

    Would return `"Troll"`    
    """
    selected_race = request.args.get("race")

    # If we receive "All" from the front-end no filtering
    if selected_race == "All":
        return None

    # Given the characters races in the database are title cased
    # e.g. "Orc" not "orc"
    if selected_race is not None:
        selected_race = selected_race.title()
    
    return selected_race

@app.route("/api/count_by_race")
def count_by_race():
    """
    This route demonstrates an explicit querying of the database
    using the ORM - later we'll have a more dyanimic example of
    querying via the ORM.

    Also demonstating COUNT and GROUP BY equivalent SQL functionality
    https://docs.sqlalchemy.org/en/13/core/functions.html?highlight=count#sqlalchemy.sql.functions.count
    """
    results = db.session.query(
        AvatarHistory.race,
        func.count(AvatarHistory.race).label("total")
    )

    results = results.group_by(
        AvatarHistory.race
    ).all()

    return query_results_to_dicts(results)

"""
Here we have an example of multiple routes pointing to the same pyton function.
This also demonstrates how to do optional parameters on Flask Routes

For instace http://localhost:5000/api/count_by/race passes `"race"` into the 
parameter `count_by`and `optional_count_by` will be `None`.

Whereas http://localhost:5000/api/count_by/race/char_class passes `"race"` into the 
parameter `count_by`and `optional_count_by` will be `"char_class"` 
"""
@app.route("/api/count_by/<count_by>", defaults={'optional_count_by': None})
@app.route("/api/count_by/<count_by>/<optional_count_by>")
def count_by(count_by, optional_count_by=None):
    """
    In order to dyanmically retrieve the attribute passed on the 
    value of `count_by` or `optional_count_by` we will use the built-in
    method `getattr` for a reference see the official python docs:
    https://docs.python.org/3/library/functions.html#getattr

    For instance http://localhost:5000/api/count_by/race/char_class 
    will return data in form of:

    [
        {"race": "Orc", "char_class": "Hunter", "total": 178}, 
        {"race": "Orc", "char_class": "Rogue", "total": 21},
        ...
    ]

    Whereas http://localhost:5000/api/count_by/race will return:
    [
        {"race": "Orc", "total": 359}, 
        {"race": "Tauren", "total": 678}, 
        {"race": "Troll", "total": 503}, 
        {"race": "Undead", "total": 785}
    ]
    """

    # first let's check if we need to filter
    selected_race = get_selected_race()
   
    # let's first handle the case we there is no `optional_count_by`
    if optional_count_by is None:
        results = db.session.query(
            getattr(AvatarHistory, count_by),
            func.count(getattr(AvatarHistory, count_by)).label("total")
        )

        # apply the query stirng filter if present
        if selected_race is not None:
            results = results.filter(AvatarHistory.race == selected_race)

        results = results.group_by(
            getattr(AvatarHistory, count_by)
        ).order_by(
            getattr(AvatarHistory, count_by)
        ).all()

    else:
        # lets handle grouping by two columns
        results = db.session.query(
            getattr(AvatarHistory, count_by),
            getattr(AvatarHistory, optional_count_by),
            func.count(getattr(AvatarHistory, count_by)).label("total")
        )

        if selected_race is not None:
            results = results.filter(AvatarHistory.race == selected_race)

        results = results.group_by(
            getattr(AvatarHistory, count_by),
            getattr(AvatarHistory, optional_count_by)
        ).order_by(
            getattr(AvatarHistory, count_by),
            getattr(AvatarHistory, optional_count_by),
        ).all()

    return query_results_to_dicts(results)


def get_column_values(for_column, selected_race = None):
    """
    Let's get the unique distinct values from column in
    our database, optionally filtering by query string.
    """
    
    value_query = db.session.query(
        func.distinct(getattr(AvatarHistory, for_column))
    )

    if selected_race is not None:
        value_query = value_query.filter(
            AvatarHistory.race == selected_race
        )
    
    values = sorted([x[0] for x in value_query.all()])

    return values


@app.route("/api/values/<for_column>/<group_by>")
@app.route("/api/values/<for_column>/", defaults={'group_by': None})
def values(for_column, group_by = None):
    """
    This route will return all of the values in a column 
    optionally grouped by another column.

    For example http://localhost:5000/api/values/race/
    [
        "Orc", 
        "Tauren", 
        "Troll", 
        "Undead"
    ]

    Whereas http://localhost:5000/api/values/race/char_class
    {
        "Druid": [
            "Tauren", "Tauren", "Tauren", "Tauren", "Tauren", 
            "Tauren", "Tauren", "Tauren", "Tauren", "Tauren"
            ], 
        "Hunter": [
            "Orc", "Orc", "Orc", "Orc", "Orc", "Orc", "Orc",
            "Tauren", "Tauren", "Tauren", "Tauren", "Tauren"
            ]
    } 
    """

    selected_race = get_selected_race()

    if group_by is None:
        values = get_column_values(for_column, selected_race)
        return jsonify(values)

    values_for_groupby = dict()

    group_by_values = get_column_values(group_by, selected_race)

    results = db.session.query(
        getattr(AvatarHistory, group_by),
        getattr(AvatarHistory, for_column),
    )

    if selected_race is not None:
        results = results.filter(
            AvatarHistory.race, selected_race
        )

    results = results.order_by(
        getattr(AvatarHistory, group_by),
        getattr(AvatarHistory, for_column),
    ).all()

    for group in group_by_values:
        values_for_groupby[group] = [x[1] for x in results if x[0] == group]

    return query_results_to_dicts(values_for_groupby)

@app.route("/api/where/<region>")
def where(region):
    """
    This will demonstrate running a SQL Query using the SQLAlchemy 
    execute method. 

    http://localhost:5000/api/where/the%20barrens will return:
    [
        {
            "char_class": "Hunter", 
            "guild": "Guild Guild -1", 
            "id": 6, 
            "level": 16, 
            "race": "Orc", 
            "region": "The Barrens"
        }, 
        {
            "char_class": "Warlock", 
            "guild": "Guild Guild -1", 
            "id": 7, 
            "level": 18, 
            "race": "Orc", 
            "region": "The Barrens"
        }
        ...
    ] 
    """

    """
    Because we using user input we need to a VERY 
    simple attempt to mitigate SQL injection
    using SQLAlchemy sql.text and bindparams
    
    https://docs.sqlalchemy.org/en/13/core/tutorial.html#specifying-bound-parameter-behaviors
    """
    results = db.engine.execute(text("""
        SELECT * FROM avatar_history 
        WHERE UPPER(region) = :region
    """).bindparams(
        region=region.upper().strip()
    ))
    
    """
    result will be a ResultProxy, see:
    https://docs.sqlalchemy.org/en/13/core/connections.html?highlight=execute#sqlalchemy.engine.Engine.execute

    so to convert into something that can be json 
    serialisable we need to iterate over each item 
    in the results and convert into a dictionary 
    and then jsonify the result.
    """
    return jsonify([dict(row) for row in results])


if __name__ == "__main__":
    app.run(debug=True)
