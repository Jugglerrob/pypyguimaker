import tkinter as tk
import tkinter.ttk as ttk
import colors


class Event:
    def __init__(self, caller):
        self.caller = caller


class SelectEvent:
    def __init__(self, caller, multiselect):
        self.caller = caller
        self.multiselect = multiselect


class Vector:
    """Represents a position in 2d space"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "Vector: %f, %f" % (self.x, self.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)


class Sized:
    """Represents an object with a size"""
    def __init__(self, size=Vector(0, 0), **kwargs):
        super().__init__(**kwargs)
        self.size = size


class GUIObj:
    """Represents the most basic gui object"""
    def __init__(self, name="", class_variable=False, **kwargs):
        # What is class_variable? Wether or not it is a global maybe?
        self.name = name
        self.class_variable = class_variable
        self._events = {}

    def bind_event(self, event, action):
        """Binds the action to the event."""
        # This is my way of doing callbacks/bindings/events. I looked up on
        # google for python event and it seems there is not built in event
        # code. So this is a quick and basic way to do it. Store actions for an
        # event as a list in a dict, where the event is the key
        actions = self._events.get(event, [])
        if action not in actions:
            actions += [action]
        self._events[event] = actions


class Container(GUIObj):
    """A gui obj that can contain Widgets"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__children = set()

    def add_child(self, child):
        """Add the given child Widget"""
        self.__children.add(child)

    def remove_child(self, child):
        """Removes the given child widget"""
        self.__children.remove(child)

    def children(self):
        """Returns a list of current children"""
        return list(self.__children)


