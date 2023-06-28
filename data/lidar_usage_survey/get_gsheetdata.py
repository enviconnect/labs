import os

import gspread

# import pandas (needed for the data table)
import pandas as pd

# figure out where we are
path = os.getcwd()
print("Current working directory is " + path)

# build path names
filedir = __file__.replace(f"get_gsheetdata.py", "")
approotdir = os.path.dirname(os.path.dirname(os.path.dirname(filedir)))
print("... working directory should be " + approotdir)

# change to the app root directory. This should be the location of the "app.py"
os.chdir(approotdir)
print("... changing working directory; now set to " + os.getcwd())

# get the data
print("Downloading latest data... ")
sa = gspread.service_account(
    filename=".secrets/lidars-per-mw-fae432341abd.json")
sheet = sa.open("lidar applications survey responses")
work_sheet = sheet.worksheet("Form responses 1")
df_in = pd.DataFrame(work_sheet.get_all_records())

print("... found "+ str(len(df_in)) + " data records ... ")

# save it
df_in.to_pickle("data/lidar_usage_survey/lidar_usage_survey.pkl")

print("... save complete!")