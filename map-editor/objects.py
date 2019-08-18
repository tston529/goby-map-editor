import sys, inspect
from typing import List

class Object:
    '''The generic class from which all other game objects inherit'''
    def __str__(self):
        to_str : str = ""
        keys = get_members(self.__class__.__name__)
        for k in keys:
            to_str = to_str + k + " : " + str(self.__dict__[k]) + "\n"
        return to_str

    def __repr__(self):
        to_str : str = ""
        keys = get_members(self.__class__.__name__)
        for k in keys:
            to_str = to_str + k + " : " + str(self.__dict__[k]) + "\n"
        return to_str

    def populate(self, vals):
        '''Given a list of data, update values of all members with new data'''
        keys = get_members(self.__class__.__name__)
        i = 0
        for k in keys:
            if vals[i] != "":
                self.__dict__[k] = vals[i]
            i+=1
        return self


class Tile(Object):
    # Default graphic for passable tiles.
    DEFAULT_PASSABLE = "·"
    # Default graphic for impassable tiles.
    DEFAULT_IMPASSABLE = "■"

    def __init__(self):
        super().__init__()
        self.passable       : str = "true" # don't use a bool here please, ruby uses lowercase for T/F and strings keep text fields simple
        self.description    : str = ""
        self.events         : list = [] # TODO: static type check as list[Event]; need Event class
        self.monsters       : list[Monster] = []
        self.graphic        : str = None
    
    def get_graphic(self):
        if self.graphic != None and self.graphic != "":
            return self.graphic
        return self.default_graphic()

    def default_graphic(self):
        return (Tile.DEFAULT_PASSABLE if self.passable == "true" else Tile.DEFAULT_IMPASSABLE)

class Monster(Object):
    def __init__(self):
        super().__init__()
        self.name               : str = "Monster"
        self.stats              : dict[str, int] = {":max_hp" : 1, ":hp" : 1, ":attack" : 1, ":defense" : 1, ":agility" : 1}
        self.inventory          : list = [] # TODO: static type check as list[Item]; need Item class
        self.gold               : int = 0
        self.battle_commands    : list[Attack] = []
        self.outfit             : dict = {} # TODO: static type check as list[Item]; need Item class

class Attack(Object):
    def __init__(self):
        super().__init__()
        self.name           : str = "Attack"
        self.strength       : int = 1
        self.success_rate   : int = 100
        self.target         : str = ":enemy" # Not in the official release of Goby yet, I'm gonna put a pull request in for my changes

def get_members(class_name: str) -> List[str]:
    '''
    Returns a list of all member variables in the specified class 
    
    :param class_name str the name of the desired class
    '''
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and name == class_name:
            return obj().__dict__.keys()    