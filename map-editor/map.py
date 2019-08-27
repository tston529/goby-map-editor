import PySimpleGUI as sg
import sys, inspect
import typing
import objects as objects
import helper as helper

def map_creator(name: str, x: int, y: int):
    '''
    Displays the current state of the map and provides options for creating user-defined types of game objects

    :param name str the name of the map

    :param x int the width of the map

    :param y int the height of the map
    '''

    obj_types = {}
    tiles = [[None for i in range(x)] for j in range(y)]

    layout = []

    # Create the buttons for every tile on the map
    map_frame = []
    for i in range(y):
        line = [sg.RButton("(None)", size=(1,1), key="{},{}".format(i,j)) for j in range(x)]
        map_frame.append(line)
    layout.append([sg.Frame('Map', map_frame)])
    
    # Populate a list of all class types ("game objects," e.g. Tile, Monster, etc.)
    obj_names = []
    new_obj_colors = {}
    x = objects.inheritors(objects.Object)
    for obj in objects.get_leaf_classes(objects.Object):
        obj_names.append(obj.__name__)
        if obj.__name__ in x:
            new_obj_colors[obj.__name__] = "darkred"
        else:
            new_obj_colors[obj.__name__] = "darkgreen"

    # Create buttons for game object creation
    create_buttons = []
    for clsname in x:
        row = [sg.Button("New {}".format(clsname), button_color=('white', new_obj_colors[clsname]))]
        for subclass in objects.inheritors_from_classname(clsname):
            row.append(sg.Button("New {}".format(subclass), button_color=('white', new_obj_colors[subclass])))
        create_buttons.append(row)

    import six
    a = map(list, six.moves.zip_longest(*create_buttons, fillvalue=sg.Button('', button_color=('white', "#DADADA"), border_width=0, disabled=True,size=(10,1)) ))
    
    new_obj_frame = sg.Frame('', a)
    layout[0].append(new_obj_frame)
    print(layout)
    layout.append([sg.Cancel(), sg.Save()])

    window = sg.Window('Map Creator: creating {}'.format(name), layout)

    while True:
        event, _ = window.Read()

        # User clicked Cancel, so just break out of the loop.
        if event in (None, 'Cancel'):
            break
        
        # One of the create buttons was clicked
        elif "New" in str(event):
            # # Extract the class type from the button text
            obj_type = str(event).replace("New ", "")

            if obj_type not in obj_types:
                obj_types[obj_type] = {}

            # Prompt user to define data for an object of that type
            #   and add it to the object dictionary for that object type
            new_obj = create_object(obj_types, obj_type)
            if new_obj != None: # if user didn't hit cancel
                obj_types[obj_type][new_obj[0]] = new_obj[1]

        # If the user clicked save, TODO: output to file
        #   (currently just prints all relevant data to stdout)
        elif event in (None, 'Save'):
            # TODO: output to yaml or json or something parsable
            # I need to update the __repl__ and __str__ to take advantage of this
            helper.to_yaml(obj_types, tiles)

        # Otherwise, the button is a map tile
        else:
            event_str = str(event).split(",")
            x = int(event_str[0])
            y = int(event_str[1])

            changed = False
            if "Tile" in obj_types:
                temp = choose_obj(obj_types["Tile"], x, y)
                if temp != None: # Need this here in case user hits cancel
                    tiles[x][y] = temp
                    changed = True
            else:
                sg.Popup("No tiles available :(\nCreate a tile type or two and try again", title="Error")
            if changed:
                window.Element(str(event)).Update(obj_types["Tile"][tiles[x][y]].get_graphic())

