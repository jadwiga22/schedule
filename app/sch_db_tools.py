# --------- SCHEDULE PROJECT ---------
# ------- Jadwiga Swierczynska -------
# ------------ 30.12.2023 ------------

"""Database tools - structure of database and workers for actions"""


from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, MappedColumn
from sqlalchemy import Table, Column, Integer, ForeignKey, String, \
    DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List
from sqlalchemy.orm import validates
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import datetime
from typing import Any


class Base(DeclarativeBase):
    pass


participation = Table(
    "person_event",
    Base.metadata,
    Column("event_id", ForeignKey("Events.id")),
    Column("person_id", ForeignKey("People.id")))


class Event(Base):
    """Class of events.

    Apart from properties explicitly mentioned below `Event` objects \
        may also contain `collides` property \
            informing about time collisions with other events.
    """
    __tablename__ = "Events"
    __allow_unmapped__ = True

    id: MappedColumn[Any] = mapped_column(Integer, primary_key=True)
    """Id of the event (integer), primary key. Automatically generated."""

    name: MappedColumn[Any] = mapped_column(String, nullable=False)
    """Name of the event. Must not be empty."""

    start_date: MappedColumn[Any] = mapped_column(DateTime, nullable=False)
    """Start date of the event - must not be greater than `end_date`."""

    end_date: MappedColumn[Any] = mapped_column(DateTime, nullable=False)
    """End date of the event - must not be less than `start_date`"""

    description: MappedColumn[Any] = mapped_column(String, nullable=False)
    """Description of the event - must be at least 3 characters long."""

    invitees: Mapped[List[Person]] = relationship(
        secondary=participation, back_populates="participates")
    """List of `Person` object - people invited to the event."""

    place_id: MappedColumn[Any] = mapped_column(
        Integer, ForeignKey('Places.id'))
    """Id of the place of the event."""

    place: Mapped[Place] = relationship("Place", back_populates="hosts_event")
    """`Place` object - place of the event"""

    collides: list[Event]

    def serialize_basic(self: Event) -> dict[str, Any]:
        """Non-recursively serialize \
            (`Person` objects from `invitees` list  \
                and `Place` object from `place` \
                will *not* be serialized)."""

        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    def serialize(self: Event) -> dict[str, Any]:
        """Recursively serialize:

        - `Person` objects from `invitees` list will be serialized \
            using `serialize_basic` method from `Person` class
        - `Place` object from `place` will be serialized \
            using `serialize_basic` method from `Place` class
        - `Event` objects from `collides` will be serialized \
            using `serialize_basic` method from `Event` class
        - other properties are serialized as in `serialize_basic`"""

        res = self.serialize_basic()
        xs = [p.serialize_basic() for p in self.invitees]
        res["invitees"] = xs
        if self.place is not None:
            res["place"] = self.place.serialize_basic()
        if "collides" in vars(self) and vars(self)["collides"] is not None:
            cs = vars(self)["collides"]
            res["collides"] = [c.serialize_basic() for c in cs]
        return res

    @validates("name")
    def validate_name(self: Event, key: str, name: str) -> str:
        """Check if the `name` is not empty.

        Arguments:

        - `self` - `Event` object
        - `key` - always equal to `"name"` \
            (as the method is automatically invoked by the database)
        - `name` - value of the `name` property
        """
        if len(name) == 0:
            raise ValueError("Name cannot be empty")
        return name

    @validates("description")
    def validate_description(self: Event, key: str, description: str) -> str:
        """Check if the `description` is at least 3 characters long.

        Arguments:

        - `self` - `Event` object
        - `key` - always equal to `"description"` \
            (as the method is automatically invoked by the database)
        - `name` - value of the `description` property
        """
        if len(description) < 3:
            raise ValueError("Description must at least 3 characters long")
        return description

    @validates("start_date", "end_date",)
    def validate_dates(self: Event, key: str, field: datetime.datetime) ->\
            datetime.datetime:
        """Check if the `start_date` is not greater than `end_date`.

        Arguments:

        - `self` - `Event` object
        - `key` - during the first invocation is equal to `"start_date"` \
            and during the second invocation is equal to `"end_date"` \
                (as the method is automatically invoked by the database)
        - `name` - value of the `start_date` and `end_date` property \
            in the first and the second invocation respectively"""
        if key == "start_date":
            if self.end_date is not None and self.end_date < field:
                raise ValueError("End date cannot be less then start date")
        if key == "end_date":
            if field < self.start_date:
                raise ValueError("End date cannot be less then start date")

        return field


