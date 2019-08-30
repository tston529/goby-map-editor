import PySimpleGUI as sg
import os, sys, inspect
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
        line = [sg.RButton("", size=(2,1), key="{},{}".format(i,j)) for j in range(x)]
        map_frame.append(line)
    layout.append([sg.Frame('Map', map_frame, title_color="white")])
    
    # Populate a list of all class types ("game objects," e.g. Tile, Monster, etc.)
    obj_names = []
    new_obj_colors = {}
    inheritor_objs = objects.inheritors(objects.Object)
    for obj in objects.get_leaf_classes(objects.Object):
        obj_names.append(obj.__name__)
        if obj.__name__ in inheritor_objs:
            new_obj_colors[obj.__name__] = "darkred"
        else:
            new_obj_colors[obj.__name__] = "darkgreen"

    # Create buttons for game object creation
    create_buttons = []
    for clsname in inheritor_objs:
        row = [sg.Button("New {}".format(clsname), button_color=('white', new_obj_colors[clsname]))]
        for subclass in objects.inheritors_from_classname(clsname):
            row.append(sg.Button("New {}".format(subclass), button_color=('white', new_obj_colors[subclass])))
        create_buttons.append(row)

    # The following will rotate the buttons to be in a vertical arrangement, which looks nicer in my opinion, but
    #   there will be a noticable spacing difference caused by a mismatch in all the button's sizes.
    # import six
    # create_buttons = map(list, six.moves.zip_longest(*create_buttons, fillvalue=sg.Button('', button_color=('#28283c', "#28283c"), border_width=0, disabled=True,size=(10,1)) ))
    
    new_obj_frame = sg.Frame('', create_buttons, title_color="white")
    layout[0].append(new_obj_frame)
    
    map_editor_dir = os.path.dirname(os.path.abspath(__file__))
    
    layout.append([sg.Button("", image_filename=map_editor_dir+"/../resources/icons8-pencil-50.png",
                            key="tool_type_pencil", 
                            image_size=(25, 25), 
                            image_subsample=2, 
                            size=(15,1)),
                   sg.Button("", image_filename=map_editor_dir+"/../resources/icons8-fill-color-50.png",
                             key="tool_type_bucket", 
                             image_size=(25, 25), 
                             image_subsample=2, 
                             size=(15, 1)),
                   sg.Combo([""], key="tile_select",
                            auto_size_text=True, size=(15, 1)),
                   sg.Button('', button_color=('#28283c', "#28283c"),
                             border_width=0, disabled=True, size=(5*x, 1)),
                   sg.Cancel(), sg.Save()])

    window = sg.Window('Map Creator: creating {}'.format(name), layout)

    #  Will be used later to fill single cells (pencil) or to flood fill (bucket)
    tool_type = "pencil"
    while True:
        event, values = window.Read()

        # User clicked Cancel, so just break out of the loop.
        if event in (None, 'Cancel'):
            break

        # Either the pencil or bucket was clicked.
        elif "tool_type" in str(event):
            tool_type = str(event).replace("tool_type_", "")
        
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
                if "Tile" in str(event) and "Tile" in obj_types:
                    window.Element("tile_select").Update(values=[""]+[key for key in obj_types["Tile"].keys()])

        # If the user clicked save, output to file
        elif event in (None, 'Save'):
            helper.to_yaml(obj_types, tiles)
            helper.map_to_csv(name, tiles)
            sg.Popup("Saved all data! :)", title="Success!")
        # Otherwise, the button is a map tile
        else:
            event_str = str(event).split(",")
            x = int(event_str[0])
            y = int(event_str[1])

            if "Tile" in obj_types:

                if tool_type == "pencil":
                    tiles[x][y] = values['tile_select']
                    if values['tile_select'] != "":
                        window.Element(str(event)).Update(obj_types["Tile"][tiles[x][y]].get_graphic())
                    else:
                        window.Element(str(event)).Update("")

                elif tool_type == "bucket":
                    tiles = flood_fill(x, y, tiles, values['tile_select'], tiles[x][y])
                    for i in range(len(tiles)):
                        for j in range(len(tiles[0])):
                            if tiles[i][j]:
                                window.Element(str("{},{}".format(i, j))).Update(obj_types["Tile"][tiles[i][j]].get_graphic())
                            else:
                                window.Element(str("{},{}".format(i, j))).Update('')
            else:
                sg.Popup("No tiles available :(\nCreate a tile type or two and try again", title="Error")
                

def flood_fill(x, y, map_tiles, new_tile_type, tile_type_to_fill) -> list:
    '''
    Fills in an area of like-tiles with another tile type.

    :param x int the current x location of the tile to potentially fill

    :param y int the current y location of the tile to potentially fill

    :new_tile_type str the type of tile to fill in the area with

    :tile_type_to_fill str the type of tile that is being filled in

    :returns the new state of the map
    '''
    if y > len(map_tiles)-1 or y < 0 or x > len(map_tiles[0])-1 or x < 0:
        return map_tiles
    if map_tiles[x][y] != tile_type_to_fill:
        return map_tiles
    
    map_tiles[x][y] = new_tile_type

    map_tiles = flood_fill(x + 1, y, map_tiles, new_tile_type, tile_type_to_fill)  # then i can either go south
    map_tiles = flood_fill(x - 1, y, map_tiles, new_tile_type, tile_type_to_fill)  # or north
    map_tiles = flood_fill(x, y + 1, map_tiles, new_tile_type, tile_type_to_fill)  # or east
    map_tiles = flood_fill(x, y - 1, map_tiles, new_tile_type, tile_type_to_fill)  # or west

    return map_tiles


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
            dropdown_list = [""]
            for sm in sub_members:
                if sm in obj_types:
                    dropdown_list = dropdown_list + [key for key in obj_types[sm].keys()]
            listbox_height = len(dropdown_list) if len(dropdown_list) < 5 else 5
            layout.append([sg.Text("{}: ".format(k)), sg.Listbox(dropdown_list, size=(15,listbox_height))])
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


def main():
    colors = {
        'BACKGROUND' : '#28283c',
        'TEXT'       : 'white',
        'INPUT'      : '#505066'
    }
    sg.SetOptions(background_color=colors['BACKGROUND'],
                text_element_background_color=colors['BACKGROUND'],
                element_background_color=colors['BACKGROUND'],
                text_color=colors['TEXT'],
                input_elements_background_color=colors['INPUT'],
                input_text_color=colors['TEXT'])

    layout = [[sg.Text('Name of map,'), sg.InputText()],
                [sg.Text('Size of map in number of blocks:')],
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