def create_object(obj_types, obj_type) -> (str, objects.Object):
    '''
    Provides a comprehensive list of all data needed to create an instance of an object

    :param obj_types dict[str]Object a dictionary mapping names of nicknames of created objects to their in-game object data  

    :param obj_type str the desired type of object to make
    '''

    layout = []

    members = objects.get_members(obj_type)
   
    for k in members:
        sub_members = [] # will contain a list of all child classes
        k2 = k[:-1].capitalize()  # converts 'monsters' to 'Monster', etc.
        instance_of_class = None

        # If the form field is to contain instances of game objects,
        #   generate a class object of that type
        for name, obj in objects.get_classes():
            if inspect.isclass(obj) and name == k2:
                instance_of_class = obj

        # If the field is to be populated with a selection of game objects
        if instance_of_class:
            leaf_classes = objects.get_leaf_classes(instance_of_class)
            # If it has no children classes, we are going to populate the field 
            #   with game objects of the found type.
            if len(leaf_classes) == 0:
                sub_members.append(k2)
            
            # Otherwise, find all instances of game objects of the type's
            #   child classes and populate the dropdown with them instead.
            else:
                for leaf in leaf_classes:
                    sub_members.append(leaf.__name__)
            dropdown_list = []
            for sm in sub_members:
                if sm in obj_types:
                    dropdown_list = dropdown_list + [key for key in obj_types[sm].keys()]
            layout.append([sg.Text("{}: ".format(k)), sg.Combo(dropdown_list)])
        else:
            layout.append([sg.Text("{}: ".format(k)), sg.InputText()])
    layout.append([sg.Text("Nickname this {}: ".format(obj_type)), sg.InputText()])
    layout.append([sg.OK(), sg.Cancel()])

    window = sg.Window('Create {}'.format(obj_type), layout)
    while True:
        event, values = window.Read()
        if event in (None, 'Cancel'):
            break
        else:
            # Nickname is mandatory and must be unique, since it
            #   will be used as part of selection in a dropdown.
            nickname = values[len(values)-1]
            if len(nickname) == 0:
                sg.Popup("Must provide a nickname for this object.")
            elif nickname in obj_types[obj_type]:
                sg.Popup("{} already exists as a nickname, choose something else.".format(values[0]))
            else:
                window.Close()
                for name, obj in inspect.getmembers(sys.modules[objects.__name__]):
                    if inspect.isclass(obj) and name == obj_type:
                        # The last data member in the list is the nickname, which
                        #   is not a member of any class, so delete it before passing
                        #   it to the object's constructor
                        del values[len(values)-1] 
                        return (nickname, obj().populate(values))
    window.Close()

def choose_obj(obj_types, x=-1, y=-1) -> str:
    '''
    Provides a dropdown selection of all created objects of a specified type

    :param obj_types dict[str]Object a dictionary mapping names of nicknames of created objects to their in-game object data  

    :x int horizontal location in tileset  

    :y int vertical location in tileset 

    :return Returns the nickname of the object type
    '''

    # Populate a dropdown with all nicknames of objects of the specifed type
    layout = [[sg.Combo([key for key in obj_types.keys()])]]
    layout.append([sg.OK(), sg.Cancel()])

    window = None
    if x >= 0 and y >= 0:
        window = sg.Window('{} Creator: ({}, {})'.format(list(obj_types.values())[0].__class__.__name__, x, y), layout)
    else:
        window = sg.Window('{} Creator'.format(list(obj_types.values())[0].__class__.__name__), layout)

    while True:
        event, values = window.Read()
        if event:
            if event in (None, 'Cancel'):
                break
            else:
                window.Close()
                return values[0]
    window.Close()
    return None

def main():
    layout = [  [sg.Text('Name of map,'), sg.InputText()],
                [sg.Text('Size of map in number of blocks')],
                [sg.Text('X'), sg.InputText()],
                [sg.Text('Y'), sg.InputText()],
                [sg.OK(bind_return_key=True), sg.Cancel()]]

    window = sg.Window('Map Creator', layout)

    while True:             
        event, values = window.Read()
        if event in (None, 'Cancel'):
            break
        if event in (None, 'OK'):
            if not (len(values[0]) != 0 and helper.is_int(values[1]) and helper.is_int(values[2])):
                sg.Popup("Ensure all fields are properly filled out first")
            else:
                window.Close()
                map_creator(values[0], int(values[1]), int(values[2]))
                break

main()
