from  tkinter import *
import tkinter.ttk as ttk
from OptionsWindow import *
import random

class GUIObj:
    '''Keeps track of a single tkinter widget and provides methods to manipulate and display the widgets properties through the gui'''
    # Convert tkinter types to style names.
    # from: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/ttk-style-layer.html - Might not be a compltete list?
    type2Style = {
        Button: "TButton",
        Checkbutton: "TCheckbutton",
        ttk.Combobox: "TCombobox",
        Entry: "TEntry",
        Text: "TEntry",  # ttk apparently has no built in Text style?
        Frame: "TFrame",
        Label: "TLabel",
        LabelFrame: "TLabelframe",
        Menubutton: "TMenubutton",
        ttk.Notebook: "TNotebook",
        ttk.PanedWindow: "TPanedwindow",
        ttk.Progressbar: "Horizontal.TProgressbar",  # could be Vertical.TProgressbar too
        Radiobutton: "TRadiobutton",
        Scale: "Horizontal.TScale",  # could be Vertical.TScale too
        Scrollbar: "Horizontal.TScale",  # could be Vertical.TScale too
        ttk.Separator: "TSeperator",
        ttk.Sizegrip: "TSizegrip",
        ttk.Treeview: "Treeview"}

    def __init__(self, window, canvas, tkType=Button, x=0, y=0, width=0, height=0, text="DEFAULT", background=None):
        # self.style = ttk.Style()
        # self.style.configure("FakeDisabled", foreground="black", background="white")

        self._x = x
        self._y = y
        self.viewId = None
        self.canvas = None
        self.lastX = None
        self.lastY = None
        if width < 0:
            self.x += width
            width *= -1
        if height < 0:
            self.y += height
            height *= -1

        # widget options
        self.name = "randName%i" % (int(random.random() * 1000000))
        self._tkType = tkType
        self._width = width
        self._height = height
        self._text = text
        if background is None:
            self._background = "#ebebeb"
        else:
            self._background = background
        self.action = ""

        self.minWidth = 20
        self.minHeight = 20

        self.canvas = canvas
        self.window = window

        self.selectedCanvas = Canvas(window.root, width=self.width + 2, height=self.height + 2,
                                     highlightthickness=0, background="red")
        self.selectedOutline = canvas.create_window(self.x - 1, self.y - 1,
                                                    height=self.height + 2, width=self.width + 2,
                                                    window=self.selectedCanvas, anchor=NW, state=HIDDEN)
        self.widget = ttk.Label(window.root, text="example button", style="TButton")
        self.widget["text"] = self.text
        self.widget.bind('<ButtonPress-1>', self.__mouse1Down)
        self.widget.bind('<B1-Motion>', self.__mouse1Drag)
        self.viewId=canvas.create_window(self.x, self.y, width = self.width, height = self.height,
                                         window=self.widget, anchor=NW) # The window item determines the size of the widget

        resizeHandleSize = 10
        self.resizeCanvas = Canvas(window.root, width=resizeHandleSize, height=resizeHandleSize, highlightthickness=0)
        self.resizeCanvas.create_rectangle(0, 0, resizeHandleSize, resizeHandleSize, fill="#ebebeb")
        self.resizeHandle = canvas.create_window(self.x + self.width - resizeHandleSize - 1,
                                                 self.y + self.height - resizeHandleSize - 1,
                                                 height = resizeHandleSize + 1, width = resizeHandleSize + 1,
                                                 window = self.resizeCanvas, anchor=NW, state=HIDDEN)
        self.resizeCanvas.bind('<ButtonPress-1>', self.__resizeMouse1Down)
        self.resizeCanvas.bind('<B1-Motion>', self.__resizeMouse1Drag)

    @property
    def tkType(self):
        return self._tkType

    @tkType.setter
    def tkType(self, value):
        """Changes the type of widget"""
        self.widget["style"] = self.type2Style[value]
        self._tkType = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        if "text" in self.widget.keys():
            self.widget["text"] = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        delta = value - self.width
        if self.width + delta < self.minWidth:
            delta = 0
            value = self.width
        self._width = value
        self.canvas.itemconfig(self.viewId, width=value)
        self.canvas.itemconfig(self.selectedOutline, width=value + 2)
        self.canvas.move(self.resizeHandle, delta, 0)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        delta = value - self.height
        if self.height + delta < self.minHeight:
            delta = 0
            value = self.height
        self._height = value
        self.canvas.itemconfig(self.viewId, height=value)
        self.canvas.itemconfig(self.selectedOutline, height=value + 2)
        self.canvas.move(self.resizeHandle, 0, delta)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        delta = 0
        hasValueError = False
        #TODO: Fix to use a window width set by user instead of canvas width
        if value < 0:
            delta = 0 - self.x
            hasValueError = True
        elif value + self.width > int(self.canvas.winfo_width()):
            delta = int(self.canvas.winfo_width()) - self.x - self.width
            hasValueError = True
        else:
            #pos in-bounds
            delta = value - self.x
        self.__move(delta, 0)
        self._x += delta
        if hasValueError:
            raise ValueError("value puts obj out of bounds, moving object as close as possible")

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        delta = 0
        hasValueError = False
         #TODO: Fix to use a window height set by user instead of canvas width
        if value < 0:
            delta = 0 - self.y
            hasValueError = True
        elif value + self.height > int(self.canvas.winfo_height()):
            delta = int(self.canvas.winfo_height()) - self.y - self.height
            hasValueError = True
        else:
            #pos in-bounds
            delta = value - self.y
        self.__move(0, delta)
        self._y += delta
        if hasValueError:
            raise ValueError("value puts obj out of bounds, moving object as close as possible")

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, value):
        self._background = value
        #self.widget["background"] = value #Broken: ttk doesn't have ["background"], use the style instead!

    def __move(self, deltaX, deltaY):
        '''Moves the view by the given delta values'''
        self.canvas.move(self.resizeHandle, deltaX, deltaY)
        self.canvas.move(self.selectedOutline, deltaX, deltaY)
        self.canvas.move(self.viewId, deltaX, deltaY)

    def __mouse1Drag(self, event):
        '''The user is dragging the obj across the screen'''
        deltaX = event.x_root - self.lastX #using x_root is useful because we won't get confused by relative positions
        deltaY = event.y_root - self.lastY
        preX = self.x
        preY = self.y
        try:
            self.x += deltaX
        except:
            pass
        try:
            self.y += deltaY
        except:
            pass
        deltaX = self.x - preX
        deltaY = self.y - preY
        self.lastX += deltaX
        self.lastY += deltaY

        self.window.onObjMove(self, deltaX, deltaY)

    def __mouse1Down(self, event):
        '''prepares the view to be dragged and brings the view to the front.''' #Might be useful to modify this so all selected views are brought to the front
        self.lastX = event.x_root
        self.lastY = event.y_root
        self.canvas.tag_raise(self.viewId)
        if len(self.window.selectedObjs) <= 1 or self not in self.window.selectedObjs:
            for item in self.window.selectedObjs:
                item.unsetFocus()
            self.window.selectedObjs = [self]
            self.setFocus()
            self.window.debugLabel["text"] = [obj.viewId for obj in self.window.selectedObjs]
        self.window.clearDrag() #This call is only necessary for widows+widgets
        self.window.setFocus(self)

    def __mouse1Double(self, event):
        '''user double clicked, open the options menu'''
        self.optionsWindow = OptionsWindow(self.tkType, self)

    def __resizeMouse1Down(self, event):
        '''The resize handle was clicked'''
        self.lastX = event.x_root
        self.lastY = event.y_root
        self.window.clearDrag()
        self.window.setFocus(self)

    def __resizeMouse1Drag(self, event):
        '''The resize handle was dragged'''
        deltaX = event.x_root - self.lastX
        deltaY = event.y_root - self.lastY
        self.lastX = event.x_root
        self.lastY = event.y_root
        self.window.onObjResize(self, deltaX, deltaY)

    def setFocus(self):
        '''makes the obj visually active'''
        self.canvas.itemconfig(self.resizeHandle, state=NORMAL)
        self.canvas.itemconfig(self.selectedOutline, state=NORMAL)

    def unsetFocus(self):
        '''makes the obj visually innactive'''
        self.canvas.itemconfig(self.resizeHandle, state=HIDDEN)
        self.canvas.itemconfig(self.selectedOutline, state=HIDDEN)
