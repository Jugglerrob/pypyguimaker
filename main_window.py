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
selected_objects = () # The currently selected gui obj
property_entries = {} # A dict of available property entries {k:name v:(containing panel, entry/associated var)}
root = None # The tk root window
main_canvas = None # The main canvas to put new gui objs on
current_filename = None

updating_drag = False # used for dragging multiple widgets

def initialize():
    global root, main_canvas, property_entries, property_frame, designer_title, code_title, code_editor, widget_counts

    root = tk.Tk()
    root.configure(background=colors.background)
    root.wm_title("PyPyGUIMaker")
    root.pack_propagate(0)
    width = 600
    height = 800
    root.geometry("%dx%d" % (width, height))
    root.state("zoomed") # sets to maximized. Supposably only works on windows and some linux machines

    styles.initialize()
    
    bold = fonts.Font(weight="bold", size=10)

    root_frame = ttk.Frame(root, style='BackgroundFrame.TFrame') # The root frame is just a giant frame used to add extra padding between the window border and elements
    root_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    left_frame_border = ttk.Frame(root_frame, style='WhiteSecondaryFrame.TFrame')
    left_frame_border.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.Y)
    left_frame = ttk.Frame(left_frame_border)
    left_frame.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y)
    widgets_title_frame = ttk.Frame(left_frame, style='LightBluePrimaryFrame.TFrame')
    widgets_title_frame.pack(fill=tk.X)
    widgets_title_label = ttk.Label(widgets_title_frame, text='Widgets', style='LightBluePrimaryNavLabel.TLabel')
    widgets_title_label.pack(fill=tk.X, padx=5)
    widget_frame = ttk.Frame(left_frame, width=150, height=800)
    widget_frame.pack(fill=tk.Y)
    widget_frame.pack_propagate(0)
 
    widgets=(("Button", GUIObj.TtkButtonImpl),
            ("Label", GUIObj.TtkLabelImpl),
            ("Checkbutton", GUIObj.TtkCheckbuttonImpl),
            ("Entry", GUIObj.TtkEntryImpl),
            ("Text", GUIObj.TkTextImpl),
            ("Canvas", GUIObj.TkCanvasImpl)
            )

    # How many widgets have been created. Useful for naming
    widget_counts = {}

    for widget in widgets:
        widget_counts[widget[0]] = 0
        create_widget_entry(widget_frame, widget[0], widget[1])

    main_frame_border = ttk.Frame(root_frame, style='WhiteSecondaryFrame.TFrame')
    main_frame_border.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)
    main_frame = ttk.Frame(main_frame_border, style='LightBluePrimaryFrame.TFrame')
    main_frame.pack(padx=2, pady=2, side=tk.LEFT, fill=tk.BOTH, expand=True)
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

    right_frame_border = ttk.Frame(root_frame, style='WhiteSecondaryFrame.TFrame')
    right_frame_border.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
    right_frame = ttk.Frame(right_frame_border)
    right_frame.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y)
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
                ("Validate Command", "entry"),
                ("Background Color", "entry")
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

    root.bind("<Delete>", lambda event: on_delete_press())

    root.mainloop()


def on_delete_press():
    """called when the delete key is pressed. Determines if the selected widgets are actually to be deleted"""
    for entry in property_entries.values():
        if root.focus_get() is entry[1]:
            return "break"
    delete_selected()


def delete_selected():
    """deletes all currently selected guiobjs"""
    for i in range (len(selected_objects), 0, -1):
        obj = selected_objects[i-1]
        delete(obj)


def delete(guiobj):
    global selected_object
    """removes a guiobj from the program"""
    gui_objects.remove(guiobj)
    guiobj.delete()
    if guiobj in selected_objects:
        selected_objects.remove(guiobj)
    

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


def create_widget_entry(frame, name, widget_type):
    """
    creates an 'entry' in the given panel for the given widget. This entry allows the user to drag an drop a widget onto a canvas
    """
    widget_frame = ttk.Frame(frame)
    widget_frame.pack(side=tk.TOP, fill=tk.X)
    widget_label = ttk.Label(widget_frame, text=name)
    widget_label.pack(side=tk.TOP, padx=5, fill=tk.X)
    widget_label.bind('<Enter>', lambda event: enter_widget_entry(widget_frame, widget_label))
    widget_label.bind('<Leave>', lambda event: leave_widget_entry(widget_frame, widget_label))
    widget_label.bind('<Button-1>', click_new_widget)
    widget_label.bind('<B1-Motion>', drag_new_widget)
    widget_label.bind('<ButtonRelease-1>', lambda event: drop_new_widget(event, name, widget_type))


