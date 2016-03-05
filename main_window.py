import GUIObj
import guiparser
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as fonts
import tkinter.filedialog
import colors
import code_editor as editor
import styles

gui_objects = [] # all gui objs in the designer
selected_object = None # The currently selected gui obj
property_entries = {} # A dict of available property entries {k:name v:(containing panel, entry/associated var)}
root = None # The tk root window
main_canvas = None # The main canvas to put new gui objs on
current_filename = None


def initialize():
    global root, main_canvas, property_entries, property_frame, designer_title, code_title, code_editor

    root = tk.Tk()
    root.configure(background=colors.background)
    root.pack_propagate(0)
    width = 600
    height = 800
    root.geometry("%dx%d" % (width, height))
    root.state("zoomed") # sets to maximized. Supposably only works on windows and some linux machines

    styles.initialize()
    
    bold = fonts.Font(weight="bold", size=10)

    root_frame = ttk.Frame(root, style='BackgroundFrame.TFrame') # The root frame is just a giant frame used to add extra padding between the window border and elements
    root_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    main_frame = ttk.Frame(root_frame, style='LightBluePrimaryFrame.TFrame')
    main_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)
    nav_frame = ttk.Frame(main_frame, style='LightBluePrimaryFrame.TFrame')
    nav_frame.pack(side=tk.TOP, fill=tk.X)
    tk.Grid.columnconfigure(nav_frame, 1, weight=1)
    designer_title = ttk.Label(nav_frame, style='LightBluePrimaryNavLabel.TLabel', text='Window Designer')
    designer_title.grid(row=0, column=0, sticky="EW", ipadx=4)
    designer_title.bind("<Button-1>", show_designer)
    code_title = ttk.Label(nav_frame, style='WhiteDisabledNavLabel.TLabel', text='Code Editor')
    code_title.grid(row=0, column=1, sticky="EW", ipadx=4)
    code_title.bind("<Button-1>", show_code)
    main_canvas = tk.Canvas(main_frame, bg=colors.white_secondary, highlightthickness=0)
    main_canvas.pack(fill=tk.BOTH, expand=True)
    main_canvas.bind("<Button-1>", unselect_all)
    code_editor = editor.CodeEditor(main_frame)

    right_frame = ttk.Frame(root_frame)
    right_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
    properties_title_frame = ttk.Frame(right_frame, style='LightBluePrimaryFrame.TFrame')
    properties_title_frame.pack(fill=tk.X)
    properties_title_label = ttk.Label(properties_title_frame, text='Properties', style='LightBluePrimaryNavLabel.TLabel')
    properties_title_label.pack(fill=tk.X, padx=5)
    #properties_header_hr = ttk.Frame(right_frame, height=2, style='BluePrimaryFrame.TFrame')
    #properties_header_hr.pack(fill=tk.X)
    #properties_label = ttk.Label(right_frame, text='PROPERTIES', style='BluePrimaryLabel.TLabel')
    #properties_label.pack(fill=tk.X, padx=20, pady=0)
    property_frame = ttk.Frame(right_frame, width=300, height=800)
    property_frame.pack(pady=4, fill=tk.Y)
    property_frame.pack_propagate(0) # prevents the frame from resizing

    # This specifies what properties to place in the properties panel
    #((Property name, property type, (objects to display for), (options))
    properties=(("Name", "entry"),
                ("X Position", "entry"),
                ("Y Position", "entry"),
                ("Width", "entry"),
                ("Height", "entry"),
                ("Text", "entry"),
                ("Command", "entry"),
                ("Justify", "option", ("left", "center", "right")),
                ("Show", "entry"),
                ("Associated Variable", "entry"),
                ("Validate", "option", ("focus", "focusin", "focusout", "key", "all", "none")),
                ("Validate Command", "entry"),
                ("On Value", "entry"),
                ("Off Value", "entry"),
                ("Take Focus", "entry"),
                ("Variable", "entry"),
                ("Validate Command", "entry")
                )
    
    property_entries = {}
    for prop in properties:
        property_entries[prop[0]] = create_property_option(property_frame, prop)

    filemenu = tk.Menu(root, tearoff=0)
    filemenu.add_command(label="Load...", command=load_prompt)
    filemenu.add_command(label="Save", command=save)
    filemenu.add_command(label="Save As", command=save_as)

    menubar = tk.Menu(root)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)
    
    load("test_gui.py")

    root.mainloop()


