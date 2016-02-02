import GUIObj
import guiparser
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as fonts
import colors

gui_objects = [] # all gui objs in the designer
selected_object = None # The currently selected gui obj
property_entries = {} # A dict of available property entries
root = None # The tk root window
main_canvas = None # The main canvas to put new gui objs on


def initialize():
    global root, main_canvas, property_entries

    root = tk.Tk()
    root.configure(background=colors.background)

    bold = fonts.Font(weight="bold", size=10)

    style = ttk.Style()
    style.configure('TFrame', background=colors.white_primary)
    style.configure('LightBluePrimaryNavLabel.TLabel', foreground=colors.background, background=colors.lightblue_primary)
    style.configure('LightBluePrimaryFrame.TFrame', background=colors.lightblue_primary)

    main_frame = ttk.Frame(root, style='LightBluePrimaryFrame.TFrame')
    main_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)
    main_title = ttk.Label(main_frame, style='LightBluePrimaryNavLabel.TLabel', text='Window Designer')
    main_title.pack(padx=5, fill=tk.X)
    main_canvas = tk.Canvas(main_frame, bg=colors.white_primary)
    main_canvas.pack(fill=tk.BOTH, expand=True)
    main_canvas.bind("<Button-1>", unselect_all)

    right_frame = ttk.Frame(root)
    right_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
    properties_title_frame = ttk.Frame(right_frame, style='LightBluePrimaryFrame.TFrame')
    properties_title_frame.pack(fill=tk.X)
    properties_title_label = ttk.Label(properties_title_frame, text='Properties', style='LightBluePrimaryNavLabel.TLabel')
    properties_title_label.pack(fill=tk.X, padx=5)
    #properties_header_hr = ttk.Frame(right_frame, height=2, style='BluePrimaryFrame.TFrame')
    #properties_header_hr.pack(fill=tk.X)
    #properties_label = ttk.Label(right_frame, text='PROPERTIES', style='BluePrimaryLabel.TLabel')
    #properties_label.pack(fill=tk.X, padx=20, pady=0)
    property_frame = ttk.Frame(right_frame)
    property_frame.pack(pady=4, fill=tk.Y)

    properties=["Name", "Y Position", "X Position", "Width", "Height", "Text", "Command"]
    property_entries = {}

    for prop in properties:
        property_entries[prop] = create_property_option(property_frame, prop)
    
    load("play.py")
    
    root.mainloop()


def create_property_option(panel, name):
    """
    helper function for creating the properties panel. creates a label and entry inside a frame.
    returns the created Entry widget
    """
    frame = ttk.Frame(panel)
    frame.pack(fill=tk.X, pady=2)
    label = ttk.Label(frame)
    label["text"] = name
    label.pack(side=tk.LEFT, padx=5)
    border = tk.Frame(frame, background=colors.white_primary) # it's easier to use a frame as a border than to style ttk entries
    border.pack(side=tk.RIGHT, padx=5)
    text = tk.Entry(border, width=20, borderwidth=2, insertwidth=1, relief="flat")
    text.pack(side=tk.RIGHT, padx=2, pady=2)

    text.bind("<FocusIn>", lambda event: set_background(border, colors.lightblue_primary))
    text.bind("<FocusOut>", lambda event: set_background(border, colors.white_primary))
    text.bind("<FocusOut>", lambda event: save_properties(selected_object), add="+")
    text.bind("<Return>", lambda event: save_properties(selected_object))
    
    return text


def load_selectedobj_properties():
    load_properties(selected_object)


def save_selectedobj_properties():
    save_properties(selected_object)


def load_properties(guiobj):
    load_button_properties(guiobj)
    load_movable_properties(guiobj)
    load_sizable_properties(guiobj)
    load_textcontainer_properties(guiobj)
    load_widget_properties(guiobj)
    load_guiobj_properties(guiobj)
    root.focus() # reset text focus. Removes any highlighting