class Place(Base):
    """Class of places where the events are held."""
    __tablename__ = "Places"

    id: MappedColumn[Any] = mapped_column(Integer, primary_key=True)
    """Id of the place (integer), primary key. Automatically generated."""

    name: MappedColumn[Any] = mapped_column(String, nullable=False)
    """Name of the place. Must not be empty."""

    street_name: MappedColumn[Any] = mapped_column(String, nullable=False)
    """Street name of the place."""

    street_number: MappedColumn[Any] = mapped_column(Integer)
    """Street number of the place. Must be a positive integer."""

    hosts_event: Mapped[List[Event]] = relationship(
        "Event", back_populates="place")
    """List of the `Event` objects - events held in this place."""

    def serialize_basic(self: Place) -> dict[str, Any]:
        """Non-recursively serialize \
            (`Event` objects from `hosts_event` list \
                will *not* be serialized)."""

        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    def serialize(self: Place) -> dict[str, Any]:
        """Recursively serialize:

        - `Event` objects from `hosts_event` will be serialized \
            using `serialize_basic` function from `Event` class
        - other properties will be serialized as in `serialize_basic`"""

        res = self.serialize_basic()
        xs = [p.serialize_basic() for p in self.hosts_event]
        res["hosts_event"] = xs
        return res

    @validates("name")
    def validate_name(self: Place, key: str, name: str) -> str:
        """Check if the `name` is not empty.

        Arguments:

        - `self` - `Place` object
        - `key` - always equal to `"name"` \
            (as the method is automatically invoked by the database)
        - `name` - value of the `name` property
        """

        if len(name) == 0:
            raise ValueError("Name cannot be empty")
        return name

    @validates("street_number")
    def validate_street_number(self: Place, key: str,
                               street_number: int) -> int:
        """Check if the `street_number` is a positive integer.

        Arguments:

        - `self` - `Event` object
        - `key` - always equal to `"street_number"` \
            (as the method is automatically invoked by the database)
        - `street_number` - value of the `street_number` property
        """

        if (not isinstance(street_number, int)) or street_number <= 0:
            raise ValueError("Street number must be positive number")
        return street_number


class Person(Base):
    """Class of people - events' participants."""
    __tablename__ = 'People'

    id: MappedColumn[Any] = mapped_column(Integer, primary_key=True)
    """Id of the person (integer), primary key. Automatically generated."""

    name: MappedColumn[Any] = mapped_column(String, nullable=False)
    """Name of the person."""

    surname: MappedColumn[Any] = mapped_column(String, nullable=False)
    """Surname of the person. Must not be empty."""

    email: MappedColumn[Any] = mapped_column(String, nullable=False)
    """Email of the person. Must contain `@` character."""

    participates: Mapped[List[Event]] = relationship(
        secondary=participation, back_populates="invitees")
    """List of `Event` objects - events in which this person participates. """

    def serialize_basic(self: Person) -> dict[str, Any]:
        """Non-recursively serialize \
            (`Event` objects from `participates` list \
                will *not* be serialized)."""

        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    def serialize(self: Person) -> dict[str, Any]:
        """Recursively serialize:

        - `Event` objects from `participates` will be serialized \
            using `serialize_basic` function from `Event` class
        - other properties will be serialized as in `serialize_basic`"""

        res = self.serialize_basic()
        xs = [p.serialize_basic() for p in self.participates]
        res["participates"] = xs
        return res

    @validates("surname")
    def validate_surname(self: Person, key: str, surname: str) -> str:
        """Check if the surname is not empty.

        Arguments:

        - `self` - `Person` object
        - `key` - always equal to `"surname"` \
            (as the method is automatically invoked by the database)
        - `surname` - value of the `surname` property"""

        if len(surname) == 0:
            raise ValueError("Surname cannot be empty")
        return surname

    @validates("email")
    def validate_email(self: Person, key: str, email: str) -> str:
        """Check if the email contains `@` character.

        Arguments:

        - `self` - `Person` object
        - `key` - always equal to `"email"` \
            (as the method is automatically invoked by the database)
        - `email` - value of the `email` property"""

        if "@" not in email:
            raise ValueError("Incorrect email address")
        return email


