import context
import unittest
import types
import datetime
import sch_db_tools as dbt
import requests
import sch_server as srv
import logging
from multiprocessing import Process


def parse_time(s):
    return datetime.datetime.strptime(s, "%d-%m-%Y %H:%M")


SERVER = "http://localhost:5000/"


class TestServer(unittest.TestCase):
    def setUp(self):
        """Initialize a server for testing (disabled app logging)"""
        app = srv.app

        app.logger.disabled = True
        log = logging.getLogger('werkzeug')
        log.disabled = True
        log.setLevel(logging.ERROR)

        self.server = Process(target=app.run)
        self.server.start()

    def tearDown(self):
        """Shutdown a server after test"""
        self.server.terminate()
        self.server.join()

    def testPersonAdd(self):
        """Adding a new person (with incorrect email address)"""
        tests = [{"name": "Jan", "surname": "Kowalski",
                  "email": "jan.com", "participates": [3, 1, 5]}]

        for t in tests:
            p = requests.put(SERVER+"people/", params=t)
            self.assertEqual(500, p.status_code,
                             "Error code after giving incorrect email")

    def testPlaceDelete(self):
        """Deleting a place"""
        tests = [{"name": "New Place",
                  "street_name": "Old Street", "street_number": 29}]

        for t in tests:
            p = requests.put(SERVER+"places/", params=t).json()
            cur = requests.delete(SERVER+"places/", params=p).json()
            self.assertEqual(
                {"msg": f"Deleted place {p['id']}"},
                cur, "Correctly deleted a place")

    def testEventUpdate(self):
        """Adding an event and updating it - but with incorrect dates"""
        tests = [{"name": "My Test Event",
                  "start_date": "10-01-2024 10:00",
                  "end_date": "17-01-2024 17:00",
                  "description": "Lorem ipsum",
                  "invitees": [],
                  "place_id": 12}]
        tests_update = [{"end_date": "10-01-2024 09:00"}]

        for t, tu in zip(tests, tests_update):
            p = requests.put(SERVER+"events/", params=t).json()
            for k, v in tu.items():
                p[k] = v
            resp = requests.post(SERVER+"events/", params=p)
            self.assertEqual(500, resp.status_code,
                             "Error code after giving incorrect date")


class TestWorkers(unittest.TestCase):
    def setUp(self):
        """Initialize a session for testing"""
        self.session = dbt.init()

    def testPersonAdd(self):
        """Adding a new person"""
        tests = [{"name": "Jan", "surname": "Kowalski",
                  "email": "jan@example.com", "participates": []}]

        for t in tests:
            with self.session:
                p = dbt.PersonWorker(t).add(self.session)
                cur = p.serialize()
                cur = {k: v for k, v in cur.items() if k != "id"}
                self.assertEqual(t, cur, "Correctly added new person")

                self.session.commit()

    def testPlaceUpdate(self):
        """Updating non-existing place"""
        tests = [{"id": 9999999999, "name": "New Place"}]

        for t in tests:
            with self.session:
                self.assertRaises(
                    AttributeError, dbt.PlaceWorker(t).update, self.session)
                self.session.commit()

    def testEventInfo(self):
        """Adding an event and fetching info about it"""
        tests = [{"name": "Test Event",
                  "start_date": parse_time("10-01-2024 10:00"),
                  "end_date": parse_time("17-01-2024 17:00"),
                  "description": "Lorem ipsum",
                  "invitees": [],
                  "place_id": 12}]

        for t in tests:
            with self.session:
                p = dbt.EventWorker(t).add(self.session)
                cur = dbt.EventWorker({"id": p.id}).info(
                    self.session).serialize_basic()

                cur = {k: v for k, v in cur.items() if k != "collides"}
                t["id"] = p.id
                self.assertEqual(t, cur, "Correctly fetches info about event")

                self.session.commit()


if __name__ == "__main__":
    unittest.main()