def enter_widget_entry(frame, label):
    """
    called when the user mouses over a widget entry.
    highlights the entry
    """
    frame.configure(style='LightBluePrimaryFrame.TFrame')
    label.configure(style='LightBluePrimaryLabel.TLabel')


def get_root_position(widget, x, y):
    """gets the position relative to the root widget"""
    while widget.master is not None:
        x += widget.winfo_x()
        y += widget.winfo_y()
        widget = widget.master
    x += widget.winfo_x()
    y += widget.winfo_y()
    return x,y


def leave_widget_entry(frame, label):
    """
    called when the user mouses out over a widget entry.
    un-highlights the entry
    """
    frame.configure(style='TFrame')
    label.configure(style='TLabel')
    

def click_new_widget(event):
    """
    called when the user clicks a widget entry
    sets up the program to drag a new widget
    """
    global new_widget_canvas, canvasx, canvasy, canvaswidth, canvasheight, incanvas
    new_widget_canvas = tk.Canvas(root, highlightthickness=0)
    new_widget_canvas.create_rectangle(0, 0, 9, 9, outline=colors.darkblue_primary, fill=colors.background)
    new_widget_canvas.create_line(0, 0, 9, 9)
    new_widget_canvas.create_line(0, 9, 9, 0)
    rootx, rooty=get_root_position(event.widget, event.x, event.y)
    new_widget_canvas.place(x=rootx, y=rooty, width=10, height=10)

    # These are used later to determine if the are inside the main canvas
    root_GUIObj = get_guiobj("root").widget # this is the canvas of the root guiobj
    canvasx, canvasy = get_root_position(root_GUIObj, root_GUIObj.winfo_x(), root_GUIObj.winfo_y())
    canvaswidth = root_GUIObj.winfo_width()
    canvasheight = root_GUIObj.winfo_height()
    incanvas = False


def drag_new_widget(event):
    """called when the user is dragging a new widget across the screen"""
    global incanvas
    rootx, rooty=get_root_position(event.widget, event.x, event.y)
    if canvasx <= rootx <= canvaswidth + canvasx and canvasy <= rooty <= canvasy + canvasheight:
        if not incanvas:
            new_widget_canvas.create_rectangle(0, 0, 9, 9, outline=colors.darkblue_primary, fill=colors.background)
            incanvas = True
    elif incanvas:
        new_widget_canvas.create_line(0, 0, 9, 9)
        new_widget_canvas.create_line(0, 9, 9, 0)
        incanvas = False
    new_widget_canvas.place(x=rootx, y=rooty)


def drop_new_widget(event, widget_name, widget_type):
    """
    called when the user stops dragging a new widget
    actually creates a new widget
    """
    new_widget_canvas.place_forget()
    if incanvas:
        widget_counts[widget_name] += 1
        name = widget_name + str(widget_counts[widget_name])
        while get_guiobj(name) is not None:
            widget_counts[widget_name] += 1
            name = widget_name + str(widget_counts[widget_name])
        rootx, rooty=get_root_position(event.widget, event.x, event.y)
        root_widget = get_guiobj("root")
        x = rootx - canvasx
        y = rooty - canvasy
        position = GUIObj.Vector(x, y)
        new_widget = widget_type(parent=root_widget, name=name, canvas=root_widget.widget, position=position)
        new_widget.bind_event("selected", on_selection)
        new_widget.bind_event("moved", on_move)
        gui_objects.append(new_widget)


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
    value = property_entries[name][1].get()
    if value == "\032":
        return None
    else:
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


def load_property(name, value, multi):
    """
    shows and sets the property value
    """
    show_property(name)
    if multi:
        multi_properties[name] = multi_properties.get(name, 0) + 1
        old_value = get_property_value(name)
        if old_value != str(value):
            set_property_value(name, "\032")
        else:
            set_property_value(name, value)
    else:
        set_property_value(name, value)


