# Alfredo Ulloa
# COMP 467
# Project 4
# The Crucible

import argparse
import sys
from pymongo import MongoClient, errors
import ffmpeg
import vimeo

# Argparse functions
parser = argparse.ArgumentParser()
parser.add_argument("--baselight", "-bl", action="store", help="import baselight file into db")
parser.add_argument("--xytech", "-xt",action="store", help="import xytech file into db")
parser.add_argument("--process", action="store", help="process video file")
parser.add_argument("--output", action="store_true", help="export data into XLS file")

args = parser.parse_args()

# Helper methods
def timecode(frame, fps):
    frames = frame % fps
    total_seconds  = frame // fps
    seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    total_hours = total_minutes // 60
    hours = total_hours % 24
    return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

def find_new_url(baselight_folder, xytech):
    for url in xytech.find():
        if "Planeshifter" in baselight_folder and baselight_folder in url["location"]:
            return url["Workorder"], url["location"]
    return None, None

def find_timecode_range(frame):
    pre_frame = frame - 48
    post_frame = frame + 48
    start = timecode(pre_frame, fps)
    end = timecode(post_frame, fps)
    return f"{start}-{end}"


client = vimeo.VimeoClient(
    token = "0070400c399f5e91c87ad0e80960999c",
    client_id='6b1666c5d4c95d3ecd5941b8dec63a7dab93112d',
    client_secret='xUzuhK2OYRA2ogYXxZ8eAqouKylGckReL4LJyll4Wg/oXJ4b18bFQIZBY1y7uwjIm+SlMrQgm4VbG/Dg0So3NVV/Z4q0ESksXeFB/42hkH3D9foA9m/7TwAFv72rWsPg',
)

# Connect to DB
client = MongoClient('localhost', 27017)
database = client["crucible"]

# Import baselight data to DB
# Excludes preliminary baselight1 directory
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

# Import xytech data to DB
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

if args.process:
    baselight_db = database["baselight"]
    xytech_db = database["xytech"]
    frames = []
    fps = 24

    video_data = ffmpeg.probe(args.process)
    for i in video_data["streams"]:
        if i["index"] == 0:
            video_timecode = i["tags"]["timecode"]
            print(f"Timecode extracted from {args.process} is {video_timecode}")

    # Find all corresponding frames
    contents = baselight_db.find()
    for content in contents:
        folder = content["folder"]
        if "Planeshifter" in folder:
            frames.extend(content["frames"])

    for frame in frames:
        find_timecode_range(frame)

if args.output:
    for content in baselight_db.find():
        folder = content["folder"]
        frames = content["frames"]

        workorder, location = find_new_url(folder, xytech_db)
        if workorder is None or location is None:
            continue
        for frame in frames:
            timecode_range = find_timecode_range(frame)

        print(f"Processing {timecode_range} for workorder {workorder} to {location}")
    print("Exporting data into XLS file...")


