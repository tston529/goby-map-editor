import yaml
def convert_int(s: str):
    try: 
        x = int(s)
        return x
    except ValueError:
        return None

def is_int(s: str) -> bool:
    try: 
        int(s)
        return True
    except ValueError:
        return False

def to_yaml(obj_types: dict, map_tiles: list):
    import os
    map_editor_dir = os.path.dirname(os.path.abspath(__file__))
    
    for key in obj_types:
        filename = key.lower() + ".yml"
        with open(map_editor_dir+"/../output/"+filename, 'w+') as fn:
            fn.write("--- !!" + key + "\n")
            fn.write(yaml.dump(obj_types[key]))
            fn.write("---")

def map_to_csv(map_name: str, map_tiles: list):
    import os
    map_editor_dir = os.path.dirname(os.path.abspath(__file__))
    
    import csv
    with open(map_editor_dir+"/../output/"+map_name+".csv", "w+") as _map:
        wr = csv.writer(_map)
        for row in map_tiles:
            wr.writerow(row)