# DB workers ---------------------------

class Worker():
    """Base class for database workers - performing actions on database."""

    def __init__(self: Worker, dict: dict[str, Any],
                 properties: dict[str, Any]) -> None:
        """Initialize a worker - set attributes listed in `properties` \
            basing on the dictionary `dict` \
                (`dict` *must* contain all properties from `properties`)."""

        for prop in properties:
            setattr(self, prop, dict[prop] if prop in dict else None)

    def updateWorker(self: Worker, p: Base | None,
                     properties: dict[str, Any]) -> None:
        """Update a database object - set attributes of `p` \
            listed in `properties` basing on the `self` properties \
                (`self` *does not have to* contain all properties \
                    from `properties`).

        Arguments:

        - `self` - `Worker` object
        - `p` - `Base` object (`Event`, `Place` or `Person`) \
            which will be updated
        - `properties` - dictionary of possible properties """

        for prop in properties:
            self_prop = getattr(self, prop)
            if self_prop is not None:
                setattr(p, prop, self_prop)


class PersonWorker(Worker):
    """Worker for `Person` class. \
        Performs adding, updating, \
            fetching info about one or all `Person` objects, \
                looking up `Person` objects with particular surname \
                    and deleting."""

    properties = {"id": "Person id",
                  "name": "Person name",
                  "surname": "Person surname",
                  "email": "Person email",
                  "participates":
                  "List of event ids in which this person participates"}
    """Dictionary with description of the properties \
        of the `Person` objects."""

    list_properties = ["participates"]
    """List of `Person` properties that are lists."""

    id: int | None
    name: str | None
    surname: str | None
    email: str | None
    participates: list[int] | list[Event]

    def __init__(self: PersonWorker, dict: dict[str, Any]):
        super().__init__(dict, PersonWorker.properties)

    def add(self: PersonWorker, session: Session) -> Person:
        """Add a `Person` object to a database \
            basing on `self` properties. Return created `Person` object.

        Arguments:

        - `self` - `PersonWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        p = Person(name=self.name, surname=self.surname, email=self.email)
        events_db = session.query(Event).filter(
            Event.id.in_(self.participates)).all()
        p.participates = events_db
        session.add(p)
        session.flush()
        return p

    def update(self: PersonWorker, session: Session) -> Person | None:
        """Update a `Person` object in a database \
            basing on `self` properties. Return updated `Person` object.

        Arguments:

        - `self` - `PersonWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        if self.participates is not None:
            self.participates = session.query(Event).filter(
                Event.id.in_(self.participates)).all()
        p = session.query(Person).filter(Person.id == self.id).first()
        super().updateWorker(p, PersonWorker.properties)
        session.flush()
        return p

    def info(self: PersonWorker, session: Session) -> Person | None:
        """Get info about a `Person` object from a database \
            with `id` equal to `self.id`. Return `Person` object.

        Arguments:

        - `self` - `PersonWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        p = session.query(Person).filter(Person.id == self.id).first()
        return p

    def info_all(self: PersonWorker, session: Session) -> list[Person]:
        """Get info about all `Person` objects from a database. \
            Return list of `Person` objects.

        Arguments:

        - `self` - `PersonWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        people = session.query(Person).all()
        return people

    def lookup(self: PersonWorker, session: Session) -> list[Person]:
        """Get info about all `Person` objects \
            with `surname` equal to `self.surname`. \
                Return list of `Person` objects.

        Arguments:

        - `self` - `PersonWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        people = session.query(Person).filter(
            Person.surname == self.surname).all()
        return people

    def delete(self: PersonWorker, session: Session) -> dict[str, str]:
        """Delete a `Person` object from a database \
            with `id` equal to `self.id`. \
                Return dictionary with information about `id` \
                    of the deleted person.

        Arguments:

        - `self` - `PersonWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        p = session.query(Person).filter(Person.id == self.id).first()
        session.delete(p)
        return {"msg": f"Deleted person {self.id}"}


