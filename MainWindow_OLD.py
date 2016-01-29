import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
from GUIObj_OLD import *
from OptionsWindow import *
from EditWindow import *
import re
import sys
import platform
import os

class MainWindow:
    def __init__(self):
        self.guiObjects = {}  # Dict of GUIObjs. Key: viewId , Value: GUIObj. Should make it easy to find the relavant GUIObj given an item id
        self.selectedObjs = []
        self.extra_code = ""
        self.file_name = None

        self.draggingViewId = None
        self.isDragging = False  # keeps track if we are dragging to select/create
        self.dragRootX = None  # The original click pos
        self.dragRootY = None
        self.dragPosX = None  # The ending mouse pos
        self.dragPosY = None

        self.root = Tk()
        self.root.title("PyPy Guimaker")
        self.root.geometry("1080x720")

        fileMenu = Menu(self.root)
        fileMenu.add_command(label="Save", command=self.save)
        fileMenu.add_command(label="Save As...", command=self.save_as)
        fileMenu.add_command(label="Load...", command=self.load)

        menubar = Menu(self.root)
        menubar.add_cascade(label="File", menu=fileMenu)
        menubar.add_command(label="Extra Module Code", command=self.openExtraCode)
        menubar.add_command(label="Run", command=self.run)
        self.root.config(menu=menubar)

        # style colors based on https://www.google.com/design/spec/style/color.html#
        ttk.Style().configure("Background.TFrame", background="#fafafa")
        ttk.Style().configure('Foreground.TFrame', background="#ffffff")
        ttk.Style().configure("Title.TLabel", background="#e0e0e0", foreground="#000000")
        ttk.Style().configure("Background.TLabel", background="#fafafa", foreground="#000000")
        ttk.Style().configure("Foreground.TLabel", background="#ffffff", foreground="#000000")

        #mainPannedFrame = ttk.PanedWindow(self.root, orient=HORIZONTAL)
        #mainPannedFrame.pack(side=LEFT, expand=True, fill=BOTH)

        #mainContentFrame = ttk.Frame(mainPannedFrame)
        #mainPannedFrame.add(mainContentFrame)

        mainContentFrame = ttk.Frame(self.root)
        mainContentFrame.pack(side=LEFT, expand=True, fill=BOTH)

        self.mainCanvas = Canvas(mainContentFrame)
        self.mainCanvas["background"] = "#e0e0e0"
        self.mainCanvas.pack(side=TOP, padx=5, pady=5, expand=True, fill=BOTH)

        #EXAMPLES
        test = GUIObj(self, self.mainCanvas, x=175, y=100, width=200, height=100)
        self.guiObjects[test.viewId] = test

        test2 = GUIObj(self, self.mainCanvas, x=50, y=50, width=100, height=200)
        self.guiObjects[test2.viewId] = test2
        self.guiObjects[test.viewId] = test

        #test2 = gui.Button(self, self.mainCanvas, x=50, y=50, width=100, height=200)
        #self.guiObjects[test2.viewId] = test2
        ##END EXAMPLES

        self.cordLabel = ttk.Label(mainContentFrame, style="Background.TLabel")
        self.cordLabel["text"] = "0, 0"
        self.cordLabel.pack(side=LEFT, padx=5, pady=5)

        self.debugLabel = ttk.Label(mainContentFrame, style="Background.TLabel")
        self.debugLabel["text"] = "Debug Label"
        self.debugLabel.pack(side=LEFT, padx=5, pady=5)

        #rightSecondaryFrame = ttk.Frame(mainPannedFrame)
        #mainPannedFrame.add(rightSecondaryFrame)
        rightSecondaryFrame = ttk.Frame(self.root)
        rightSecondaryFrame.pack(padx=5, pady=5, expand=False, fill=NONE)

        self.mainOptions = OptionsWindow(rightSecondaryFrame, None)
        self.mainOptions.mainFrame.pack(side=LEFT, expand=True, fill=BOTH)

        self.postInitialization()
        self.root.mainloop()

    def postInitialization(self):
        self.mainCanvas.bind('<ButtonPress-1>', self.mouse1Down)
        self.mainCanvas.bind('<ButtonRelease-1>', self.mouse1Up)
        self.mainCanvas.bind('<B1-Motion>', self.mouse1Drag)
        self.root.bind('<Key>', self.keyPress)

    def openExtraCode(self):
        editor = EditWindow(self)

    def mouse1Down(self, event):
        self.root.focus()
        if self.isDragging:
            self.clearDrag()
        self.isDragging = True
        self.dragRootX = event.x
        self.dragRootY = event.y
        self.debugLabel["text"] = "mouse 1 down"
        self.draggingViewId = self.mainCanvas.create_rectangle(self.dragRootX, self.dragRootY, self.dragRootX,
                                                               self.dragRootY, fill='', dash=[10, 30])
        for item in self.selectedObjs:
            item.unsetFocus()
        self.selectedObjs = []

    def mouse1Drag(self, event):
        if self.isDragging:
            self.debugLabel["text"] = "dragging"
            self.dragPosX = event.x
            self.dragPosY = event.y
            self.mainCanvas.coords(self.draggingViewId, self.dragRootX, self.dragRootY, self.dragPosX,
                                   self.dragPosY)

    def mouse1Up(self, event):
        '''Stoped dragging on the canvas. Focus the selection if there was any'''
        if self.isDragging:
            self.debugLabel["text"] = "mouse 1 up"
            self.dragPosX = event.x
            self.dragPosY = event.y
            selectedIds = self.mainCanvas.find_overlapping(self.dragRootX, self.dragRootY, self.dragPosX, self.dragPosY)
            self.debugLabel["text"] = selectedIds
            for itemId in selectedIds:
                if itemId in self.guiObjects:
                    self.selectedObjs.append(self.guiObjects[itemId])
                    self.guiObjects[itemId].setFocus()

    def keyPress(self, event):
        # The user pressed somewhere on the canvas not on a widget
        if str(event.char) == "n" and self.draggingViewId is not None:
            self.clearDrag()
            newObj = GUIObj(self, self.mainCanvas, Button, self.dragRootX, self.dragRootY,
                            self.dragPosX - self.dragRootX, self.dragPosY - self.dragRootY)
            self.guiObjects[newObj.viewId] = newObj
            self.selectedObjs = []
            #for frame in self.maskingFrames:
            #    frame.lift()

    def clearDrag(self):
        self.isDragging = False
        self.mainCanvas.delete(self.draggingViewId)
        self.draggingViewId = None

    def setFocus(self, guiObj):
        '''gives the given GUIObj focus'''
        self.mainOptions.guiObj = guiObj


    def onObjMove(self, guiObj, deltaX, deltaY):
        '''Forwards the moved object to the options menu, and moves all other objects'''
        for obj in self.selectedObjs:
            if obj != guiObj:
                try:
                    obj.x += deltaX
                except:
                    pass
                try:
                    obj.y += deltaY
                except:
                    pass

        self.mainOptions.moveObj(guiObj)

    def onObjResize(self, guiObj, deltaX, deltaY):
        '''Forwards the resized object to the options menu'''
        for obj in self.selectedObjs:
            obj.width += deltaX
            obj.height += deltaY

        self.mainOptions.resizeObj(guiObj)

    def run(self):
        """saves the file and runs the gui"""
        self.save()
        os.system("where python > ztemp")
        filename= self.file_name
        with open("ztemp","r") as myfile:
            command=myfile.read()
            command = command.strip()
            #print("command=/"+command+"/")
            newcommand = command+" "+filename
            os.system(newcommand)
            

    def save_as(self):
        self.save_contents(file_name=None)

    def save(self):
        self.save_contents(file_name=self.file_name)

    def save_contents(self, file_name=None):
        output = ""
        # do some basic imports and setup
        output += "from tkinter import *\n"
        output += "\n"
        # add extra module code
        output += self.extra_code
        output += "\n"
        # make the function
        output += "def initialize():\n"
        output += '''    """generated by pypyguimaker. creates the tkinter window"""\n'''
        # define all the globals
        object_names = [object.name for object in self.guiObjects.values()]
        output += "    global " + str(object_names).strip("[").strip("]").replace("'","") + "\n"
        # create the root
        output += "    root = Tk()\n"
        output += "    root.geometry('500x500')\n"
        output += "    root.title('Python application')\n"
        output += "\n"

        for object in self.guiObjects.values():
            output += "    %s = %s(root" % (object.name, object.tkType.__name__)
            if object.action:
                action_output = object.action
                if object.action.startswith("="):
                    action_output = "lambda:" + object.action[1:]
                output += ", command=%s" % (action_output)
            output += ")\n"
            output += "    %s['text'] = '%s'\n" % (object.name, object.text)  # This could be empty
            output += "    %s.place(x=%s, y=%s, width=%i, height=%i)\n" % \
                      (object.name, object.x, object.y, object.width, object.height)
            output += "\n"

        output += "    root.mainloop()\n"
        output += "\n"
        output += "initialize()"

        if file_name is None:
            try:
                with tkinter.filedialog.asksaveasfile(mode='w') as file:
                    self.file_name = file.name
                    file.write(output)
                    file.close()
                    # update the file name
                    self.root.wm_title("PyPy Guimaker: " + self.file_name)
            except:
                pass
        else:
            with open(file_name, "w") as file:
                file.write(output)
                file.close()

    def load(self):
        '''clears the window and loads a file'''
        # parses the gui from a file
        try:
            with tkinter.filedialog.askopenfile(mode='r') as file:
                self.clear()
                self.file = file
                
                lines = file.readlines()
                inInitialize = False
                currentGuiobj = None
                for line in lines:
                    original_line = line # the unmodified line. Used to just copy the text
                    lineTab = len(line) - len(line.strip(' '))  # counts the number of leading spaces
                    line = line.strip(' ')
                    line = line.replace('\n', '')
                    if line == "def initialize():":
                        inInitialize = True
                        continue
                    if inInitialize:
                        # ignore comments
                        if line.startswith("#"):
                            continue
                        # ignore empty lines
                        if line == "":
                            continue
                        # ignore global declarations
                        if line.startswith("global"):
                            continue
                        # if the line is not indented then we have left the initialize method
                        if lineTab == 0:
                            inInitialize = False
                            continue
                        # ignore docstrings
                        if line.startswith('''"""'''):
                            continue
                        # get the objects name
                        objName = re.split("\s|\[|\.", line)[0]
                        # ignore root stuff
                        if objName == "root":
                            continue
                        # this obj is new
                        if currentGuiobj is None or objName != currentGuiobj.name:
                            # get objtype from a string OBJNAME = OBJTYPE(root<,options>)
                            objType = WidgetTypeHelper.convertToType(line.split("=")[1].split("(")[0].strip(" "))
                            # create the new guiobj
                            currentGuiobj = GUIObj(self, self.mainCanvas)
                            currentGuiobj.name = objName
                            currentGuiobj.tkType = objType
                            self.guiObjects[currentGuiobj.viewId] = currentGuiobj
                            print("$$$$$ ",line)
                            n = line.index("(")
                            templine = line[n+1:]
                            options_strings = templine.split(",")[1:]
                            #options_strings = line[0:-1].split("(")[1].split(",")[1:]
                            print("options_strings=")
                            print(options_strings)
                            options = {option.split("=")[0].strip(" "): option.split("=")[1].strip(" ") for option in options_strings}
                            print(options)
                            if "command" in options.keys():
                                # load the command binding
                                if options["command"].startswith("lambda:"):
                                    options["command"] = "=" + options["command"].strip("lambda:")
                                currentGuiobj.action = options["command"]
                            continue
                        else:
                            command = line.strip(objName)
                            # if the command starts with [ then it's an attribute
                            if command.startswith("["):
                                attribute = command.split("=")[0].strip(' ')  # get only ['ATTRIBUTENAME']
                                attribute = attribute[2:-2]  # get only ATTRIBUTENAME
                                value = command.split("=")[1].strip(' ')  # get only ATTRIBUTEVALUE
                                if attribute == "text":
                                    currentGuiobj.text = value.strip("'")
                            # if the command starts with .place( then it's a place command...
                            if command.startswith(".place("):
                                #construct a list of attrbute strings formated as ATTRIBUTE=VALUE
                                atrributes = command[7:-1]
                                atrributes = atrributes.split(", ")
                                for atrributePair in atrributes:
                                    attribute = atrributePair.split("=")[0]
                                    value = atrributePair.split("=")[1]
                                    if attribute == "y":
                                        currentGuiobj.y = int(value)
                                    elif attribute == "x":
                                        currentGuiobj.x = int(value)
                                    elif attribute == "width":
                                        currentGuiobj.width = int(value)
                                    elif attribute == "height":
                                        currentGuiobj.height = int(value)
                    else:
                        # load the extra code
                        # ignore import
                        if line != "from tkinter import *":
                            # ignore if the first line is empty
                            if not (self.extra_code == "" and line == ""):
                                self.extra_code += original_line
        except:
            pass

    def isRootStatement(self, statement):
        possibleStatements = ["root.geometry(", "root.title("]
        for possible in possibleStatements:
            if possible == statement:
                return True
        return False

    def clear(self):
        """clears all state from the program"""
        self.guiObjects = {}
        self.selectedObjs = []
        self.extra_code = ""

        self.draggingViewId = None
        self.isDragging = False
        self.dragRootX = None
        self.dragRootY = None
        self.dragPosX = None
        self.dragPosY = None

        self.mainCanvas.delete("all")

if __name__ == "__main__":
    MainWindow()