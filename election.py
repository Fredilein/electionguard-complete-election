#!/usr/local/bin/python3
import json
import requests
import os

API_URL = "http://localhost:5000"
HEADERS = {'Content-Type': 'application/json'}

# election_name = input("Election Name: ")
election_name = "election_results"

# Path and Filenames
# I believe it's currently not possible to have them outside the electionguard-web-api folder (Server needs to access them...)
export_path = "../data/" + election_name
encrypted_ballots_file_name = "encrypted-ballots"
encrypted_ballots_resolved_file_name = export_path + "/" + encrypted_ballots_file_name
registered_ballots_file_name = "registered-ballots"
registered_ballots_resolved_file_name = export_path + "/registered-ballots"
tally_results_file_name = "tallies"



print("\n### Create Election")

num_trustees = input("Number of trustees: ")
threshold = input("How many trustees are needed for tallying?: ")
election_path = input("Path to election.json file: (default './election.json') ")
if not election_path:
    election_path = "./election.json"

with open(election_path, "r") as ef:
    election = json.load(ef)

url = API_URL + "/electionguard"
data = {
    'config': {
        'numberOfTrustees': num_trustees,
        'threshold': threshold
    },
    'election': election
}
data_str = json.dumps(data)
res_create = requests.post(url, data=data_str, headers=HEADERS)
res_create_json = res_create.json()
print(res_create_json)



print("\n### Initialize Encryption")

electionguardconfig = res_create_json["electionGuardConfig"]

url = API_URL + "/electionguard/InitializeEncryption"
data = {
    "election": election,
    "electionGuardConfig": electionguardconfig,
    "exportPath": export_path,
    "exportFileName": encrypted_ballots_file_name
}
data_str = json.dumps(data)
res_init = requests.put(url, data=data_str, headers=HEADERS)
res_init_json = res_init.json()
print(res_init_json)



print("\n### Voting: Enter your votes in the Vue Ballot Marking Device now. Important: Remember ballot ID's")
print("Come back here when done")



print("\n### Load Ballots")

ballot_count = input("Number of ballots: (Not manually in the future) ")

encrypted_file_name_manual = input("Paste encrypted ballots file name (located in the web-api/data/election_results/): ")
if not encrypted_file_name_manual:
    encrypted_file_name_manual = "encrypted-ballots_2020_3_9"
encrypted_ballots_resolved_file_name = "/Users/adi/Documents/Studium/bachelor-thesis/electionguard/electionguard-web-api/data/election_results/" + encrypted_file_name_manual


url = API_URL + "/electionguard/LoadBallots"
data = {
    "startIndex": 0,
    "count": ballot_count,
    "importFileName": encrypted_ballots_resolved_file_name
}
data_str = json.dumps(data)
res_load = requests.post(url, data=data_str, headers=HEADERS)
res_load_json = res_load.json()
print(res_load_json)



print("\n### Record Ballots")

cast_ballots = input("Enter comma separated cast id's: ")
spoild_ballots = input("Enter comma separated spoild id's: ")


cast_ballots_list = cast_ballots.split(",")
spoild_ballots_list = spoild_ballots.split(",")

if cast_ballots_list[0] == "":
    cast_ballots_list = []
if spoild_ballots_list[0] == "":
    spoild_ballots_list = []

url = API_URL + "/electionguard/RecordBallots"
data = {
    "ballots": res_load_json,
    "CastBallotIds": cast_ballots_list,
    "SpoildBallotIds": spoild_ballots_list,
    "exportPath": export_path,
    "exportFileNamePrefix": registered_ballots_file_name
}
print(data)
data_str = json.dumps(data)
print(data_str)
res_record = requests.post(url, data=data_str, headers=HEADERS)
# res_record_json = res_record.json()
print(res_record.text)



print("\n### Tally Votes")

election_map = res_create_json["electionMap"]
trustee_keys = res_create_json["trusteeKeys"]
# registered_ballots_resolved_file_name = "../data/" + election_name + "/registered-ballots"


url = API_URL + "/electionguard/tallyVotes"
data = {
    "electionGuardConfig": electionguardconfig,
    "electionMap": election_map,
    "trusteeKeys": trustee_keys,
    "registeredBallotsFileName": registered_ballots_resolved_file_name,
    "exportPath": export_path,
    "exportFileNamePrefix": tally_results_file_name
}
data_str = json.dumps(data)
with open("temp.txt", "w") as f:
    f.write(data_str)

# input("Press Enter to tally votes")

res_tally = requests.post(url, data=data_str, headers=HEADERS)
res_tally_json = res_tally.json()
print(res_tally_json)


print("\n### Formatted Results")

for i, contest in enumerate(election["contests"]):
    print("Contest {}: {}".format(i, contest["title"]))
    if contest["type"]== "Candidate":
        for j, candidate in enumerate(contest["candidates"]):
            print("{}: {}".format(candidate["name"], res_tally_json["tallyResults"][i]["candidates"][j]))
    elif contest["type"] == "YesNo":
        print("Yes: {}".format(res_tally_json["tallyResults"][i]["yes"]))
        print("No: {}".format(res_tally_json["tallyResults"][i]["no"]))
    else:
        print("Contest type not yet supported")