def show_code(event=None):
    main_canvas.pack_forget()
    code_editor.pack(fill=tk.BOTH, expand=True)
    code_editor._modified() # redraw and recolor
    code_title.configure(style='LightBluePrimaryNavLabel.TLabel')
    designer_title.configure(style='WhiteDisabledNavLabel.TLabel')


def show_designer(event=None):
    code_editor.pack_forget()
    main_canvas.pack(fill=tk.BOTH, expand=True)
    designer_title.configure(style='LightBluePrimaryNavLabel.TLabel')
    code_title.configure(style='WhiteDisabledNavLabel.TLabel')


def create_property_option(panel, options):
    """
    helper function for creating the properties panel. creates a label and entry inside a frame.
    returns the created Entry widget
    """
    name = options[0]
    input_type = options[1]
    
    frame = ttk.Frame(panel)
    #frame.pack(fill=tk.X, pady=2)
    label = ttk.Label(frame)
    label["text"] = name
    label.pack(side=tk.LEFT, padx=5)

    if input_type == "entry":
        border = tk.Frame(frame, background=colors.white_primary) # it's easier to use a frame as a border than to style ttk entries
        border.pack(side=tk.RIGHT, padx=5)
        text = tk.Entry(border, width=20, borderwidth=2, insertwidth=1, relief="flat", disabledbackground=colors.white_disabled)
        text.pack(side=tk.RIGHT, padx=2, pady=2)

        text.bind("<FocusIn>", lambda event: set_background(border, colors.lightblue_primary))
        text.bind("<FocusOut>", lambda event: set_background(border, colors.white_primary))
        text.bind("<FocusOut>", lambda event: save_selectedobj_properties(), add="+")
        text.bind("<Return>", lambda event: save_selectedobj_properties())
    
        return (frame, text)

    elif input_type == "option":
        value = tk.StringVar()
        option = ttk.OptionMenu(frame, value, options[2][0], *options[2])
        option.pack(side=tk.RIGHT, padx=5)
        value.set("")

        option.bind("<FocusOut>", lambda event: save_selectedobj_properties(), add="+")
        value.trace("w", lambda *args: save_selectedobj_properties())
        
        return (frame, value)

def hide_all_properties():
    """
    hides all properties
    """
    for name in property_entries.keys():
        hide_property(name)


def get_property_value(name):
    """
    returns the set value of the property entry given the name
    """
    return property_entries[name][1].get()


def set_property_value(name, value):
    """
    sets the value of the property entry given the name.
    """
    if isinstance(property_entries[name][1], tk.Entry): # This is a common entry
        property_entries[name][1].delete(0, tk.END)
        property_entries[name][1].insert(0, value);
    else: # otherwise we are setting the property of an associated variable
        property_entries[name][1].set(value)


def show_property(name):
    """
    shows the given property entry and label
    """
    property_entries[name][0].pack(fill=tk.X, pady=2)


def hide_property(name):
    """
    hides the given property entry and label
    """
    property_entries[name][0].pack_forget()


def load_property(name, value):
    """
    shows and sets the property value
    """
    show_property(name)
    set_property_value(name, value)


def load_selectedobj_properties():
    load_properties(selected_object)


def save_selectedobj_properties():
    save_properties(selected_object)


def load_properties(guiobj):
    hide_all_properties()
    # The ordering of these calls determines the position of the properties
    load_guiobj_properties(guiobj)
    load_widget_properties(guiobj)
    load_movable_properties(guiobj)
    load_sizable_properties(guiobj)
    load_textcontainer_properties(guiobj)
    load_entry_properties(guiobj)
    load_button_properties(guiobj)
    load_checkbutton_properties(guiobj)

    root.focus() # reset text focus. Removes any highlighting


def save_properties(guiobj):
    """
    saves all the properties set in the options panel to the selected widget
    """
    if isinstance(guiobj, GUIObj.Checkbutton):
        save_checkbutton_properties(guiobj)
    if isinstance(guiobj, GUIObj.Entry):
        save_entry_properties(guiobj)
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