def start_load_properties_multi():
    global multi_properties
    multi_properties = {} # a dict of properties and how many times its been loaded


def finish_load_properties_multi(total_loaded):
    global multi_properties
    for name in multi_properties.keys():
        if multi_properties[name] < total_loaded:
            hide_property(name)
    multi_properties = {}
    

def load_selectedobj_properties():
    pass


def save_selectedobj_properties():
    global updating_drag
    updating_drag = True
    for obj in selected_objects:
        save_properties(obj)
    updating_drag = False


def load_properties(guiobj, multi):
    if not multi:
        hide_all_properties()
        # The ordering of these calls determines the position of the properties
    load_guiobj_properties(guiobj, multi)
    load_widget_properties(guiobj, multi)
    load_movable_properties(guiobj, multi)
    load_sizable_properties(guiobj, multi)
    load_textcontainer_properties(guiobj, multi)
    load_entry_properties(guiobj, multi)
    load_button_properties(guiobj, multi)
    load_checkbutton_properties(guiobj, multi)
    load_text_properties(guiobj, multi)
    load_canvas_properties(guiobj, multi)

    root.focus() # reset text focus. Removes any highlighting


def save_properties(guiobj):
    """
    saves all the properties set in the options panel to the selected widget
    """
    if isinstance(guiobj, GUIObj.Checkbutton):
        save_checkbutton_properties(guiobj)
    if isinstance(guiobj, GUIObj.Text):
        save_text_properties(guiobj)
    if isinstance(guiobj, GUIObj.Entry):
        save_entry_properties(guiobj)
    if isinstance(guiobj, GUIObj.Button):
        save_button_properties(guiobj)
    if isinstance(guiobj, GUIObj.Canvas):
        save_canvas_properties(guiobj)
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
    command = get_property_value("Command")
    offvalue = get_property_value("Off Value")
    onvalue = get_property_value("On Value")
    takefocus = get_property_value("Take Focus")
    variable = get_property_value("Variable")

    if command is not None:
        guiobj.command = command
    if offvalue is not None:
        guiobj.offvalue = offvalue
    if onvalue is not None:
        guiobj.takefocus = onvalue
    if variable is not None:
        guiobj.variable = variable

def load_checkbutton_properties(guiobj, multi):
    if isinstance(guiobj, GUIObj.Checkbutton):
        load_property("Command", guiobj.command, multi)
        load_property("Off Value", guiobj.offvalue, multi)
        load_property("On Value", guiobj.onvalue, multi)
        load_property("Take Focus", guiobj.takefocus, multi)
        load_property("Variable", guiobj.variable, multi)


def save_text_properties(guiobj):
    #  Text doesn't add anything new so we can just pass
    pass


def load_text_properties(guiobj, multi):
    #  Text doesn't add anything new so we can just pass
    pass


def save_canvas_properties(guiobj):
    bg = get_property_value("Background Color")
    if bg is not None:
        guiobj.bg = bg


def load_canvas_properties(guiobj, multi):
    if isinstance(guiobj, GUIObj.Canvas):
        load_property("Background Color", guiobj.bg, multi)


def save_entry_properties(guiobj):
    justify = get_property_value("Justify")
    show = get_property_value("Show")
    associated_variable = get_property_value("Associated Variable")
    validate = get_property_value("Validate")
    validate_command = get_property_value("Validate Command")

    if justify is not None:
        guiobj.justify = justify
    if show is not None:
        guiobj.show = show
    if associated_variable is not None:
        guiobj.associated_variable = associated_variable
    if validate is not None:
        guiobj.validate = validate
    if validate_command is not None:
        guiobj.validate_command = validate_command


def load_entry_properties(guiobj, multi):
    if isinstance(guiobj, GUIObj.Entry):
        load_property("Justify", guiobj.justify, multi)
        load_property("Show", guiobj.show, multi)
        load_property("Associated Variable", guiobj.associated_variable, multi)
        load_property("Validate", guiobj.validate, multi)
        load_property("Validate Command", guiobj.validate, multi)


def save_button_properties(guiobj):
    command = get_property_value("Command")

    if command is not None:
        guiobj.command = command


