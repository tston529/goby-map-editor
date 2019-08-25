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
    for key in obj_types:
        filename = key.lower() + ".yml"
        with open(filename, 'w+') as fn:
            fn.write("--- !!" + key + "\n")
            fn.write(yaml.dump(obj_types[key]))
            fn.write("---")