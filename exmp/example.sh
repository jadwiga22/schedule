# add - direct

python3 sch_client.py add places --name University --street_name "Good Street" --street_number 22
python3 sch_client.py add events --name "Christmas Eve" --start_date "24-12-2023 17:00" --end_date "24-12-2023 19:00" --place_id 1 --invitees 5 --description "Dinner with family"
python3 sch_client.py add people --name Marek --surname Nowak --email marek@example.com --participates 1 2

# add - api

python3 sch_client.py -a add places --name University --street_name "Good Street" --street_number 22
python3 sch_client.py -a add events --name "Christmas Eve" --start_date "24-12-2023 17:00" --end_date "24-12-2023 19:00" --place_id 1 --invitees 5 --description "Dinner with family"
python3 sch_client.py -a add people --name Marek --surname Nowak --email marek@example.com --participates 1 2

# update - direct

python3 sch_client.py update people --id 60 --name Marek --surname Nowak --email marek@example.com --participates 11 12
python3 sch_client.py update events --id 28 --name "Christmas Eve" --start_date "24-12-2023 10:00" --end_date "24-12-2023 20:00" --place_id 10 --invitees 2 --description "Dinner with family"
python3 sch_client.py update places --id 16 --name University --street_name "Good Street" --street_number 22

# update - api

python3 sch_client.py -a update people --id 47 --name Marek --surname Nowak --email marek@example.com --participates 11 12
python3 sch_client.py -a update events --id 22 --name "Christmas Eve" --start_date "24-12-2023 10:00" --end_date "24-12-2023 20:00" --place_id 10 --invitees 2 --description "Dinner with family"
python3 sch_client.py -a update places --id 16 --name University --street_name "Good Street" --street_number 22

# delete - direct

python3 sch_client.py delete people --id 48
python3 sch_client.py delete events --id 27
python3 sch_client.py delete places --id 14

# delete - api

python3 sch_client.py -a delete people --id 50
python3 sch_client.py -a delete events --id 26
python3 sch_client.py -a delete places --id 13

# info - direct

python3 sch_client.py info people --id 10
python3 sch_client.py info events --id 3
python3 sch_client.py info places --id 4

# info - api 

python3 sch_client.py -a info people --id 10
python3 sch_client.py -a info events --id 3
python3 sch_client.py -a info places --id 4

# lookup - direct (only)

python3 sch_client.py lookup people --surname Kowalski
python3 sch_client.py lookup events --name "Christmas Eve"
python3 sch_client.py lookup places --name "Library"

# info_all - direct (only)

python3 sch_client.py info_all people
python3 sch_client.py info_all events
python3 sch_client.py info_all places