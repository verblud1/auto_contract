import json
import os
from pathlib import Path

script_dir = Path(__file__).parent
parent_dir = script_dir.parent

odir = parent_dir / "data" / "config.json"
folder = "/config.json"

with open(odir) as file:
    data = json.load(file)

for school in school_data:
    print(item["schools"]["town"][2]["name"])