class Window(Container, Sized):
    """Represents a window on the screen. Is a Container for other widgets"""
    def __init__(self, title="", size=Vector(600, 800), **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.size = size

    @property
    def name(self):
        return "root"
        
    @name.setter
    def name(self, value):
        pass # don't set name.
        # Todo: Make this error so we can see where name setting logic is wrong



class Widget(GUIObj):
    """Represents all tk widgets. Must be a child of a container."""
    def __init__(self, parent=None, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent
        self.parent.add_child(self)


class MovableWidget(Widget):
    """A Widget that has a position"""
    def __init__(self, position=Vector(0, 0), **kwargs):
        super().__init__(**kwargs)
        self.position = position


class SizableWidget(Widget):
    """
    A Widget that has a size
    Must implement resized event
    """
    def __init__(self, size=Vector(0, 0), **kwargs):
        super().__init__(size=size, **kwargs)
        self.size = size


class TkWidgetImpl(Widget):
    def __init__(self, widget=None, parent=None, **kwargs):
        """
        @type widget: tk.Widget
        @type canvas: tk.Canvas
        @type view_id: int

        This is the most basic representation of a TKWidget.

        The canvas property is the canvas that this widget exists on.

        The widget property is the real tk widget that is being used to display
        the widget representation. This may or not be the same type that is
        being represented. For example, a label could be used to display a
        button representation.

        The window property is a canvas that holds everything display related
        to this widget. Anything that needs to be displayed should be placed
        onto this canvas in a canvas window. For example, the real tk widget,
        the outline frame, and the drag handles belong in individual canvas
        windows on this canvas.

        The selected property is true if the widget is currently selected. It
        is initialized to False

        This class also provides makes use of the "selected" and "unselected"
        bindings. You should bind these to show or hide things that should be
        shown or hidden based on active selection.

        This class also binds mouse-1 on the given widget to selected. a.k.a.
        when you click on the real tk widget self.selected = True

        NOTE: Instantiating this class only will leave you with a 0X0 size
        widget. For a widget that can be seen, use TkSizableWidgetImpl.
        """

        super().__init__(parent=parent, **kwargs)
        self.canvas = parent.widget
        self.widget = widget
        self.widget["cursor"] = "arrow"  # makes the cursor always be the arrow
        # the window is a canvas that contains everything related to the widget
        self.window = tk.Canvas()
        # create the selection outline
        # We use a blue frame and make it 4 pixels wider than the window canvas
        self.outline = tk.Frame(bg=colors.lightblue_primary)
        self.__outline_id = self.window.create_window(-2,
                                                      -2,
                                                      window=self.outline,
                                                      anchor=tk.NW,
                                                      width=0,
                                                      height=0,
                                                      state=tk.HIDDEN)
        # place the widget into the window
        # we use the same size as a window canvas
        self.__widget_id = self.window.create_window(0, 0, window=widget,
                                                     width=0, anchor=tk.NW,
                                                     height=0)
        # the view id is used to keep track of everything INCLUDING the window
        # canvas on the main canvas
        self.view_id = self.canvas.create_window(0, 0, window=self.window,
                                                 anchor=tk.NW)
        self._selected = False
        # bind the widget and move it to the front
        self.outline.bind("<Button-1>", self.__select, add="+")
        self.widget.bind("<Button-1>", self.__select, add="+")
        self.widget.bind("<Control-1>", self.__multiselect, add="+")
        # The normal self.widget.lift() method won't work on a canvas :/
        tk.Misc.lift(self.widget)
        # bind the configure method
        self.window.bind("<Configure>", self.__configure, add="+")

    def delete(self):
        """removes this object from the display"""
        self.canvas.delete(self.view_id)

    def __configure(self, event):
        """
        This is called when the main window is changed, for example, resized.
        So we also resize everything inside the canvas
        """
        self.window.itemconfig(self.__outline_id, width=event.width+4)
        self.window.itemconfig(self.__outline_id, height=event.height+4)
        self.window.itemconfig(self.__widget_id, width=event.width)
        self.window.itemconfig(self.__widget_id, height=event.height)

    def __multiselect(self, event):
        self._selected = True
        self.window.itemconfig(self.__outline_id, state=tk.NORMAL)
        if "selected" in self._events:
            for event in self._events["selected"]:
                event(SelectEvent(self, True))

    def __select(self, event):
        self.selected = True

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        # hide or show the outline
        self.window.itemconfig(self.__outline_id,
                               state=tk.NORMAL if value else tk.HIDDEN)
        # callback
        if value and "selected" in self._events:
            for event in self._events["selected"]:
                event(SelectEvent(self, False))
        if not value and "unselected" in self._events:
            for event in self._events["unselected"]:
                event(SelectEvent(self, False))


class TkMovableWidgetImpl(MovableWidget, TkWidgetImpl):
    """
    This class is the movable widget implementation. This implementation should
    be almost completely universal to all widgets.

    This class implements the position property as a Vector

    This class also implements the "moved" event, which calls the bound action
    with a Vector parameter representing the delta moved

    By inheriting from this class <B1-Motion> is bound on the widget to
    implement dragging.
    """
    def __init__(self, position=Vector(0, 0), **kwargs):
        self.__maxpos = Vector(0, 0)
        self.__click_offset = Vector(0, 0)
        self._position = Vector(0, 0)
        super().__init__(**kwargs)
        self.__recalc_maxpos(None, position)  # this also set the position

        self.widget.bind("<B1-Motion>", self.__drag, add="+")
        self.widget.bind("<Button-1>", self.__click, add="+")
        self.outline.bind("<B1-Motion>", self.__drag, add="+")
        self.outline.bind("<Button-1>", self.__click, add="+")
        self.bind_event("resized", self.__recalc_maxpos)
        self.parent.bind_event("resized", self.__recalc_maxpos)

    def __drag(self, event):
        """
        Called from the mouse being dragged across the widget
        """
        # event.x and event.y is the position of the mouse relative to the
        # widget.This is essentially the delta
        new_pos = Vector(0, 0)
        new_pos.x = event.x_root - self.__click_offset.x
        new_pos.y = event.y_root - self.__click_offset.y

        self.position = new_pos

    def __click(self, event):
        """
        Called from the widget being clicked on
        """
        self.__click_offset = Vector(event.x_root - self.position.x,
                                     event.y_root - self.position.y)

    def __recalc_maxpos(self, event=None, position=None):
        """
        Recalculates and fixes the maximum x and y positions.
        Called when the user resizes the widget or parent widget, or durring
        __init__
        """
        max_x = 0
        max_y = 0
        if isinstance(self.parent, Sized):
            max_x = self.parent.size.x - self.size.x
            max_y = self.parent.size.y - self.size.y

        self.__maxpos = Vector(max_x, max_y)
        if position is None:
            new_position = Vector(self.position.x, self.position.y)
            if new_position.x > max_x:
                new_position.x = max_x
            if new_position.y > max_y:
                new_position.y = max_y
            self.position = new_position
            self.position = self.position
        else:
            new_position = Vector(position.x, position.y)
            if new_position.x > max_x:
                new_position.x = max_x
            if new_position.y > max_y:
                new_position.y = max_y
            self.position = new_position

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        # Check to make sure we are not moving outside of bounds
        # This check might not work if the parent does not have a size
        if value.x > self.__maxpos.x:
            value.x = self.__maxpos.x
        if value.y > self.__maxpos.y:
            value.y = self.__maxpos.y
        if value.x < 0:
            value.x = 0
        if value.y < 0:
            value.y = 0

        # calculate the delta and move the view_id by the delta
        delta_x = value.x - self.position.x
        delta_y = value.y - self.position.y

        self.canvas.move(self.view_id, delta_x, delta_y)
        self._position = value
        # callback
        if "moved" in self._events:
            delta = Vector(delta_x, delta_y)
            for event in self._events["moved"]:
                new_event = Event(self)
                new_event.delta = delta
                event(new_event)


class TkSizableWidgetImpl(SizableWidget, TkWidgetImpl, Sized):
    """
    This is the implementation for a sizable widget. This should be almost
    universal to all tk widgets.

    This implements the size property which is a vector.

    This implements the "resized" event which calls with no params

    Inheriting from this class will place a square handle on the corner of the
    widget that can be dragged to resize.
    """
    def __init__(self, **kwargs):
        self._size = self.size
        self.__handle_id = "NONE"
        super().__init__(**kwargs)
        # create a handle as a frame
        handle = tk.Frame(self.canvas.winfo_toplevel(),
                          bg=colors.lightblue_primary)
        handle_fill = tk.Frame(handle, bg="white")
        handle_fill.pack(fill=tk.BOTH, expand=True, pady=2, padx=2)
        # put the handle into a canvas window at the bottom right
        handle_size = 10
        self.__handle_id = self.window.create_window(self.size.x+2,
                                                     self.size.y+2,
                                                     width=handle_size,
                                                     height=handle_size,
                                                     anchor=tk.SE,
                                                     window=handle)
        self.window.itemconfig(self.__handle_id, state=tk.HIDDEN)
        # bind the handle drags
        handle.bind("<B1-Motion>", self.__drag, add="+")
        handle_fill.bind("<B1-Motion>", self.__drag, add="+")
        handle.bind("<Button-1>", self.__click, add="+")
        handle_fill.bind("<Button-1>", self.__click, add="+")
        # bind handle hiding
        self.bind_event("selected", self.__show_handle)
        self.bind_event("unselected", self.__hide_handle)
        # Have the widget update it's size
        # self.size = self.size
        self.__click_offset = Vector(0, 0)

        # callback
        if "resized" in self._events:
            for event in self._events["resized"]:
                new_event = Event(self)
                event(new_event)

    def __show_handle(self, event=None):
        self.window.itemconfig(self.__handle_id, state=tk.NORMAL)

    def __hide_handle(self, event=None):
        self.window.itemconfig(self.__handle_id, state=tk.HIDDEN)

    def __drag(self, event):
        """
        The handle was dragged and this widget needs to be resized by the delta
        """
        new_size = Vector(0, 0)
        new_size.x = event.x_root - self.__click_offset.x
        new_size.y = event.y_root - self.__click_offset.y
        new_size = self._clamp_size(new_size)
        self.size = new_size

    def __click(self, event):
        """
        The handle was clicked. Set up to be dragged
        """
        self.__click_offset = Vector(event.x_root - self.size.x,
                                     event.y_root - self.size.y)

    def _clamp_size(self, size):
        """
        Clamps a vector size so that it does not go out of bounds of the parent
        """
        new_size = Vector(size.x, size.y)
        if isinstance(self, MovableWidget) and isinstance(self.parent, Sized):
            if new_size.x + self.position.x > self.parent.size.x:
                new_size.x = self.parent.size.x - self.position.x
            if new_size.y + self.position.y > self.parent.size.y:
                new_size.y = self.parent.size.y - self.position.y
        return new_size

    @property
    def size(self):
        if hasattr(self, '_size'):
            return self._size
        else:
            return Vector(0, 0)

    @size.setter
    def size(self, value):
        if hasattr(self, '_size'):
            # clamp the size
            if value.y < 10:
                value.y = 10
            if value.x < 10:
                value.x = 10
            # find the delta
            delta = Vector(value.x - self.size.x, value.y - self.size.y)
            # set the size
            self._size = value
            # resize the whole view
            self.canvas.itemconfig(self.view_id, width=self.size.x)
            self.canvas.itemconfig(self.view_id, height=self.size.y)
            # adjust the handle position
            # if hasattr(self, "__handle_id"):
            self.window.move(self.__handle_id, delta.x, delta.y)

            # callback
            if "resized" in self._events:
                for event in self._events["resized"]:
                    new_event = Event(self)
                    event(new_event)
        else:
            self._size = value


class Font:
    """Represents a font family"""
    pass


class TextContainer:
    """Represents a widget that contains text"""
    def __init__(self, text="", font=Font(), **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font = font


class Frame(Container, MovableWidget, SizableWidget):
    """Represents a tk.Frame"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Button(TextContainer, MovableWidget, SizableWidget):
    def __init__(self, command="", **kwargs):
        """
        @type canvas: tk.Canvas
        """
        super().__init__(**kwargs)
        self.command = command


class Label(TextContainer, MovableWidget, SizableWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Canvas(MovableWidget, SizableWidget):
    def __init__(self, bg="white", **kwargs):
        super().__init__(**kwargs)
        self.bg = bg


class Checkbutton(Label):
    def __init__(self, command="", offvalue="", onvalue="", takefocus=True,
                 variable="", size=Vector(90, 20), text="Checkbutton",
                 **kwargs):
        super().__init__(command=command, offvalue=offvalue, onvalue=onvalue,
                         takefocus=takefocus, variable=variable, size=size,
                         text=text, **kwargs)
        self.command = command
        self.offvalue = offvalue
        self.onvalue = onvalue
        self.takefocus = takefocus
        self.variable = variable


class Entry(TextContainer, MovableWidget, SizableWidget):
    def __init__(self, justify="left", show="", validate="",
                 validate_command="", associated_variable="",
                 size=Vector(90, 20), **kwargs):
        super().__init__(size=size, **kwargs)
        self.justify = justify
        # indicates what character to replace with for password fields
        self.show = show
        self.associated_variable = associated_variable
        # when to validate
        # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/entry-validation.html
        self.validate = validate
        self.validate_command = validate_command


class Text(MovableWidget, SizableWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TtkButtonImpl(Button, TkSizableWidgetImpl, TkMovableWidgetImpl):
    def __init__(self, canvas=None, text="Button", size=Vector(50, 40),
                 **kwargs):
        """
        @type canvas: tk.Canvas
        """
        new_button = ttk.Label(canvas.winfo_toplevel(), style="TButton")

        super().__init__(widget=new_button, text=text, size=size,
                         canvas=canvas, **kwargs)

    @property
    def text(self):
        if hasattr(self, '_text'):
            return self._text
        else:
            return ""

    @text.setter
    def text(self, value):
        self._text = value
        self.widget["text"] = self._text


class TtkLabelImpl(Label, TkSizableWidgetImpl, TkMovableWidgetImpl):
    def __init__(self, canvas=None, text="Label", size=Vector(35, 20),
                 **kwargs):
        new_label = ttk.Label(canvas.winfo_toplevel(), style="TLabel")
        super().__init__(widget=new_label, canvas=canvas, size=size, **kwargs)
        self.text = text

    @property
    def text(self):
        if hasattr(self, '_text'):
            return self._text
        else:
            return ""

    @text.setter
    def text(self, value):
        self._text = value
        self.widget["text"] = self._text


class TtkEntryImpl(TkSizableWidgetImpl, TkMovableWidgetImpl, Entry):
    def __init__(self, canvas=None, text="", justify="left", show="",
                 validate="", validate_command="", associated_variable="",
                 **kwargs):
        self._text = text
        self._justify = justify
        self._show = show

        new_entry = ttk.Entry(canvas.winfo_toplevel(),
                              style="EntryStyle.TEntry",
                              state=tk.DISABLED)
        super().__init__(widget=new_entry,
                         text=text,
                         justify=justify,
                         validate=validate,
                         validate_command=validate_command,
                         associated_variable=associated_variable,
                         **kwargs)
        self.text = text
        self.justify = justify
        self.show = show

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.widget["state"] = tk.NORMAL
        self.widget.delete(0, tk.END)
        self.widget.insert(0, value)
        self.widget["state"] = tk.DISABLED

    @property
    def justify(self):
        return self._justify

    @justify.setter
    def justify(self, value):
        self.widget["state"] = tk.ACTIVE
        if value == "right":
            self._justify = "right"
            self.widget["justify"] = "right"
        elif value == "center":
            self._justify = "center"
            self.widget["justify"] = "center"
        else:
            self._justify = "left"
            self.widget["justify"] = "left"
        self.widget["state"] = tk.DISABLED

    @property
    def show(self):
        return self._show

    @show.setter
    def show(self, value):
        self._show = value
        self.widget["show"] = value


class TkTextImpl(TkSizableWidgetImpl, TkMovableWidgetImpl):
    def __init__(self, canvas=None, text="", size=Vector(200, 40), **kwargs):
        self._text = text

        new_entry = tk.Text(canvas.winfo_toplevel(), state=tk.DISABLED)
        super().__init__(widget=new_entry, text=text, size=size, **kwargs)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.widget["state"] = tk.NORMAL
        self.widget.delete(1.0, tk.END)
        self.widget.insert(1.0, value)
        self.widget["state"] = tk.DISABLED


class TtkCheckbuttonImpl(TkSizableWidgetImpl,
                         TkMovableWidgetImpl,
                         Checkbutton):
    def __init__(self, canvas=None, text="Checkbutton", **kwargs):
        self.intvar = tk.IntVar()
        self.intvar.set(0)
        new_checkbutton = ttk.Checkbutton(canvas.winfo_toplevel(),
                                          style="CheckbuttonStyle.Checkbutton",
                                          variable=self.intvar,
                                          offvalue=0,
                                          onvalue=0)
        self._text = text
        super().__init__(text=text, widget=new_checkbutton, canvas=canvas,
                         **kwargs)

    @property
    def text(self):
        if hasattr(self, '_text'):
            return self._text
        else:
            return ""

    @text.setter
    def text(self, value):
        self._text = value
        self.widget["text"] = self._text


class TkCanvasImpl(TkSizableWidgetImpl, TkMovableWidgetImpl, Canvas):
    def __init__(self, canvas=None, bg="White", **kwargs):
        self._bg = bg
        new_canvas = tk.Canvas(canvas.winfo_toplevel(), bg=bg)
        super().__init__(widget=new_canvas, bg=bg, canvas=canvas, **kwargs)

    @property
    def bg(self):
        return self._bg

    @bg.setter
    def bg(self, value):
        self._bg = value
        self.widget.config(bg=self.bg)


class WindowImpl(Window):
    def __init__(self, canvas=None, size=Vector(0, 0), title="window",
                 **kwargs):
        self.position = Vector(0, 0)
        self._title = title
        super().__init__(size=size, title=title, **kwargs)
        self.outline = tk.Frame(canvas, bg=colors.white_secondary)
        self.outline.pack(fill=tk.BOTH)
        self.representation = ttk.Frame(self.outline, style="LightBluePrimaryFrame.TFrame")
        self.representation.pack(fill=tk.BOTH, padx=2, pady=2)
        self.title_label = ttk.Label(self.representation,
                                     text=title,
                                     style="LightBluePrimaryLabel.TLabel",
                                     )
        self.title_label.pack(anchor="nw", side=tk.TOP, padx=5, pady=5)
        self.wrapper = tk.Frame(self.representation)
        self.wrapper.pack()
        self.widget = tk.Canvas(self.wrapper,
                                width=size.x,
                                height=size.y)
        self.widget.pack()
        self.view_id = canvas.create_window(0, 0, window=self.outline,
                                            anchor=tk.NW)
        self.representation.bind("<Button-1>", self.__select, add="+")
        self.title_label.bind("<Button-1>", self.__select, add="+")
        self.widget.bind("<Button-1>", self.__select, add="+")
        self.representation.bind("<Control-1>", self.__select, add="+")
        self.title_label.bind("<Control-1>", self.__select, add="+")
        self.widget.bind("<Control-1>", self.__select, add="+")

    def __select(self, event):
        self.selected = True

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        # hide or show the outline
        if value:
            self.outline.configure(bg=colors.lightblue_secondary)
        else:
            self.outline.configure(bg=colors.white_secondary)
        # callback
        if value and "selected" in self._events:
            for event in self._events["selected"]:
                event(SelectEvent(self, False))
        if not value and "unselected" in self._events:
            for event in self._events["unselected"]:
                event(SelectEvent(self, False))

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        try:
            self.title_label["text"] = value
        except:
            pass

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        try:
            self.widget.configure(height=value.y, width=value.x)
        except:
            pass
