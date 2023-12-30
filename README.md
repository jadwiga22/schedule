# schedule

Schedule - Python command-line application for managing events, participants and places. Provides direct access to database or via API. 


## Running the application

### Using `schedule.pyz`

You can simply run the standalone version of the application (if you have a Python interpreter). 

```
python3 schedule.pyz
```

### With the application code

Firstly go into the `app` directory. Then run

```
pip install -r requirements.txt
```

Now you can simply run the application with

```
python3 sch_client.py
```

Remember to also run the `sch_server.py` application, if you want to access the database via API.

## How to use `schedule`?

The application provides the manual. You can access it via

```
python3 schedule.pyz --help
```

or

```
python3 sch_client.py --help
```

### Usage examples

You can find some usage examples in `exmp/example.sh` (only for `sch_client.py` file - but they are also valid for the `schedule.pyz` file; simply replace `sch_client.py` with `schedule.pyz`).

## Running tests

To test the application simply run

```
cd tests
python3 test.py -v
```
