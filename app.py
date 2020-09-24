# import necessary libraries
import os
from sqlalchemy.sql import select, column
from sqlalchemy.sql.expression import func
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
from models import create_classes
import simplejson

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '') or "sqlite:///db.sqlite"

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

@app.route("/api/count_by/<count_by>")
def count_by(count_by):
    results = db.session.query(
        getattr(AvatarHistory, count_by),
        func.count(getattr(AvatarHistory, count_by)).label("total")
    ).group_by(
        getattr(AvatarHistory, count_by)
    ).all()

    return query_results_to_dicts(results)

@app.route("/api/values/<for_column>/<group_by>")
def values(for_column, group_by):

    values_for_groupby = dict()

    group_by_values = sorted([x[0] for x in db.session.query(
        func.distinct(getattr(AvatarHistory, group_by))
    ).all()])

    results = db.session.query(
        getattr(AvatarHistory, group_by),
        getattr(AvatarHistory, for_column),
    ).order_by(
        getattr(AvatarHistory, group_by),
        getattr(AvatarHistory, for_column),
    ).all()

    for group in group_by_values:
        values_for_groupby[group] = [x[1] for x in results if x[0] == group]


    return query_results_to_dicts(values_for_groupby)


if __name__ == "__main__":
    app.run()
