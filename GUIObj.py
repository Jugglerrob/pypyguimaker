__author__ = 'robert'

import tkinter as tk
import tkinter.ttk as ttk
import colors

class Event:
    def __init__(self, caller):
        self.caller = caller


class Vector:
    """Represents a position in 2d space"""
    def __init__(self, x, y):
        self.x = x
        self.y = y


    def __str__(self):
        return "Vector: %f, %f" % (self.x, self.y)


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
        # This is my way of doing callbacks/bindings/events. I looked up on google for python event and it seems there
        # is not built in event code. So this is a quick and basic way to do it. Store actions for an event as a list
        # in a dict, where the event is the key
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

        The widget property is the real tk widget that is being used to display the widget representation. This may or
        not be the same type that is being represented. For example, a label could be used to display a button
        representation.

        The window property is a canvas that holds everything display related to this widget. Anything that needs to be
        displayed should be placed onto this canvas in a canvas window. For example, the real tk widget, the outline
        frame, and the drag handles belong in individual canvas windows on this canvas.

        The selected property is true if the widget is currently selected. It is initialized to False

        This class also provides makes use of the "selected" and "unselected" bindings. You should bind these to show
        or hide things that should be shown or hidden based on active selection.

        This class also binds mouse-1 on the given widget to selected. a.k.a. when you click on the real tk widget
        self.selected = True

        NOTE: Instantiating this class only will leave you with a 0X0 size widget. For a widget that can be seen,
              use TkSizableWidgetImpl.
        """

        super().__init__(parent=parent, **kwargs)
        self.canvas = parent.widget
        self.widget = widget
        self.window = tk.Canvas()  # the window is a canvas that contains everything related to the widget
        # create the selection outline
        # We use a blue frame and make it 4 pixels wider than the window canvas
        self.__outline_id = self.window.create_window(-2, -2, window=tk.Frame(bg=colors.lightblue_primary),
                                                      anchor=tk.NW,
                                                      width=0,
                                                      height=0,
                                                      state=tk.HIDDEN)
        # place the widget into the window
        # we use the same size as a window canvas
        self.__widget_id = self.window.create_window(0, 0, window=widget, width=0, anchor=tk.NW,
                                  height=0)
        # the view id is used to keep track of everything INCLUDING the window canvas on the main canvas
        self.view_id = self.canvas.create_window(0, 0, window=self.window, anchor=tk.NW)
        self._selected = False
        # bind the widget and move it to the front
        self.widget.bind("<Button-1>", self.__select, add="+")
        self.widget.lift()
        # bind the configure method
        self.window.bind("<Configure>", self.__configure, add="+")

    def __configure(self, event):
        """This is called when the main window is changed, for example, resized. So we also resize everything inside the canvas"""
        self.window.itemconfig(self.__outline_id, width=event.width+4)
        self.window.itemconfig(self.__outline_id, height=event.height+4)
        self.window.itemconfig(self.__widget_id, width=event.width)
        self.window.itemconfig(self.__widget_id, height=event.height)

    def __select(self, event):
        self.selected = True

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = value
        self.window.itemconfig(self.__outline_id, state=tk.NORMAL if value else tk.HIDDEN)  # hide or show the outline
        # callback
        if value and "selected" in self._events:
            for event in self._events["selected"]:
                event(Event(self))
        if not value and "unselected" in self._events:
            for event in self._events["unselected"]:
                event(Event(self))


class TkMovableWidgetImpl(MovableWidget, TkWidgetImpl):
    """
    This class is the movable widget implementation. This implementation should be almost completely universal to all
    widgets.

    This class implements the position property as a Vector

    This class also implements the "moved" event, which calls the bound action with a Vector parameter representing the
    delta moved

    By inheriting from this class <B1-Motion> is bound on the widget to implement dragging.
    """
    def __init__(self, position=Vector(0, 0), **kwargs):
        self.__maxpos = Vector(0, 0)
        self.__click_offset = Vector(0, 0)
        self._position = Vector(0, 0)
        super().__init__(**kwargs)
        self.__recalc_maxpos(None, position) # this also set the position

        self.widget.bind("<B1-Motion>", self.__drag, add="+")
        self.widget.bind("<Button-1>", self.__click, add="+")
        self.bind_event("resized", self.__recalc_maxpos)
        self.parent.bind_event("resized", self.__recalc_maxpos)

    def __drag(self, event):
        """
        Called from the mouse being dragged across the widget
        """
        # event.x and event.y is the position of the mouse relative to the widget.This is essentially the delta
        new_pos = Vector(0, 0)
        new_pos.x = event.x_root - self.__click_offset.x
        new_pos.y = event.y_root - self.__click_offset.y
        
        self.position = new_pos

    def __click(self, event):
        """
        Called from the widget being clicked on
        """
        self.__click_offset = Vector(event.x_root - self.position.x, event.y_root - self.position.y)


    def __recalc_maxpos(self, event=None, position=None):
        """
        Recalculates and fixes the maximum x and y positions.
        Called when the user resizes the widget or parent widget, or durring __init__
        """
        max_x = 0
        max_y = 0
        if isinstance(self.parent, Sized):
            max_x = self.parent.size.x - self.size.x
            max_y = self.parent.size.y - self.size.y
        self.__maxpos = Vector(max_x, max_y)
        if position is None:
            self.position = self.position
        else:
            self.position = position


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
    
        
class TkSizableWidgetImpl(SizableWidget, TkWidgetImpl):
    """
    This is the implementation for a sizable widget. This should be almost universal to all tk widgets.

    This implements the size property which is a vector.

    This implements the "resized" event which calls with no params

    Inheriting from this class will place a square handle on the corner of the widget that can be dragged to resize.
    """
    def __init__(self, **kwargs):
        self._size = self.size
        super().__init__(**kwargs)
        # create a handle as a frame
        handle = tk.Frame(self.canvas.winfo_toplevel(), bg=colors.lightblue_primary)
        handle_fill = tk.Frame(handle, bg="white")
        handle_fill.pack(fill=tk.BOTH, expand=True, pady=2, padx=2)
        # put the handle into a canvas window at the bottom right
        handle_size = 10
        self.__handle_id = self.window.create_window(self.size.x+2, self.size.y+2, width=handle_size, height=handle_size, anchor=tk.SE,
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
        #self.size = self.size
        self.__click_offset = Vector(0, 0)

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
        self.size = new_size

    def __click(self, event):
        """
        The handle was clicked. Set up to be dragged
        """
        self.__click_offset = Vector(event.x_root - self.size.x, event.y_root - self.size.y)

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
            if hasattr(self, "__handle_id"):
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
        print(text)
        self.text = text
        self.font = font


class Frame(Container, MovableWidget, SizableWidget):
    """Represents a tk.Frame"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Button(TextContainer, MovableWidget, SizableWidget):
    def __init__(self, command=None, **kwargs):
        """
        @type canvas: tk.Canvas
        """
        super().__init__(**kwargs)
        self.command = command