def save_checkbutton_properties(guiobj):
    guiobj.command = get_property_value("Command")
    guiobj.offvalue = get_property_value("Off Value")
    guiobj.onvalue = get_property_value("On Value")
    guiobj.takefocus = get_property_value("Take Focus")
    guiobj.variable = get_property_value("Variable")


def load_checkbutton_properties(guiobj):
    if isinstance(guiobj, GUIObj.Checkbutton):
        load_property("Command", guiobj.command)
        load_property("Off Value", guiobj.offvalue)
        load_property("On Value", guiobj.onvalue)
        load_property("Take Focus", guiobj.takefocus)
        load_property("Variable", guiobj.variable)


def save_entry_properties(guiobj):
    guiobj.justify = get_property_value("Justify")
    guiobj.show = get_property_value("Show")
    guiobj.associated_variable = get_property_value("Associated Variable")
    guiobj.validate = get_property_value("Validate")
    guiobj.validate_command = get_property_value("Validate Command")


def load_entry_properties(guiobj):
    if isinstance(guiobj, GUIObj.Entry):
        load_property("Justify", guiobj.justify)
        load_property("Show", guiobj.show)
        load_property("Associated Variable", guiobj.associated_variable)
        load_property("Validate", guiobj.validate)
        load_property("Validate Command", guiobj.validate)


def save_button_properties(guiobj):
    guiobj.command = get_property_value("Command")


def load_button_properties(guiobj):
    if isinstance(guiobj, GUIObj.Button):
        load_property("Command", guiobj.command)


def save_movable_properties(guiobj):
    x = guiobj.position.x
    y = guiobj.position.y
    try:
        x = int(get_property_value("X Position"))
    except:
        pass
    try:
        y = int(get_property_value("Y Position"))
    except:
        pass
    guiobj.position = GUIObj.Vector(x, y)


def load_movable_properties(guiobj):
    if isinstance(guiobj, GUIObj.MovableWidget):
        load_property("X Position", guiobj.position.x)
        load_property("Y Position", guiobj.position.y)


def save_sizable_properties(guiobj):
    x = guiobj.size.x
    y = guiobj.size.y
    try:
        x = int(get_property_value("Width"))
    except:
        pass
    try:
        y = int(get_property_value("Height"))
    except:
        pass
    guiobj.size = GUIObj.Vector(x, y)


def load_sizable_properties(guiobj):
    if isinstance(guiobj, GUIObj.SizableWidget):
        load_property("Width", guiobj.size.x)
        load_property("Height", guiobj.size.y)


def save_textcontainer_properties(guiobj):
    guiobj.text = get_property_value("Text")
    # TODO: save font


def load_textcontainer_properties(guiobj):
    if isinstance(guiobj, GUIObj.TextContainer):
        load_property("Text", guiobj.text)


def save_widget_properties(guiobj):
    # TODO: add support for setting parent
    pass


def load_widget_properties(guiobj):
    pass


def save_guiobj_properties(guiobj):
    guiobj.name = get_property_value("Name")


def load_guiobj_properties(guiobj):
    if isinstance(guiobj, GUIObj.GUIObj):
        load_property("Name", guiobj.name)


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


def clear():
    global gui_objects
    """
    resets the window to its initial state
    """
    unselect_all()
    gui_objects = []
    main_canvas.delete("all")


def load_prompt():
    """
    prompt the user for a file to load
    """
    try:
        filename = tkinter.filedialog.askopenfilename(filetypes=[('Py file','*.py'), ('All files','*.*')])
        if filename != '':
            load(filename)
    except Exception as e:
        print("error when opening and loading file")
        print(e)


def load(filename):
    """
    loads the file with the given filename
    """
    clear()
    file = open(filename, "r")
    source = file.read()
    file.close()
    load_code(source)
    load_initialize(source)