class PlaceWorker(Worker):
    """Worker for `Place` class. \
        Performs adding, updating, \
            fetching info about one or all `Place` objects, \
                looking up `Place` objects with particular name \
                    and deleting."""

    properties = {"id": "Place id",
                  "name": "Place name",
                        "street_name": "Street name",
                        "street_number": "Street number"}
    """Dictionary with description of the properties of the `Place` objects."""

    id: int
    name: str | None
    street_name: str | None
    street_number: int | None

    list_properties: list[str] = []
    """List of `Place` properties that are lists."""

    def __init__(self: PlaceWorker, dict: dict[str, Any]) -> None:
        super().__init__(dict, PlaceWorker.properties)

    def add(self: PlaceWorker, session: Session) -> Place | None:
        """Add a `Place` object to a database \
            basing on `self` properties. Return created `Place` object.

        Arguments:

        - `self` - `PlaceWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        p = Place(name=self.name, street_name=self.street_name,
                  street_number=self.street_number)
        session.add(p)
        session.flush()
        return p

    def update(self: PlaceWorker, session: Session) -> Place | None:
        """Update a `Place` object in a \
            database basing on `self` properties. \
                Return updated `Place` object.

        Arguments:

        - `self` - `PlaceWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        p = session.query(Place).filter(Place.id == self.id).first()
        super().updateWorker(p, PlaceWorker.properties)
        session.flush()
        return p

    def info(self: PlaceWorker, session: Session) -> Place | None:
        """Get info about a `Place` object from a database \
            with `id` equal to `self.id`. Return `Place` object.

        Arguments:

        - `self` - `PlaceWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        p = session.query(Place).filter(Place.id == self.id).first()
        return p

    def info_all(self: PlaceWorker, session: Session) -> list[Place]:
        """Get info about all `Place` objects from a database. \
            Return list of `Place` objects.

        Arguments:

        - `self` - `PlaceWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        places = session.query(Place).all()
        return places

    def lookup(self: PlaceWorker, session: Session) -> list[Place]:
        """Get info about all `Place` objects \
            with `name` equal to `self.name`. \
                Return list of `Place` objects.

        Arguments:

        - `self` - `PlaceWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        places = session.query(Place).filter(Place.name == self.name).all()
        return places

    def delete(self: PlaceWorker, session: Session) -> dict[str, str]:
        """Delete a `Place` object from a database \
            with `id` equal to `self.id`. \
                Return dictionary with information about `id` \
                    of the deleted place.

        Arguments:

        - `self` - `PlaceWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        p = session.query(Place).filter(Place.id == self.id).first()
        session.delete(p)
        return {"msg": f"Deleted place {self.id}"}


