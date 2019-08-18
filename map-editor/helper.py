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