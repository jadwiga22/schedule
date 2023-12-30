# --------- SCHEDULE PROJECT ---------
# ------- Jadwiga Swierczynska -------
# ------------ 30.12.2023 ------------

"""Server providing API for actions on database"""

import datetime
from flask import Flask, request, jsonify, Response
import sch_db_tools as dbt
from typing import Any


app: Flask = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///schedule.db"


def parse_time(s: str) -> datetime.datetime:
    """Parse string to `datetime.datetime` object. \
        Replace `"%20"` with `" "` (space) \
            and parse a string with format `"dd-mm-yyyy hh:mm"`.

    Arguments:

    - `s` - string to be parsed"""

    s.replace("%20", " ")
    return datetime.datetime.strptime(s, "%d-%m-%Y %H:%M")


# get parameters from query

def get_people_params() -> dict[str, (None | str | list[str])]:
    """Get parameters from request. \
        Returns a dictionary with keys from `PersonWorker.properties`."""

    params: dict[str, (None | str | list[str])] = {}
    for p in dbt.PersonWorker.properties:
        if p in dbt.PersonWorker.list_properties:
            params[p] = request.args.getlist(p)
        else:
            params[p] = request.args.get(p)
    return params


def get_events_params() -> \
        dict[str, (None | str | list[str] | datetime.datetime)]:
    """Get parameters from request. \
        Returns a dictionary with keys from `EventWorker.properties`."""

    params: dict[str, (None | str | list[str] | datetime.datetime)] = {}
    for p in dbt.EventWorker.properties:
        if p in dbt.EventWorker.list_properties:
            params[p] = request.args.getlist(p)
        else:
            params[p] = request.args.get(p)

    if params["start_date"] is not None \
            and isinstance(params["start_date"], str):
        params["start_date"] = parse_time(params["start_date"])
    if params["end_date"] is not None and isinstance(params["end_date"], str):
        params["end_date"] = parse_time(params["end_date"])

    return params


def get_places_params() -> dict[str, (None | str | list[str] | int)]:
    """Get parameters from request. \
        Returns a dictionary with keys from `PlaceWorker.properties`."""

    params: dict[str, (None | str | list[str] | int)] = {}
    for p in dbt.PlaceWorker.properties:
        if p in dbt.PlaceWorker.list_properties:
            params[p] = request.args.getlist(p)
        else:
            params[p] = request.args.get(p)

    if params["street_number"] is not None \
            and isinstance(params["street_number"], str):
        params["street_number"] = int(params["street_number"])

    return params


# PUT <-> Create

@app.route('/people/', methods=['PUT'])
def put_people() -> Response:
    """Carry out a put request for people. \
        Perform an `add` operation on `people` table, \
            `jsonify` a result and return it."""

    params = get_people_params()
    params["table"] = "people"
    params["action"] = "add"

    resp = dbt.act(params)

    if isinstance(resp, dict):
        print(f"Add: person {resp['id']}")
    return jsonify(resp)


@app.route('/events/', methods=['PUT'])
def put_events() -> Response:
    """Carry out a put request for events. \
        Perform an `add` operation on `events` table, \
            `jsonify` a result and return it."""

    params = get_events_params()
    params["table"] = "events"
    params["action"] = "add"

    resp = dbt.act(params)

    if isinstance(resp, dict):
        print(f"Add: event {resp['id']}")
    return jsonify(resp)


@app.route('/places/', methods=['PUT'])
def put_places() -> Response:
    """Carry out a put request for places. \
        Perform an `add` operation on `places` table, \
            `jsonify` a result and return it."""

    params = get_places_params()
    params["table"] = "places"
    params["action"] = "add"

    resp = dbt.act(params)

    if isinstance(resp, dict):
        print(f"Add: place {resp['id']}")
    return jsonify(resp)


# GET <-> Read

@app.route('/people/', methods=['GET'])
def get_people() -> Response:
    """Carry out a get request for people. \
        Perform an `info` operation on `people` table, \
            `jsonify` a result and return it."""

    params = get_people_params()
    params["table"] = "people"
    params["action"] = "info"

    resp = dbt.act(params)

    print(f"Info: person {params['id']}")
    return jsonify(resp)


@app.route('/events/', methods=['GET'])
def get_events() -> Response:
    """Carry out a get request for events. \
        Perform an `info` operation on `events` table, \
            `jsonify` a result and return it."""

    params = get_events_params()
    params["table"] = "events"
    params["action"] = "info"

    resp = dbt.act(params)

    print(f"Info: event {params['id']}")
    return jsonify(resp)


@app.route('/places/', methods=['GET'])
def get_places() -> Response:
    """Carry out a get request for places. \
        Perform an `info` operation on `places` table, \
            `jsonify` a result and return it."""

    params = get_places_params()
    params["table"] = "places"
    params["action"] = "info"

    resp = dbt.act(params)

    print(f"Info: place {params['id']}")
    return jsonify(resp)


# POST <-> Update

@app.route('/people/', methods=['POST'])
def post_people() -> Response:
    """Carry out a post request for people. \
        Perform an `update` operation on `people` table, \
            `jsonify` a result and return it."""

    params = get_people_params()
    params["table"] = "people"
    params["action"] = "update"

    resp = dbt.act(params)

    print(f"Update: person {params['id']}")
    return jsonify(resp)


@app.route('/events/', methods=['POST'])
def post_events() -> Response:
    """Carry out a post request for events. \
        Perform an `update` operation on `events` table, \
            `jsonify` a result and return it."""

    params = get_events_params()
    params["table"] = "events"
    params["action"] = "update"

    resp = dbt.act(params)

    print(f"Update: event {params['id']}")
    return jsonify(resp)


@app.route('/places/', methods=['POST'])
def post_places() -> Response:
    """Carry out a post request for places. \
        Perform an `update` operation on `places` table, \
            `jsonify` a result and return it."""

    params = get_places_params()
    params["table"] = "places"
    params["action"] = "update"

    resp = dbt.act(params)

    print(f"Update: place {params['id']}")
    return jsonify(resp)


# DELETE <-> Delete

@app.route('/people/', methods=['DELETE'])
def delete_people() -> Response:
    """Carry out a delete request for people. \
        Perform a `delete` operation on `people` table, \
            `jsonify` a result and return it."""

    params = get_people_params()
    params["table"] = "people"
    params["action"] = "delete"

    resp = dbt.act(params)

    print(f"Delete: person {params['id']}")
    return jsonify(resp)


@app.route('/events/', methods=['DELETE'])
def delete_events() -> Response:
    """Carry out a delete request for events. \
        Perform a `delete` operation on `events` table, \
            `jsonify` a result and return it."""

    params = get_events_params()
    params["table"] = "events"
    params["action"] = "delete"

    resp = dbt.act(params)

    print(f"Delete: event {params['id']}")
    return jsonify(resp)


@app.route('/places/', methods=['DELETE'])
def delete_places() -> Response:
    """Carry out a delete request for places. \
        Perform a `delete` operation on `places` table, \
            `jsonify` a result and return it."""

    params = get_places_params()
    params["table"] = "places"
    params["action"] = "delete"

    resp = dbt.act(params)

    print(f"Delete: place {params['id']}")
    return jsonify(resp)


if __name__ == '__main__':
    app.run()