def load_code(source):
    src = [] # lines of source code
    # This state machine loads every line into src besides "initialize()" and everything inside "def initialize()"
    state = "NORMAL"
    indent_level = 0
    for line in source.splitlines():
        if state == "NORMAL":
            if line.strip(' ') == 'def initialize():':
                state = "INITIALIZE_START"
                continue
            if line == "initialize()":
                continue
            else:
                src.append(line)
        elif state == "INITIALIZE_START":
            state = "INITIALIZE"
            indent_level = len(line) - len(line.lstrip(' '))
            continue
        elif state == "INITIALIZE":
            if line.lstrip(' ').startswith('#'):
                continue
            elif len(line.lstrip(' ')) == 0:
                continue
            elif len(line) - len(line.lstrip(' ')) < indent_level:
                state = "NORMAL"
                src.append(line)
                continue
            else:
                continue
    code_editor["text"] = "\n".join(src)
    code_editor.updateLineNumbers()
                

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
            load_root(obj, assignments, method_calls)
        elif obj.object_type == "Button":
            load_button(obj, assignments, method_calls)
        elif obj.object_type == "Label":
            load_label(obj, assignments, method_calls)
        elif obj.object_type == "Entry":
            load_entry(obj, assignments, method_calls)
        elif obj.object_type == "Checkbutton":
            load_checkbutton(obj, assignments, method_calls)
        else:
            print("Error when loading objects. Objects of type %s are not yet supported" % (obj.object_type))


def load_root(obj, assignments, method_calls):
    """
    loads the root object code into guiobjs
    """
    # the Tk type should only be instantiated once and is represented by a window obj
    title = ""
    size = GUIObj.Vector(800, 600)
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
    new_window = GUIObj.WindowImpl(canvas=main_canvas, title=title, size=size, name=obj.object_name)
    gui_objects.append(new_window)


def load_button(obj, assignments, method_calls):
    """
    loads button code into a guiobj
    """
    parent_name = obj.args[0]
    parent = get_guiobj(parent_name)
    command = ""
    text = ""
    position = GUIObj.Vector(0, 0)
    size = GUIObj.Vector(0, 0)

    if "command" in obj.keywords:
        command = obj.keywords["command"]
    if "text" in obj.keywords:
        text = obj.keywords["text"]

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

    new_button = GUIObj.TtkButtonImpl(name=obj.object_name, canvas=parent.widget, position=position, size=size, parent=parent, command=command, text=text)
    new_button.bind_event("selected", on_selection)
    gui_objects.append(new_button)


def load_label(obj, assignments, method_calls):
    """
    loads label code into a guiobj
    """
    parent_name = obj.args[0]
    parent = get_guiobj(parent_name)
    text = ""
    position = GUIObj.Vector(0, 0)
    size = GUIObj.Vector(0, 0)

    if "text" in obj.keywords:
        text = obj.keywords["text"]        

    for assignment in assignments:
        if isinstance(assignment, guiparser.SubscriptAssignment):
            if assignment.subscript == "text":
                text = assignment.value

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

    new_label = GUIObj.TtkLabelImpl(name=obj.object_name, canvas=parent.widget, position=position, size=size, parent=parent, text=text)
    new_label.bind_event("selected", on_selection)
    gui_objects.append(new_label)


def load_entry(obj, assignment, method_calls):
    """
    loads entry code into a guiobj
    """
    parent_name = obj.args[0]
    parent = get_guiobj(parent_name)
    text = ""
    position = GUIObj.Vector(0, 0)
    size = GUIObj.Vector(0, 0)
    justify = "left"
    show = ""
    associated_variable = ""
    validate = ""
    validate_command = ""

    for word in obj.keywords:
        if word == "text":
            text = obj.keywords["text"]
        elif word == "justify":
            justify = obj.keywords["justify"]
            if justify == "tk.LEFT":
                justify = "left"
            elif justify == "tk.RIGHT":
                justify = "right"
            elif justify == "tk.CENTER":
                justify = "center"
        elif word == "show":
            show = obj.keywords["show"]
        elif word == "textvariable":
            associated_variable = obj.keywords["textvariable"]
        elif word == "validate":
            validate = obj.keywords["validate"]
        elif word == "validatecommand":
            validate_command = obj.keywords["validatecommand"]

    #for assignment in assignments:
    #    if isinstance(assignment, guiparser.SubscriptAssignment):
    #        if assignment.subscript == "text":
    #            text = assignment.value

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
        if method.method_name == "insert":
            if method.args[0] == 0: # assure that we're inserting at the very start
                text = method.args[1]
            else:
                println("Cannot insert text at any place other than 0")

    new_entry = GUIObj.TtkEntryImpl(name=obj.object_name,
                                    canvas=parent.widget,
                                    position=position,
                                    size=size,
                                    parent=parent,
                                    text=text,
                                    justify=justify,
                                    show=show,
                                    associated_variable=associated_variable,
                                    validate=validate,
                                    validatecommand=validate_command)
    new_entry.bind_event("selected", on_selection)
    gui_objects.append(new_entry)


