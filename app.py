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

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', '') or "sqlite:///db.sqlite"

# Remove tracking modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

AvatarHistory = create_classes(db)


def query_results_to_dicts(results):
    return simplejson.dumps(results)

# create route that renders index.html template


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/all")
def all():
    results = db.session.query(
        AvatarHistory.level,
        AvatarHistory.guild,
        AvatarHistory.race,
        AvatarHistory.char_class,
        AvatarHistory.region
    ).all()

    return query_results_to_dicts(results)

def get_selected_race():
    selected_race = request.args.get("race")
    if selected_race == "All":
        return None
    
    return selected_race

@app.route("/api/count_by/<count_by>", defaults={'optional_count_by': None})
@app.route("/api/count_by/<count_by>/<optional_count_by>")
def count_by(count_by, optional_count_by=None):

    selected_race = get_selected_race()
   
    if optional_count_by is None:
        results = db.session.query(
            getattr(AvatarHistory, count_by),
            func.count(getattr(AvatarHistory, count_by)).label("total")
        )

        if selected_race is not None:
            results.filter(AvatarHistory.race == selected_race)

        results = results.group_by(
            getattr(AvatarHistory, count_by)
        ).all()

    else:
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


def get_column_values(for_column, selected_race):
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

    results = db.engine.execute(text("""
        SELECT * FROM avatar_history 
        WHERE UPPER(region) = :region
    """).bindparams(
        region=region.upper().strip()
    ))
    
    return jsonify([dict(row) for row in results])


if __name__ == "__main__":
    app.run(debug=True)
