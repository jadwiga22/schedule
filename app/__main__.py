# --------- SCHEDULE PROJECT ---------
# ------- Jadwiga Swierczynska -------
# ------------ 30.12.2023 ------------

"""Command line application - runs the server \
    and the CLI for the schedule application"""

import sch_server as srv
import sch_client as cli
import logging
from multiprocessing import Process
import os
import flask.cli


def setUp():
    """Initialize a server (disabled app logging)"""

    logging.getLogger('werkzeug').disabled = True
    flask.cli.show_server_banner = lambda *args: None

    app = srv.app

    server = Process(target=app.run)
    server.start()

    return server


def tearDown(server):
    """Shutdown a server"""
    server.terminate()
    server.join()


def main():
    try:
        server = setUp()
        cli.main()
    finally:
        tearDown(server)


if __name__ == "__main__":
    main()