def load_checkbutton(obj, assignments, method_calls):
    """
    loads checkbutton into a guiobj
    """
    parent_name = obj.args[0]
    parent = get_guiobj(parent_name)
    text = ""
    position = GUIObj.Vector(0, 0)
    size = GUIObj.Vector(0, 0)

    if "text" in obj.keywords:
        text = obj.keywords["text"]

    for assignment in assignments:
        if isinstance(assignment, guiparser.SubscriptAssignment):
            if assignment.subscript == "text":
                text = assignment.value

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

    new_checkbutton = GUIObj.TtkCheckbuttonImpl(name=obj.object_name, canvas=parent.widget, position=position, size=size, parent=parent, text=text)
    new_checkbutton.bind_event("selected", on_selection)
    gui_objects.append(new_checkbutton)
            

def save():
    """called when the user clicks 'save'"""
    if current_filename is not None:
        save_gui(current_filename)
    else:
        save_as()


def save_as():
    """called when the user clicks 'save as'"""
    global current_filename
    try:
        filename = tk.filedialog.asksaveasfilename(defaultextension='.py',
                                                   filetypes=[('python files', '.py'), ('all files', '.*')])
        save_gui(filename) # temp test code
        current_filename = filename        
    except:
        pass # this will be called when the user exits or cancels the file dialog


def save_gui(filename):
    src = gui_to_src()
    with open(filename, 'w') as file:
        file.write(src)
        

def gui_to_src():
    src = ""
    associated_vars = []
    mainloop = ""
    # get the widget creation code
    for obj in gui_objects:
        if isinstance(obj, GUIObj.TtkLabelImpl):
            src += label_to_src(obj)
        elif isinstance(obj, GUIObj.TtkButtonImpl):
            src += button_to_src(obj)
        elif isinstance(obj, GUIObj.TtkEntryImpl):
            src += entry_to_src(obj, associated_vars)
        elif isinstance(obj, GUIObj.TtkCheckbuttonImpl):
            src += checkbutton_to_src(obj, associated_vars)
        elif isinstance(obj, GUIObj.WindowImpl):
            root_src, mainloop = root_to_src(obj)
            src += root_src
    src += mainloop
    # indent all the widget code
    lines = src.splitlines()
    src = ""
    for line in lines:
        src += (" " * 4) + line + "\n"
    # add user code
    src = code_editor["text"] + "def initialize():" + src + "initialize()\n"
    return src


def label_to_src(label):
    """returns a string of the generated src for the label"""
    name = label.name
    posx = str(label.position.x)
    posy = str(label.position.y)
    sizex = str(label.size.x)
    sizey = str(label.size.y)
    text = label.text
    parent = label.parent.name

    src = """%(name)s = Label(%(parent)s)
%(name)s["text"] = "%(text)s"
%(name)s.place(x=%(posx)s, y=%(posy)s, width=%(sizex)s, height=%(sizey)s)\n\n""" % locals()
    return src


def button_to_src(button):
    """returns a string of the generated src for the button"""
    name = button.name
    posx = str(button.position.x)
    posy = str(button.position.y)
    sizex = str(button.size.x)
    sizey = str(button.size.y)
    text = button.text
    parent = button.parent.name
    command = button.command

    src = ""
    if command:
        src += "%(name)s = Button(%(parent)s, command=%(command)s)\n" % locals()
    else:
        src += "%(name)s = Button(%(parent)s)\n" % locals()
    src += '%(name)s["text"] = "%(text)s"\n' % locals()
    src += '%(name)s.place(x=%(posx)s, y=%(posy)s, width=%(sizex)s, height=%(sizey)s)\n\n' % locals()
    return src


