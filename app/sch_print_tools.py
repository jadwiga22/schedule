# --------- SCHEDULE PROJECT ---------
# ------- Jadwiga Swierczynska -------
# ------------ 30.12.2023 ------------

"""Tools for printing data - objects from database or dicts from API"""

from typing import Any


def print_data_people(p: dict[str, Any]) -> None:
    """Print data of a serialized `Person` object.

    Arguments:

    - `p` - dictionary (serialized `Person` object)"""

    if p is None:
        print("Not found")
        return
    print(f"Person: {p['id']}")
    print(f"Name: {p['name']}")
    print(f"Surname: {p['surname']}")
    print(f"Email: {p['email']}")
    print(f"Participating in events:")
    for e in p['participates']:
        print(f"Event id: {e['id']}, Event name: {e['name']}")
    print("\n")


def print_data_places(p: dict[str, Any]) -> None:
    """Print data of a serialized `Place` object.

    Arguments:

    - `p` - dictionary (serialized `Place` object)"""

    if p is None:
        print("Not found")
        return
    print(f"Place: {p['id']}")
    print(f"Name: {p['name']}")
    print(f"Street name: {p['street_name']}")
    print(f"Street number: {p['street_number']}")
    print(f"Events:")
    for e in p['hosts_event']:
        print(f"Event id: {e['id']}, Event name: {e['name']}")
    print("\n")


def print_data_events(p: dict[str, Any]) -> None:
    """Print data of a serialized `Event` object.

    Arguments:

    - `p` - dictionary (serialized `Event` object)"""

    if p is None:
        print("Not found")
        return
    print(f"Event: {p['id']}")
    print(f"Name: {p['name']}")
    print(f"Start date: {p['start_date']}")
    print(f"End date: {p['end_date']}")
    print(f"Description: {p['description']}")
    print(f"Place id: {p['place_id']}")
    if 'place' in p and p['place'] is not None:
        print(f"Place: {p['place']['name']}")
    print(f"Participants:")
    for e in p['invitees']:
        print(
            f"""Person id: {e['id']}, \
Person name: {e['name']}, Person surname: {e['surname']}""")
    if "collides" in p:
        print(f"Collides with {len(p['collides'])} events:")
        for c in p['collides']:
            print(f"Event id: {c['id']}, Name: {c['name']}")
        print("\n")
    print("\n")


def printer_one(res: dict[str, Any], table: str) -> None:
    """Print serialized database object \
        (or message from the database worker after deletion).

    Arguments:

    - `res` - dictionary to be printed
    - `table` - table name of the dictionary \
        (`"people"`, `"events"` or `"places"`)"""

    func = {
        "people": print_data_people,
        "events": print_data_events,
        "places": print_data_places
    }

    if isinstance(res, dict) and "msg" in res:
        print(res["msg"])
        return

    func[table](res)


def printer(res: dict[str, Any] | list[dict[str, Any]], table: str) -> None:
    """Print single object or a list of objects \
        - according to the type of `res`.

    Arguments:

    - `res` - dictionary or a list of dictionaries \
        to be printed using `printer_one`
    - `table` - table name of the dictionary/dictionaries \
        to be printed (`"people"`, `"events"` or `"places"`)"""
    if isinstance(res, list):
        for r in res:
            printer_one(r, table)
    else:
        printer_one(res, table)
