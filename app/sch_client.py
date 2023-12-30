# --------- SCHEDULE PROJECT ---------
# ------- Jadwiga Swierczynska -------
# ------------ 30.12.2023 ------------

"""CLI client - performs database actions directly or through API"""

import argparse
import datetime
import sch_db_tools as dbt
import sch_print_tools as prt
import requests
from typing import Union, Any
import sys

SERVER = "http://localhost:5000/"

# PARSING ------------------------------------


def parse_time(s: str) -> datetime.datetime:
    """Parse time and return `datetime.datetime` object.

    Arguments:

    - `s` -- string in format `dd-mm-yyyy hh:mm`"""

    return datetime.datetime.strptime(s, "%d-%m-%Y %H:%M")


def parse_option_values(
        parser: argparse.ArgumentParser, properties: dict[str, str],
        possibles: list[str], requirements: list[str],
        list_parse: list[str], date_parse: list[str],
        int_parse: list[str]) -> None:
    """Create options in command-line argument parser.

    Arguments:

    - `parser` - `argparse.ArgumentParser` object
    - `properties` - dictionary with descritpion of properties (options)\
        that will be displayed (i. e. names of the options\
             are the keys and the values are the descriptions)
    - `possibles` - possible options \
        (all keys from the `properties` dictionary)
    - `requirements` - list of required options' names
    - `list_parse` - list of options' names that should be parsed as a list
    - `date_parse` - list of options' names that should be parsed as a date
    - `int_parse` - list of options' names that should be parsed as a date
    """

    for p in possibles:
        if p in list_parse:
            parser.add_argument(f"--{p}", required=p in requirements,
                                help=properties[p] +
                                " (required)"
                                if p in requirements else properties[p],
                                nargs="*")
        elif p in int_parse:
            parser.add_argument(f"--{p}", required=p in requirements,
                                help=properties[p] +
                                " (required)"
                                if p in requirements else properties[p],
                                type=int)
        elif p in date_parse:
            parser.add_argument(f"--{p}", required=p in requirements,
                                help=properties[p] +
                                " (required)"
                                if p in requirements else properties[p],
                                type=parse_time)
        else:
            parser.add_argument(f"--{p}", required=p in requirements,
                                help=properties[p] +
                                " (required)"
                                if p in requirements else properties[p])


def parse() -> argparse.Namespace:
    """Parse arguments from command line and return them as a dictionary.
    """

    properties: dict[str, dict[str, str]] = {
        "people": dbt.PersonWorker.properties,
        "events": dbt.EventWorker.properties,
        "places": dbt.PlaceWorker.properties
    }
    requirements: dict[str, dict[str, list[str]]] = {
        t: {
            "add": [p for p in properties[t] if p != "id"],
            "update": ["id"],
            "lookup": ["name"] if t != "people" else ["surname"],
            "info": ["id"],
            "info_all": [],
            "delete": ["id"]
        } for t in ["people", "events", "places"]
    }
    possibles: dict[str, dict[str, list[str]]] = {
        t: {
            a: (requirements[t][a]
                if a != "update" else list(properties[t].keys()))
            for a in requirements[t]
        } for t in ["people", "events", "places"]
    }

    list_parse: list[str] = ["participates", "invitees"]
    date_parse: list[str] = ["start_date", "end_date"]
    int_parse: list[str] = ["street_number", "place_id", "id"]

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description="Command-line application for managing events,\
            participants and places of events. \
                Directly performing actions on databases or through API.",
        epilog="Have fun!"
    )

    parser.add_argument("-a", "--api", action="store_true",
                        help="Get data using API")

    subparser_action = parser.add_subparsers(
        description="Action to be performed",
        required=True,
        dest="action",
        help="add - adding new record, \
            update - updating a record, \
            lookup - lookup a record with given name \
                (unavailable through API), \
            info - get data of a record with given id, \
            info_all - get data of all records (unavailable through API), \
            delete - remove a record with given id")

    for a in ["add", "update", "lookup", "info", "info_all", "delete"]:
        subparser = subparser_action.add_parser(
            a, description=f"Performing action {a}")
        subsubp = subparser.add_subparsers(
            description=f"Table for which action {a} will be performed",
            dest="table",
            required=True,
            help="people - participants data (e.g. name, surname), \
                    events - events data (e.g. name, dates), \
                    places - places of the events data (e.g. name, street)")
        for t in ["people", "events", "places"]:
            subsubsubp = subsubp.add_parser(
                t,
                description=f"Performing action {a} on {t} table")
            parse_option_values(
                subsubsubp, properties[t], possibles[t][a],
                requirements[t][a], list_parse, date_parse, int_parse)

    args: argparse.Namespace = parser.parse_args()
    return args


def api_access(instr: dict[str, Any]) -> dict[str, Any] | list[dict[str, Any]]:
    """Access database through API.

    Arguments:

    - `instr` -- dictionary containing parameters of the database query \
        ( `action`, `table` and parameters required by the database function)
    """

    action = instr["action"]
    table = instr["table"]

    # fixing format
    if "start_date" in instr and instr["start_date"] is not None:
        instr["start_date"] = instr["start_date"].strftime("%d-%m-%Y %H:%M")
    if "end_date" in instr and instr["end_date"] is not None:
        instr["end_date"] = instr["end_date"].strftime("%d-%m-%Y %H:%M")

    reqs: dict[str, Any] = {
        "add": requests.put,
        "update": requests.post,
        "info": requests.get,
        "delete": requests.delete
    }

    res: requests.Response = reqs[action](SERVER+table+"/", params=instr)

    return res.json()


def direct_access(instr: dict[str, Any]) -> dict[str, Any] \
        | list[dict[str, Any]]:
    """Directly access the database.

    Arguments:

    - `instr` - dictionary containing parameters of the database query \
        (`action`, `table` and parameters required by the database function)
    """

    s = dbt.act(instr)
    return s


def eval(instr: dict[str, Any]) -> None:
    """Evaluate given instruction.

    Arguments:

    - `instr` - dictionary containing parameters of the database query \
        (e.g. `api`, `action`, `table` and parameters \
            required by the database function)
    """

    table = instr["table"]
    api = instr["api"]

    if api:
        s = api_access(instr)
    else:
        s = direct_access(instr)

    prt.printer(s, table)


def main():
    args = vars(parse())
    # print("Parsed args", args, "\n-------------------------\n")

    eval(args)

    print("-------------------------\n\
| Successfully executed |\n\
-------------------------")


if __name__ == "__main__":
    main()