def save_properties(guiobj):
    """
    saves all the properties set in the options panel to the selected widget
    """
    if isinstance(guiobj, GUIObj.Button):
        save_button_properties(guiobj)
    if isinstance(guiobj, GUIObj.MovableWidget):
        save_movable_properties(guiobj)
    if isinstance(guiobj, GUIObj.SizableWidget):
        save_sizable_properties(guiobj)
    if isinstance(guiobj, GUIObj.TextContainer):
        save_textcontainer_properties(guiobj)
    if isinstance(guiobj, GUIObj.Widget):
        save_widget_properties(guiobj)
    if isinstance(guiobj, GUIObj.GUIObj):
        save_guiobj_properties(guiobj)


def save_button_properties(guiobj):
    guiobj.command = property_entries["Command"].get()


def load_button_properties(guiobj):
    if isinstance(guiobj, GUIObj.Button):
        property_entries["Command"].configure(state=tk.NORMAL)
        property_entries["Command"].delete(0, tk.END)
        property_entries["Command"].insert(0, guiobj.command)
    else:
        property_entries["Command"].configure(state=tk.DISABLED)


def save_movable_properties(guiobj):
    x = guiobj.position.x
    y = guiobj.position.y
    try:
        x = int(property_entries["X Position"].get())
    except:
        pass
    try:
        y = int(property_entries["Y Position"].get())
    except:
        pass
    guiobj.position = GUIObj.Vector(x, y)


def load_movable_properties(guiobj):
    if isinstance(guiobj, GUIObj.MovableWidget):
        property_entries["X Position"].configure(state=tk.NORMAL)
        property_entries["Y Position"].configure(state=tk.NORMAL)
        property_entries["X Position"].delete(0, tk.END)
        property_entries["Y Position"].delete(0, tk.END)
        property_entries["X Position"].insert(0, guiobj.position.x)
        property_entries["Y Position"].insert(0, guiobj.position.y)
    else:
        property_entries["X Position"].configure(state=tk.DISABLED)
        property_entries["Y Position"].configure(state=tk.DISABLED)


def save_sizable_properties(guiobj):
    x = guiobj.size.x
    y = guiobj.size.y
    try:
        x = int(property_entries["Width"].get())
    except:
        pass
    try:
        y = int(property_entries["Height"].get())
    except:
        pass
    guiobj.size = GUIObj.Vector(x, y)


def load_sizable_properties(guiobj):
    if isinstance(guiobj, GUIObj.SizableWidget):
        property_entries["Width"].configure(state=tk.NORMAL)
        property_entries["Height"].configure(state=tk.NORMAL)
        property_entries["Width"].delete(0, tk.END)
        property_entries["Height"].delete(0, tk.END)
        property_entries["Width"].insert(0, guiobj.size.x)
        property_entries["Height"].insert(0, guiobj.size.y)
    else:
        property_entries["Width"].configure(state=tk.DISABLED)
        property_entries["Height"].configure(state=tk.DISABLED)


def save_textcontainer_properties(guiobj):
    guiobj.text = property_entries["Text"].get()
    # TODO: save font


def load_textcontainer_properties(guiobj):
    if isinstance(guiobj, GUIObj.TextContainer):
        property_entries["Text"].configure(state=tk.NORMAL)
        property_entries["Text"].delete(0, tk.END)
        property_entries["Text"].insert(0, guiobj.text)
    else:
        property_entries["Text"].configure(state=tk.DISABLED)


def save_widget_properties(guiobj):
    # TODO: add support for setting parent
    pass


def load_widget_properties(guiobj):
    pass


def save_guiobj_properties(guiobj):
    guiobj.name = property_entries["Name"].get()


def load_guiobj_properties(guiobj):
    if isinstance(guiobj, GUIObj.GUIObj):
        property_entries["Name"].configure(state=tk.NORMAL)
        property_entries["Name"].delete(0, tk.END)
        property_entries["Name"].insert(0, guiobj.name)
    else:
        property_entries["Name"].configure(state=tk.DISABLED)


def set_background(widget, color):
    """
    sets the background of a tk widget
    will not work on a ttk widget
    """
    # used primarly to highlight the border frame around an entry widget in the properties panel when presed
    widget["background"] = color
    

def get_guiobj(name):
    """
    returns the guiobj of the given name.
    return None if nothing is found
    """
    # Simple sequential search
    for obj in gui_objects:
        if obj.name == name:
            return obj
    return None