def load_button_properties(guiobj, multi):
    if isinstance(guiobj, GUIObj.Button):
        load_property("Command", guiobj.command, multi)


def save_movable_properties(guiobj):
    x = guiobj.position.x
    y = guiobj.position.y
    try:
        x = int(get_property_value("X Position"))
    except:
        x = guiobj.position.x
    try:
        y = int(get_property_value("Y Position"))
    except:
        y = guiobj.position.y
    guiobj.position = GUIObj.Vector(x, y)


def load_movable_properties(guiobj, multi):
    if isinstance(guiobj, GUIObj.MovableWidget):
        if not multi and len(selected_objects) > 1:
            load_property("X Position", guiobj.position.x, True)
            load_property("Y Position", guiobj.position.y, True)
        else:
            load_property("X Position", guiobj.position.x, multi)
            load_property("Y Position", guiobj.position.y, multi)


def save_sizable_properties(guiobj):
    x = guiobj.size.x
    y = guiobj.size.y
    try:
        x = int(get_property_value("Width"))
    except:
        x = guiobj.size.x
    try:
        y = int(get_property_value("Height"))
    except:
        y = guiobj.size.y
    guiobj.size = GUIObj.Vector(x, y)


def load_sizable_properties(guiobj, multi):
    if isinstance(guiobj, GUIObj.SizableWidget):
        if not multi and len(selected_objects) > 1:
            load_property("Width", guiobj.size.x, True)
            load_property("Height", guiobj.size.y, True)
        else:
            load_property("Width", guiobj.size.x, multi)
            load_property("Height", guiobj.size.y, multi)


def save_textcontainer_properties(guiobj):
    text = get_property_value("Text")

    if text is not None:
        guiobj.text = text
    # TODO: save font


def load_textcontainer_properties(guiobj, multi):
    if isinstance(guiobj, GUIObj.TextContainer):
        load_property("Text", guiobj.text, multi)


def save_widget_properties(guiobj):
    # TODO: add support for setting parent
    pass


def load_widget_properties(guiobj, multi):
    pass


def save_guiobj_properties(guiobj):
    name = get_property_value("Name") 
    if name is not None:
        guiobj.name = get_property_value("Name")
        

def load_guiobj_properties(guiobj, multi):
    if isinstance(guiobj, GUIObj.GUIObj):
        if not multi:
            load_property("Name", guiobj.name, multi)
        if multi:
            load_property("Name", "\032", multi)
            hide_property("Name")


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


def on_move(guievent):
    """
    callback for when a widget is dragged

    moves all other selected widgets
    """
    global updating_drag
    if not updating_drag:
        updating_drag = True
        for obj in selected_objects:
            if obj is not guievent.caller:
                position = obj.position
                position += guievent.delta
                obj.position = position
        updating_drag = False

def on_selection(guievent):
    global selected_objects
    """
    callback for when a widget is selected

    unselects all other widgets and sets the properties panel to be focused on the current widget
    """
    root.focus() # will remove all entry focus
    for obj in selected_objects:
        save_properties(obj)
    caller = guievent.caller
    if caller not in selected_objects:
        if guievent.multiselect is False:
            unselect_others(caller)
            selected_objects = [caller]
            load_properties(caller, False)
        else:
            selected_objects.append(caller)
            start_load_properties_multi()
            for obj in selected_objects:
                load_properties(obj, True)
            finish_load_properties_multi(len(selected_objects))
        if isinstance(caller, GUIObj.MovableWidget):
            caller.bind_event("moved", lambda event: load_movable_properties(caller, False))
        if isinstance(caller, GUIObj.SizableWidget):
            caller.bind_event("resized", lambda event: load_sizable_properties(caller, False))


def unselect_others(exluded):
    """
    unselects all guiobjs except for the excluded obj
    """
    global selected_objects
    
    for obj in gui_objects:
        if obj is not exluded:
            obj.selected = False
            if obj in selected_objects:
                save_properties(obj)
    selected_objects = [exluded]


