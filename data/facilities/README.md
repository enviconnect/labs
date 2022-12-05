# Facilities

This directory contains information about the facilities shown in the explorer.

 - Each facility has its own .yaml file.

 - The YAML files are concatenated into a single file `facilities.yaml` that is read by the explorer app.

 - **Do not edit `facilities.yaml` directly. Instead, edit each of the facility's YAML files and then concatenate them.**

 - To concatenate the files (e.g., after updating them), run `build_facilities_yaml.ipynb`.