class Label(TextContainer, MovableWidget, SizableWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Checkbutton(Label):
    def __init__(self, command="", offvalue="", onvalue="", takefocus=True, variable="", **kwargs):
        super().__init__(command=command, offvalue=offvalue, onvalue=onvalue, takefocus=takefocus, variable=variable, **kwargs)
        print("checkbutton")
        self.command = command
        self.offvalue = offvalue
        self.onvalue = onvalue
        self.takefoucs = takefocus
        self.variable = variable


class Entry(TextContainer, MovableWidget, SizableWidget):
    def __init__(self, justify="left", show="", validate="", validate_command="", associated_variable="", **kwargs):
        super().__init__(**kwargs)
        self.justify = justify
        self.show = show # indicates what character to replace with for password fields
        self.associated_variable = associated_variable
        self.validate = validate # when to validate http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/entry-validation.html
        self.validate_command = validate_command # a callback to dynamically validate contents
        

class TtkButtonImpl(Button, TkSizableWidgetImpl, TkMovableWidgetImpl):
    def __init__(self, canvas=None, text="", **kwargs):
        """
        @type canvas: tk.Canvas
        """
        #self.__text = ""
        
        new_button = ttk.Label(canvas.winfo_toplevel(), style="TButton")

        super().__init__(widget=new_button, canvas=canvas, **kwargs)

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


class TtkLabelImpl(Label, TkSizableWidgetImpl, TkMovableWidgetImpl):
    def __init__(self, canvas=None, text="", **kwargs):
        new_label = ttk.Label(canvas.winfo_toplevel(), style="TLabel")
        super().__init__(widget=new_label, canvas=canvas, **kwargs)
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
    def __init__(self, canvas=None, text="", justify="left", show="", validate="", validate_command="", associated_variable="",  **kwargs):
        self._text = text
        self._justify = justify
        self._show = show
        
        # To have a disabled entry looked like an enabled entry we must make an entire new style
        # style code grabbed from: http://stackoverflow.com/a/17639955
        style = ttk.Style()
        style.element_create("plain.field", "from", "clam")
        style.layout("EntryStyle.TEntry",
                           [('Entry.plain.field', {'children': [(
                               'Entry.background', {'children': [(
                                   'Entry.padding', {'children': [(
                                       'Entry.textarea', {'sticky': 'nswe'})],
                              'sticky': 'nswe'})], 'sticky': 'nswe'})],
                              'border':'2', 'sticky': 'nswe'})])
        style.configure("EntryStyle.TEntry",
                         background=colors.white_primary, # this is actually the background behind the whole widget
                         fieldbackground="white") # this is the background behind the text
        # end copied style code
        style.map("EntryStyle.TEntry",
                  foreground = [("disabled", "black") ] # requried to make the text appear black instead of disabled
                  )
        new_entry = ttk.Entry(canvas.winfo_toplevel(), style="EntryStyle.TEntry", state=tk.DISABLED)
        super().__init__(widget=new_entry, text=text, justify=justify, validate=validate, validate_command=validate_command, associated_variable=associated_variable, **kwargs)
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


class TtkCheckbuttonImpl(TkSizableWidgetImpl, TkMovableWidgetImpl, Checkbutton):
    def __init__(self, canvas=None, text="", **kwargs):
        print("******")
        style = ttk.Style()
        # This style removes the focus indicator. When clicking it won't place a dashed line around the label
        # There would appear to be no way to disabled the hover color
        # One idea would be to create the checkbutton as a label but then it is not possible to set the check on or off
        style.layout('CheckbuttonStyle.Checkbutton',
                        [('Checkbutton.padding', {'sticky': 'nswe', 'children':
                            [('Checkbutton.indicator', {'sticky': '', 'side': 'left'}),
                             ('Checkbutton.label', {'sticky': 'nswe'})],               
                            'side': 'left'})]
                     )
        self.intvar = tk.IntVar()
        self.intvar.set(0)
        new_checkbutton = ttk.Checkbutton(canvas.winfo_toplevel(), style="CheckbuttonStyle.Checkbutton", variable=self.intvar, offvalue=0, onvalue=0)
        self._text = text
        super().__init__(text=text, widget=new_checkbutton, canvas=canvas, **kwargs)

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
        

class WindowImpl(Window):
    def __init__(self, canvas=None, size=Vector(0, 0), **kwargs):
        super().__init__(size=size, **kwargs)
        self.widget = tk.Canvas(canvas, width=size.x, height=size.y)
        self.view_id = canvas.create_window(0, 0, window=self.widget, anchor=tk.NW)


if __name__ == "__main__":
    root = tk.Tk()
    mainCanvas = tk.Canvas(root, bg="#aaa")
    mainCanvas.pack()

    example_window = Window(title='foo', name='root_window')

    example_button = TtkButtonImpl(canvas=mainCanvas, position=Vector(40, 40), size=Vector(100, 200), parent=example_window)
    print(example_button.parent)
    #def selectExample(event): example.selected = True
    #def resize(event): example.size = Vector(example.size.x + 2, example.size.y + 2)
    #example.widget.bind("<Button-1>", selectExample)
    #example.bind_event("handle_dragged", lambda x: resize(x))

    root.mainloop()
    #root = Window(name="master", title="My Test Program", size=(1920, 1080))
    #mainFrame = Frame(parent=root, name="mainFrame", class_variable=True, size=(200, 600))
    #testButton = Button(parent=mainFrame, name="testButton", text="click me!", size=(100, 20), position=(10, 10))


    #for tests