def unselect_all(event=None):
    """
    sets the selected state of all guibojs to False
    """
    global selected_objects
    
    for obj in gui_objects:
        obj.selected = False
    for obj in selected_objects:
        save_properties(obj)
    selected_objects = []


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
    global current_filename
    clear()
    file = open(filename, "r")
    source = file.read()
    file.close()
    load_code(source)
    load_initialize(source)
    current_filename = file.name
    root.wm_title("PyPyGUIMaker: %s" % (current_filename))


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
        elif obj.object_type == "Text":
            load_text(obj, assignments, method_calls)
        elif obj.object_type == "Canvas":
            load_canvas(obj, assignments, method_calls)
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
    new_button.bind_event("moved", on_move)
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
    new_label.bind_event("moved", on_move)
    gui_objects.append(new_label)


def load_text(obj, assignments, method_calls):
    """
    loads text code into a guiobj
    """
    parent_name = obj.args[0]
    parent = get_guiobj(parent_name)
    position = GUIObj.Vector(0, 0)
    size = GUIObj.Vector(0, 0)

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

    new_text = GUIObj.TkTextImpl(name=obj.object_name, canvas=parent.widget, position=position, size=size, parent=parent)
    new_text.bind_event("selected", on_selection)
    new_text.bind_event("moved", on_move)
    gui_objects.append(new_text)


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
    new_entry.bind_event("moved", on_move)
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
    new_checkbutton.bind_event("moved", on_move)
    gui_objects.append(new_checkbutton)


def load_canvas(obj, assignments, method_calls):
    """
    loads canvas into a guiobj
    """
    parent_name = obj.args[0]
    parent = get_guiobj(parent_name)
    bg = ""
    position = GUIObj.Vector(0, 0)
    size = GUIObj.Vector(0, 0)

    if "bg" in obj.keywords:
        bg = obj.keywords["bg"]

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
        if method.method_name in ["config", "configure"]:
            if "bg" in method.keywords:
                bg = method.keywords["bg"]

    new_canvas = GUIObj.TkCanvasImpl(name=obj.object_name, canvas=parent.widget, position=position, size=size, parent=parent, bg=bg)
    new_canvas.bind_event("selected", on_selection)
    new_canvas.bind_event("moved", on_move)
    gui_objects.append(new_canvas)
            

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
        root.wm_title("PyPyGUIMaker: %s" % (current_filename))
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
        elif isinstance(obj, GUIObj.TkTextImpl):
            src += text_to_src(obj)
        elif isinstance(obj, GUIObj.TtkButtonImpl):
            src += button_to_src(obj)
        elif isinstance(obj, GUIObj.TtkEntryImpl):
            src += entry_to_src(obj, associated_vars)
        elif isinstance(obj, GUIObj.TtkCheckbuttonImpl):
            src += checkbutton_to_src(obj, associated_vars)
        elif isinstance(obj, GUIObj.WindowImpl):
            root_src, mainloop = root_to_src(obj)
            src += root_src
        elif isinstance(obj, GUIObj.TkCanvasImpl):
            src += canvas_to_src(obj, associated_vars)
    src += mainloop
    # indent all the widget code
    lines = src.splitlines()
    src = ""
    for line in lines:
        src += (" " * 4) + line + "\n"
    _globals = "\n    global "
    for obj in gui_objects:
        _globals += obj.name + ", "
    _globals = _globals[0:-2] + "\n"
    # add user code
    src = code_editor["text"] + "def initialize():" + _globals + src + "initialize()\n"
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


def text_to_src(text):
    """
    returns the string of the generated src for the text
    """
    name = text.name
    posx = str(text.position.x)
    posy = str(text.position.y)
    sizex = str(text.size.x)
    sizey = str(text.size.y)
    parent = text.parent.name
    src = ""
    src += '%(name)s = Text(%(parent)s)\n' % locals()
    src += "%(name)s.place(x=%(posx)s, y=%(posy)s, width=%(sizex)s, height=%(sizey)s)\n\n" % locals()
    return src


def canvas_to_src(canvas, associated_vars):
    """
    returns the string of the generated src for the entry.
    associated_vars in a list of already generated associated variables
    """
    name = canvas.name
    posx = str(canvas.position.x)
    posy = str(canvas.position.y)
    sizex = str(canvas.size.x)
    sizey = str(canvas.size.y)
    parent = canvas.parent.name
    bg = canvas.bg
    src = ""
    src += '%(name)s = Canvas(%(parent)s, bg="%(bg)s")\n' % locals()
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

        
