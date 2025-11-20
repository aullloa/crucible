# Alfredo Ulloa
# COMP 467
# Project 4
# The Crucible

import argparse

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
parser.add_argument("--baselight", "-bl", action="store_true", help="input baselight file")
parser.add_argument("--xytech", "-xt",action="store_true", help="input xytech file")