class EventWorker(Worker):
    """Worker for `Event` class. \
        Performs adding, updating, \
            fetching info about one or all `Event` objects, \
                looking up `Event` objects with particular name \
                    and deleting."""

    properties = {"id": "Event id",
                  "name": "Event name",
                        "start_date":
                          "Start date of the event ('dd-mm-yyyy hh:mm')",
                        "end_date":
                          "End date of the event ('dd-mm-yyyy hh:mm')",
                        "description": "Description (at least 3 characters)",
                        "invitees": "List of invited people ids",
                        "place_id": "Id of the event place"}

    """Dictionary with description of the properties of the `Event` objects."""

    id: int
    name: str | None
    start_date: str | None
    end_date: str | None
    description: str | None
    invitees: list[Person] | list[int] | None
    place_id: int | None
    collides: list[Event] | list[int] | None

    list_properties: list[str] = ["invitees"]
    """List of `Event` properties that are lists."""

    def __init__(self: EventWorker, dict: dict[str, Any]) -> None:
        super().__init__(dict, EventWorker.properties)

    @staticmethod
    def time_collision(event: Event, session: Session) -> list[Event]:
        """Return list of `Event` objects with which `event` collides.

        Arguments:

        - `event` - `Event` object
        - `session` - `sqlalchemy.orm.Session` object"""

        return session.query(Event).filter(
            ((event.start_date <= Event.start_date)
             & (Event.start_date <= event.end_date))
            | ((Event.start_date <= event.start_date)
               & (event.start_date <= Event.end_date)))\
            .filter(Event.id != event.id).all()

    def add(self: EventWorker, session: Session) -> Event | None:
        """Add an `Event` object to a database \
            basing on `self` properties. \
                Return created `Event` object with `collisions` property \
                    - list of `Event` objects with which this event collides.

        Arguments:

        - `self` - `EventWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        if self.invitees is not None:
            self.invitees = session.query(Person).filter(
                Person.id.in_(self.invitees)).all()
        p = Event(name=self.name, start_date=self.start_date,
                  end_date=self.end_date, description=self.description,
                  invitees=self.invitees, place_id=self.place_id)
        session.add(p)
        session.flush()

        res = p
        collisions = EventWorker.time_collision(p, session)
        res.collides = collisions
        return res

    def update(self: EventWorker, session: Session) -> Event | None:
        """Update an `Event` object in a database \
            basing on `self` properties. \
                Return updated `Event` object with `collisions` property \
                    - list of `Event` objects with which this event collides.

        Arguments:

        - `self` - `EventWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        p = session.query(Event).filter(Event.id == self.id).first()

        if p is None:
            return None

        if self.invitees is not None:
            self.invitees = session.query(Person).filter(
                Person.id.in_(self.invitees)).all()

        if getattr(self, "start_date") is not None:
            p.start_date = datetime.datetime(1, 1, 1, 0, 1)
        if getattr(self, "end_date") is not None:
            p.end_date = datetime.datetime(9999, 12, 31, 23, 59)

        super().updateWorker(p, EventWorker.properties)
        session.flush()

        res = p
        collisions = EventWorker.time_collision(p, session)
        res.collides = collisions
        return res

    def info(self: EventWorker, session: Session) -> Event | None:
        """Get info about an `Event` object from a database \
            with `id` equal to `self.id`. Return `Event` object.

        Arguments:

        - `self` - `EventWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        p = session.query(Event).filter(Event.id == self.id).first()
        return p

    def info_all(self: EventWorker, session: Session) -> list[Event]:
        """Get info about all `Event` objects from a database. \
            Return list of `Event` objects.

        Arguments:

        - `self` - `EventWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        events = session.query(Event).all()
        return events

    def lookup(self: EventWorker, session: Session) -> list[Event]:
        """Get info about all `Event` objects \
            with `name` equal to `self.name`. Return list of `Event` objects.

        Arguments:

        - `self` - `EventWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        events = session.query(Event).filter(Event.name == self.name).all()
        return events

    def delete(self: EventWorker, session: Session) -> dict[str, str]:
        """Delete an `Event` object from a database \
            with `id` equal to `self.id`. \
                Return dictionary with information \
                    about `id` of the deleted event.

        Arguments:

        - `self` - `PersonWorker` object
        - `session` - `sqlalchemy.orm.Session` object"""

        p = session.query(Event).filter(Event.id == self.id).first()
        session.delete(p)
        return {"msg": f"Deleted event {self.id}"}


def init() -> Session:
    """Initialize a session (`sqlalchemy.orm.Session` object) and return it."""

    engine = create_engine("sqlite:///schedule.db", echo=False)
    Base.metadata.create_all(engine)
    return Session(engine)


def act(instr: dict[str, Any]) -> dict[str, Any] | list[dict[str, Any]]:
    """Perform an action on a database according to `dict`.

    Arguments:

    - `dict` - dictionary with info about action \
        that we want to perform (name of that action, table, \
            parameters of the query)"""

    engine = create_engine("sqlite:///schedule.db", echo=False)
    Base.metadata.create_all(engine)

    action = instr["action"]
    table = instr["table"]

    workers = {
        "people": PersonWorker,
        "events": EventWorker,
        "places": PlaceWorker
    }

    s: Worker = workers[table](instr)

    with init() as session:
        DBItem = Person | Event | Place
        s2: DBItem | list[DBItem] | dict[str,
                                         str] = getattr(s, action)(session)
        if s2 is None:
            res: dict[str, Any] | list[dict[str, Any]] = {"msg": "Not found"}
        else:
            if not isinstance(s2, dict):
                if isinstance(s2, list):
                    res = [r.serialize() for r in s2]
                else:
                    res = s2.serialize()
            else:
                res = s2
        session.commit()

    return res
