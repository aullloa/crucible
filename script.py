# Alfredo Ulloa
# COMP 467
# Project 4
# The Crucible

import argparse
import sys
import pandas as pd
from pymongo import MongoClient, errors


# Helper methods
def timecode(frame, fps):
    frames = frame % fps
    total_seconds  = frame // fps
    seconds = total_seconds % fps
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    total_hours = total_minutes // 60
    hours = total_hours % 24
    return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

parser = argparse.ArgumentParser()
parser.add_argument("--baselight", "-bl", action="store", help="input baselight file")
parser.add_argument("--xytech", "-xt",action="store", help="input xytech file")

args = parser.parse_args()

# Connect to DB
client = MongoClient('localhost', 27017)
database = client["crucible"]

if args.baselight:
    collection_name = "baselight"
    collection = database[collection_name]
    try:
        baselight_file = open(args.baselight, "r")
        baselight_lines = baselight_file.readlines()

        for line in baselight_lines:
            each_line = line.strip().split()
            url = each_line[0].strip("/baselightfilesystem1")
            frames = list(map(int, each_line[1:]))
            collection.insert_one({"folder": url, "frames": frames})
        print(f"Data from {args.baselight} imported successfully!")
    except FileNotFoundError:
        print(f"{args.baselight} file not found")
        sys.exit(1)
    except errors.ConnectionFailure:
        print("Could not connect to MongoDB")
        sys.exit(1)

if args.xytech:
    collection_name = "xytech"
    collection = database[collection_name]
    try:
        xytech_file = open(args.xytech, "r")
        xytech_lines = xytech_file.readlines()
        for line in xytech_lines:
            if line.__contains__("Workorder"):
                workorder_line = line.strip().split()
                workorder = workorder_line[2]
                continue
            each_line = line.strip().split()
            if not (line.startswith("/")):
                continue
            else:
                url = each_line[0].strip()
                collection.insert_one({"Workorder": workorder, "location": url})
        print(f"Data from {args.xytech} imported successfully!")
    except FileNotFoundError:
        print(f"{args.xytech} file not found")
        sys.exit(1)
    except errors.ConnectionFailure:
        print("Could not connect to MongoDB")
        sys.exit(1)


