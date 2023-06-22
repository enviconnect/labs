import os

import gspread

# import pandas (needed for the data table)
import pandas as pd

path = os.getcwd()

print(path)

# change to the working directory. This should be the location of the "app.py"
os.chdir("labs")
print(path)

sa = gspread.service_account(
    filename=".secrets/lidars-per-mw-fae432341abd.json")
sheet = sa.open("lidar applications survey responses")
work_sheet = sheet.worksheet("Form responses 1")
df_in = pd.DataFrame(work_sheet.get_all_records())

# save it
df_in.to_pickle("data/lidar_usage_survey/lidar_usage_survey.pkl")
