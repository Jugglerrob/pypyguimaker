import GUIObj
import guiparser
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as fonts
import colors

gui_objects = []


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

    properties=["Name", "Y Position", "X Position", "Width", "Height"]
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
    text.bind("<FocusOut>", lambda event: save_properties, add="+")
    text.bind("<Return>", lambda event: save_properties)
    
    return text


def save_properties():
    """
    saves all the properties set in the options panel to the selected widget
    """
    pass


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
    """
    callback for when a widget is selected

    unselects all other widgets and sets the properties panel to be focused on the current widget
    """
    caller = guievent.caller
    unselect_others(caller)


def unselect_others(exluded):
    """
    unselects all guiobjs except for the excluded obj
    """
    for obj in gui_objects:
        if obj is not exluded:
            obj.selected = False


def unselect_all(event=None):
    """
    sets the selected state of all guibojs to False
    """
    for obj in gui_objects:
        obj.selected = False

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
            
        else:
            print("Error when loading objects. Objects of type %s are not yet supported" % (obj.object_type))
        
    
initialize()

        
