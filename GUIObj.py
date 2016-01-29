__author__ = 'robert'

import tkinter as tk
import tkinter.ttk as ttk
import colors

class GUIObj:
    """Represents the most basic gui object"""
    def __init__(self, name="", class_variable=False, **kwargs):
        self.name = name
        self.class_variable = class_variable


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


class Window(Container):
    """Represents a window on the screen. Is a Container for other widgets"""
    def __init__(self, title="", size=(600, 800), **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.size = size


class Widget(GUIObj):
    """Represents all tk widgets. Must be a child of a container."""
    def __init__(self, parent=None, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent
        self._events = {}
        self.parent.add_child(self)

    def bind_event(self, event, action):
        """Binds the action to the event."""
        # This is my way of doing callbacks/bindings/events. I looked up on google for python event and it seems there
        # is not built in event code. So this is a quick and basic way to do it. Store actions for an event as a list
        # in a dict, where the event is the key
        self._events[event] = self._events.get(event, []).append(action)


class Vector:
    """Represents a position in 2d space"""
    def __init__(self, x, y):
        self.x = x
        self.y = y


class MovableWidget(Widget):
    """A Widget that has a position"""
    def __init__(self, position=Vector(0, 0), **kwargs):
        super().__init__(**kwargs)
        self.position = position


class SizableWidget(Widget):
    """A Widget that has a size"""
    def __init__(self, size=Vector(0, 0), **kwargs):
        super().__init__(**kwargs)
        self.size = size


class TkWidgetImpl(Widget):
    def __init__(self, widget=None, canvas=None, **kwargs):
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

        super().__init__(**kwargs)
        self.canvas = canvas
        self.widget = widget
        self.window = tk.Canvas()  # the window is a canvas that contains everything related to the widget
        # create the selection outline
        # We use a blue frame and make it 2 pixels wider than the window canvas
        self.__outline_id = self.window.create_window(-1, -1, window=tk.Frame(bg=colors.lightblue_primary),
                                                      anchor=tk.NW,
                                                      width=0,
                                                      height=0,
                                                      state=tk.HIDDEN)
        # place the widget into the window
        # we use the same size as a window canvas
        self.__widget_id = self.window.create_window(0, 0, window=widget, width=0, anchor=tk.NW,
                                  height=0)
        # the view id is used to keep track of everything INCLUDING the window canvas on the main canvas
        self.view_id = canvas.create_window(0, 0, window=self.window, anchor=tk.NW)
        self._selected = False
        # bind the widget and move it to the front
        self.widget.bind("<Button-1>", self.__select, add="+")
        self.widget.lift()
        # bind the configure method
        self.window.bind("<Configure>", self.__configure, add="+")

    def __configure(self, event):
        """This is called when the main window is changed, for example, resized. So we also resize everything inside the canvas"""
        self.window.itemconfig(self.__outline_id, width=event.width+2)
        self.window.itemconfig(self.__outline_id, height=event.height+2)
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
                event(None)
        if not value and "unselected" in self._events:
            for event in self._events["unselected"]:
                event(None)


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
        self.__click_offset = Vector(0, 0)
        self._position = Vector(0, 0)
        super().__init__(**kwargs)
        self.position = position
        self.widget.bind("<B1-Motion>", self.__drag, add="+")
        self.widget.bind("<Button-1>", self.__click, add="+")

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

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        # calculate the delta and move the view_id by the delta
        delta_x = value.x - self.position.x
        delta_y = value.y - self.position.y
        self.canvas.move(self.view_id, delta_x, delta_y)
        self._position = value
        # callback
        if "moved" in self._events:
            delta = Vector(delta_x, delta_y)
            for event in self._events["moved"]:
                event(delta)

        
class TkSizableWidgetImpl(SizableWidget, TkWidgetImpl):
    """
    This is the implementation for a sizable widget. This should be almost universal to all tk widgets.

    This implements the size property which is a vector.

    This implements the "resized" event which calls with no params

    Inheriting from this class will place a square handle on the corner of the widget that can be dragged to resize.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._size = self.size
        # create a handle as a frame
        handle = tk.Frame(self.canvas.winfo_toplevel(), bg="black")
        handle_fill = tk.Frame(handle, bg="white")
        handle_fill.pack(fill=tk.BOTH, expand=True, pady=1, padx=1)
        # put the handle into a canvas window at the bottom right
        handle_size = 10
        self.__handle_id = self.window.create_window(self.size.x + 1, self.size.x + 1, width=handle_size, height=handle_size, anchor=tk.SE,
                                                     window=handle)
        # bind the handle drags
        handle.bind("<B1-Motion>", self.__drag, add="+")
        handle_fill.bind("<B1-Motion>", self.__drag, add="+")
        handle.bind("<Button-1>", self.__click, add="+")
        handle_fill.bind("<Button-1>", self.__click, add="+")
        # Have the widget update it's size
        self.size = self.size
        self.__click_offset = Vector(0, 0)

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
            self.window.move(self.__handle_id, delta.x, delta.y)
            # callback
            if "resized" in self._events:
                for event in self._events["resized"]:
                    event()
        else:
            self._size = value


class Font:
    """Represents a font family"""
    pass


class TextContainer:
    """Represents a widget that contains text"""
    def __init__(self, text="", font=Font(), **kwargs):
        self.text = text
        self.font = font


class Frame(Container, MovableWidget, SizableWidget):
    """Represents a tk.Frame"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Button(MovableWidget, SizableWidget, TextContainer):
    def __init__(self, **kwargs):
        """
        @type canvas: tk.Canvas
        """
        super().__init__(**kwargs)


class TtkButtonImpl(TkSizableWidgetImpl, TkMovableWidgetImpl, Button, TextContainer):
    def __init__(self, canvas=None, **kwargs):
        """
        @type canvas: tk.Canvas
        """
        
        new_button = ttk.Label(canvas.winfo_toplevel(), style="TButton")
        new_button["text"] = "default"

        super().__init__(widget=new_button, canvas=canvas, **kwargs)


if __name__ == "__main__":
    root = tk.Tk()
    mainCanvas = tk.Canvas(root, bg="#aaa")
    mainCanvas.pack()

    example_window = Window(title='foo', name='root_window')

    example_button = TtkButtonImpl(canvas=mainCanvas, position=Vector(0, 0), size=Vector(50, 50), parent=example_window)
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

