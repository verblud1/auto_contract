import json
import os
from pathlib import Path

script_dir = Path(__file__).parent
parent_dir = script_dir.parent

odir = parent_dir / "data" / "config.json"
folder = "/config.json"

with open(odir) as file:
    schools_data = json.load(file)
school_type='district'
i=0
for school in schools_data:
        #print(f"ключ: {имя школы}")
        print("name:", f"{school['schools'][school_type][i]['name']}.docx")
         
        count_money = school['schools'][school_type][i]['child_count']
        
        
        
        name_doc = f"{school['schools'][school_type][i]['name']} договор от 12.09"
        print(count_money)
        print(name_doc)
        i=i+1