# goby-map-editor
Create map/game data for goby projects, inspired by the issue: https://github.com/nskins/goby/issues/82 

## Requirements
\>= Python 3.6  
Tkinter (apt install python-tk if running it doesn't work immediately)

## Making Changes
First I strongly recommend perusing the Goby source.  It's not complex so you should be able to get a confidently strong idea of what's going on in an hour or two.  The code under /lib/goby is what we'll be targeting

This program works by reading all the member values of any given class (from my source code, not Goby's :P), then generates data fields which will be used to populate a new instance of that object.  Making this generic was the best thing I could do to make any future changes to goby as easy as possible, since as soon as the program detects a new class in 'objects.py' it creates new buttons and text fields for it.  
  
I am trying to force static typing in this project, since each class has its own data types, and keeping track of what data type goes where is a royal pain with dynamic typing.  Hence why we need Python 3.6 or up.

## Roadmap
- [x] Groundwork (base app, basic text fields, etc)  
- [x] Export data to JSON or YAML (YAML would be preferred) 
- [ ] Export map to CSV 
- [ ] Contextual form fields (dropdown for custom game objects, textfield for others)   
    - [x] Textfield forms for most, dropdowns for custom objects
    - [ ] Handling of lists (multi-select)
  - [x] Automatic dropdowns for any instances of created game objects, provided the class exists  
  - [ ] Dictionary support (stats, equipment, etc)
- [ ] Form field validation  
- [ ] Support for Item game object  
  - [x] Food
  - [ ] Equipment
  - [ ] Etc?
- [x] Support for default Event game objects
  - [x] Chest  
  - [x] NPC  
  - [x] Shop
- [ ] Edit created object types
- [ ] Open existing files for editing
- [ ] A less cumbersome UX (WIP)
- [ ] Better UI (WIP)