def entry_to_src(entry, associated_vars):
    """
    returns a string of the generated src for the entry.
    associated_vars is a list of already generated associated variables
    """
    name = entry.name
    posx = str(entry.position.x)
    posy = str(entry.position.y)
    sizex = str(entry.size.x)
    sizey = str(entry.size.y)
    text = entry.text
    parent = entry.parent.name
    justify = entry.justify
    show = entry.show
    associated_variable = entry.associated_variable
    validate = entry.validate
    validate_command = entry.validate_command
    src = ""

    if associated_variable and associated_variable not in associated_vars:
        src += "%(associated_variable)s = StringVar()\n\n" % locals()
        associated_vars.append(associated_variable)
    src += """%(name)s = Entry(%(parent)s)
%(name)s.insert(0, "%(text)s")\n""" % locals()
    if associated_variable:
        src += '%(name)s["textvariable"] = %(associated_variable)s\n' % locals()
    if justify:
        src += '%(name)s["justify"] = "%(justify)s"\n' % locals()
    if show:
        src += '%(name)s["show"] = "%(show)s"\n' % locals()
    if validate:
        src += '%(name)s["validate"] = "%(validate)s"\n' % locals()
    if validate_command:
        src += '%(name)s["validatecommand"] = %(validate_command)s\n' % locals()
    src += "%(name)s.place(x=%(posx)s, y=%(posy)s, width=%(sizex)s, height=%(sizey)s)\n\n" % locals()
    return src


def checkbutton_to_src(checkbutton, associated_vars):
    """
    returns the string of the generated src for the entry.
    associated_vars in a list of already generated associated variables
    """
    name = checkbutton.name
    posx = str(checkbutton.position.x)
    posy = str(checkbutton.position.y)
    sizex = str(checkbutton.size.x)
    sizey = str(checkbutton.size.y)
    text = checkbutton.text
    parent = checkbutton.parent.name
    command = checkbutton.command
    offvalue = checkbutton.offvalue
    onvalue = checkbutton.onvalue
    takefocus = checkbutton.takefocus
    variable = checkbutton.variable
    isnumeric = onvalue.isnumeric() and offvalue.isnumeric() # to know if we should use StringVar or IntVar
    src = ""
    
    if variable and variable not in associated_vars:
        if isnumeric:
            src += "%(variable)s = IntVar()\n" % locals()
        else:
            src += "%(variable)s = StringVar()\n" % locals()
        associated_vars.append(variable)
    if command:
        src += '%(name)s = Checkbutton(%(parent)s, command=%(command)s)\n' % locals()
    else:
        src += '%(name)s = Checkbutton(%(parent)s)\n' % locals()        
    src += '%(name)s["text"] = "%(text)s"\n' % locals()
    if variable:
        src += '%(name)s["variable"] = %(variable)s\n' % locals()
    if onvalue:
        if isnumeric:
            src += '%(name)s["onvalue"] = %(onvalue)s\n' % locals()
        else:
            src += '%(name)s["onvalue"] = "%(onvalue)s"\n' % locals()
    if offvalue:
        if isnumeric:
            src += '%(name)s["offvalue"] = %(offvalue)s\n' % locals()
        else:
            src += '%(name)s["offvalue"] = "%(offvalue)s"\n' % locals()
    if takefocus:
        src += '%(name)s["takefocus"] = %(takefocus)s\n' % locals()
    src += "%(name)s.place(x=%(posx)s, y=%(posy)s, width=%(sizex)s, height=%(sizey)s)\n\n" % locals()
    return src


def root_to_src(_root):
    """
    returns a tuple
    tuple[0] is src to create window
    tuple[1] is src to start mainloop
    the mainloop src should be added after all other widgets are added to src
    """
    name = _root.name
    title = _root.title
    sizex = str(_root.size.x)
    sizey = str(_root.size.y)
    geometry = sizex + "x" + sizey

    src = """
%(name)s = Tk()
%(name)s.title("%(title)s")
%(name)s.geometry("%(geometry)s")\n\n""" % locals()
    mainloop = "%(name)s.mainloop()" % locals()
    return src, mainloop

            
initialize()

        