def on_selection(guievent):
    global selected_object
    """
    callback for when a widget is selected

    unselects all other widgets and sets the properties panel to be focused on the current widget
    """
    save_properties(selected_object)
    caller = guievent.caller
    unselect_others(caller)
    selected_object = caller
    load_properties(selected_object)
    if isinstance(caller, GUIObj.MovableWidget):
        caller.bind_event("moved", lambda event: load_movable_properties(caller))
    if isinstance(caller, GUIObj.SizableWidget):
        caller.bind_event("resized", lambda event: load_sizable_properties(caller))


def unselect_others(exluded):
    """
    unselects all guiobjs except for the excluded obj
    """
    global selected_object
    
    for obj in gui_objects:
        if obj is not exluded:
            obj.selected = False
            if obj is selected_object:
                save_properties(obj)
                selected_object = None
                load_properties(None)


def unselect_all(event=None):
    """
    sets the selected state of all guibojs to False
    """
    global selected_object
    
    for obj in gui_objects:
        obj.selected = False
    if selected_object is not None:
        save_properties(selected_object)
        selected_object = None
        load_properties(None)
    
    


def clear():
    """
    resets the window to its initial state
    """
    pass


def load(filename):
    """
    loads the file with the given filename
    """
    clear()
    file = open(filename, "r")
    source = file.read()
    file.close()
    load_initialize(source)


def load_initialize(source):
    """
    loads the guiobjs from the initialization function in the given file
    """
    tree = guiparser.get_tree(source)
    initialize_objects = guiparser.get_objects(tree)
    initialize_function = guiparser.get_initialize(tree)
    for obj in initialize_objects:
        
        # make sense of the returned objects and create them in the canvas
        assignments = guiparser.get_assignments(initialize_function, obj.object_name)
        method_calls = guiparser.get_method_calls(initialize_function, obj.object_name)

        # Tk root loading
        if obj.object_type == "Tk":
            # the Tk type should only be instantiated once and is represented by a window obj
            title = ""
            size = GUIObj.Vector(600, 800)
            # find the parameters for the window
            # almost everything for window is in single argument method calls
            if "title" in method_calls:
                title = method_calls["title"].args[0]
            if "geometry" in method_calls:
                # geometry is given as a string formated as XPOSxYPOS ex: 600x800
                # split it up and turn it into a vector
                x = int(method_calls["geometry"].args[0].split("x")[0])
                y = int(method_calls["geometry"].args[0].split("x")[1])
                size = GUIObj.Vector(x, y)
            new_window = GUIObj.Window(title=title, size=size, name=obj.object_name)
            gui_objects.append(new_window)
        # End Tk root loading

        # Button loading
        elif obj.object_type == "Button":
            parent_name = obj.args[0]
            parent = get_guiobj(parent_name)
            command = ""
            text = ""
            position = GUIObj.Vector(0, 0)
            size = GUIObj.Vector(0, 0)

            # options for a button can be defined in BOTH the constructor and method and assignment calls
            if "command" in obj.keywords:
                command = obj.keywords["command"]
            if "text" in obj.keywords:
                text = obj.keywords["command"]

            for assignment in assignments:
                if isinstance(assignment, guiparser.SubscriptAssignment):
                    if assignment.subscript == "text":
                        text = assignment.value
                    elif assignment.subscript == "command":
                        command = assignment.value

            for method in method_calls.values():
                if method.method_name == "place":
                    if "x" in method.keywords:
                        position.x = int(method.keywords["x"])
                    if "y" in method.keywords:
                        position.y = int(method.keywords["y"])
                    if "width" in method.keywords:
                        size.x = int(method.keywords["width"])
                    if "height" in method.keywords:
                        size.y = int(method.keywords["height"])

            if parent == None:
                print ("Error when loading objects. cannot find parent of %s named %s" %(obj.name, parent_name))

            new_button = GUIObj.TtkButtonImpl(name=obj.object_name, canvas=main_canvas, position=position, size=size, parent=parent, command=command, text=text)
            new_button.bind_event("selected", on_selection)
            gui_objects.append(new_button)
        # End Button loading        

        else:
            print("Error when loading objects. Objects of type %s are not yet supported" % (obj.object_type))
    
    
initialize()

        
