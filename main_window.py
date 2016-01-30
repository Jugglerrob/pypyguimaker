import GUIObj
import guiparser
import tkinter as tk
import tkinter.ttk as ttk
import colors

gui_objects = []

def initialize():
    global root, main_canvas
    root = tk.Tk()
    root.configure(background=colors.background)
    main_canvas = tk.Canvas(root, bg=colors.white_primary)
    main_canvas.pack(padx=5, pady=5)
    main_canvas.bind("<Button-1>", unselect_all)

    load("play.py")
    
    root.mainloop()


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

        
