from tkinter import *
import tkinter.ttk as ttk
from WidgetTypeHelper import *
from VerticalScrollFrame import *


class OptionsWindow:
    errorColor = "red"
    normalColor = "black"

    def __init__(self, root, guiObj):
        """guiObj is the GUIObj that this window is manipulating. Created with an unplaced "mainFrame" that holds
           all the widgets"""
        self._guiObj = guiObj
        inputWidth = 160
        labelWidth = 60
        paddingY = 1
        paddingX = 5

        # self.root = Tk()
        # self.root.geometry("280x400")
        # self.root.configure(background="#ebebeb")
        # self.root.title("Widget Options")

        self.mainFrame = ttk.Frame(root, style="Background.TFrame")

        titleLabel = ttk.Label(self.mainFrame, style="Title.TLabel")
        titleLabel["anchor"] = CENTER
        titleLabel["text"] = "Widget"
        titleLabel.pack(fill=X, expand=TRUE)

        nameFrame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        nameFrame.pack(fill=X, expand=TRUE)

        nameLabel = ttk.Label(nameFrame, style="Foreground.TLabel")
        nameLabel["anchor"] = E
        nameLabel["text"] = "Name"
        nameLabel.pack(padx=paddingX, pady=paddingY, side=LEFT)

        self.nameText = ttk.Entry(nameFrame, width=20)
        self.nameText.insert(END, "???")
        self.nameText.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        self.nameText.bind("<KeyPress-Return>", self.__submitNameText)
        self.nameText.bind("<FocusOut>", self.__submitNameText)

        textFrame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        textFrame.pack(fill=X, expand=TRUE)

        textLabel = ttk.Label(textFrame, style="Foreground.TLabel")
        textLabel["anchor"] = E
        textLabel["text"] = "Text"
        textLabel.pack(padx=paddingX, pady=paddingY, side=LEFT)

        self.textText = ttk.Entry(textFrame, width=20)
        self.textText.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        self.textText.bind("<KeyPress-Return>", self.__submitText)
        self.textText.bind("<FocusOut>", self.__submitText)

        typeFrame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        typeFrame.pack(fill=X, expand=TRUE)

        typeLabel = ttk.Label(typeFrame, style="Foreground.TLabel")
        typeLabel["anchor"] = E
        typeLabel["text"] = "Type"
        typeLabel.pack(padx=paddingX, pady=paddingY, side=LEFT)

        self.typeVar = StringVar(self.mainFrame)
        self.typeVar.set(" ")

        self.typeOptionMenu = ttk.OptionMenu(typeFrame, self.typeVar, *([None] + sorted(WidgetTypeHelper.typeNames.keys())),
                                             command=self.__submitType)
        self.typeOptionMenu.pack(padx=paddingX, pady=paddingY, side=RIGHT)

        positionLabel = ttk.Label(self.mainFrame, style="Title.TLabel")
        positionLabel["anchor"] = CENTER
        positionLabel["text"] = "Position"
        positionLabel.pack(fill=X, expand=TRUE)

        xPosFrame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        xPosFrame.pack(fill=X, expand=TRUE)

        xLabel = ttk.Label(xPosFrame, style="Foreground.TLabel")
        xLabel["anchor"] = E
        xLabel["text"] = "X position"
        xLabel.pack(padx=paddingX, pady=paddingY, side=LEFT)

        self.xText = ttk.Entry(xPosFrame, width=20)
        self.xText.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        self.xText.bind("<KeyPress-Return>", self.__submitXPos)
        self.xText.bind("<FocusOut>", self.__submitXPos)

        yPosFrame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        yPosFrame.pack(fill=X, expand=True)

        yLabel = ttk.Label(yPosFrame, style="Foreground.TLabel")
        yLabel["anchor"] = E
        yLabel["text"] = "Y position"
        yLabel.pack(padx=paddingX, pady=paddingY, side=LEFT)

        self.yText = ttk.Entry(yPosFrame, width=20)
        self.yText.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        self.yText.bind("<KeyPress-Return>", self.__submitYPos)
        self.yText.bind("<FocusOut>", self.__submitYPos)

        widthFrame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        widthFrame.pack(fill=X, expand=True)

        widthLabel = ttk.Label(widthFrame, style="Foreground.TLabel")
        widthLabel["anchor"] = E
        widthLabel["text"] = "Width"
        widthLabel.pack(padx=paddingX, pady=paddingY, side=LEFT)

        self.widthText = ttk.Entry(widthFrame, width=20)
        self.widthText.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        self.widthText.bind("<KeyPress-Return>", self.__submitWidth)
        self.widthText.bind("<FocusOut>", self.__submitWidth)

        heightFrame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        heightFrame.pack(fill=X, expand=True)

        heightLabel = ttk.Label(heightFrame, style="Foreground.TLabel")
        heightLabel["anchor"] = E
        heightLabel["text"] = "Height"
        heightLabel.pack(padx=paddingX, pady=paddingY, side=LEFT)

        self.heightText = ttk.Entry(heightFrame, width=20)
        self.heightText.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        self.heightText.bind("<KeyPress-Return>", self.__submitHeight)
        self.heightText.bind("<FocusOut>", self.__submitHeight)

        bindingLabel = ttk.Label(self.mainFrame, style="Title.TLabel")
        bindingLabel["anchor"] = CENTER
        bindingLabel["text"] = "Bindings"
        bindingLabel.pack(fill=X, expand=TRUE)

        # --- Events --- #
        # --- Regular Events --- #
        actionFrame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        actionFrame.pack(fill=X, expand=TRUE)

        actionLabel = ttk.Label(actionFrame, style="Foreground.TLabel")
        actionLabel["anchor"] = E
        actionLabel["text"] = "Action"
        actionLabel.pack(padx=paddingX, pady=paddingY, side=LEFT)

        self.actionText = ttk.Entry(actionFrame, width=20)
        self.actionText.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        self.actionText.bind("<KeyPress-Return>", self.__submitAction)
        self.actionText.bind("<FocusOut>", self.__submitAction)

        # enterFrame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # enterFrame.pack(fill=X, expand=TRUE)
        #
        # enterLabel = ttk.Label(enterFrame, style="Foreground.TLabel")
        # enterLabel["anchor"] = E
        # enterLabel["text"] = "Mouse Enter"
        # enterLabel.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.enterText = ttk.Entry(enterFrame, width=20)
        # self.enterText.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        # #self.actionText.bind("<KeyPress-Return>", self.__submitB1Motion)
        # #self.actionText.bind("<FocusOut>", self.__submitB1Motion)
        #
        # # --- Button-1 events --- #
        # button1Frame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # button1Frame.pack(fill=X, expand=TRUE)
        #
        # button1Label = ttk.Label(button1Frame, style="Foreground.TLabel")
        # button1Label["anchor"] = E
        # button1Label["text"] = "Button-1 Press"
        # button1Label.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.button1Text = ttk.Entry(button1Frame, width=20)
        # self.button1Text.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        # #self.actionText.bind("<KeyPress-Return>", self.__submitButton1)
        # #self.actionText.bind("<FocusOut>", self.__submitButton1)
        #
        # b1MotionFrame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # b1MotionFrame.pack(fill=X, expand=TRUE)
        #
        # b1MotionLabel = ttk.Label(b1MotionFrame, style="Foreground.TLabel")
        # b1MotionLabel["anchor"] = E
        # b1MotionLabel["text"] = "Button-1 Motion"
        # b1MotionLabel.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.b1MotionText = ttk.Entry(b1MotionFrame, width=20)
        # self.b1MotionText.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        # #self.actionText.bind("<KeyPress-Return>", self.__submitB1Motion)
        # #self.actionText.bind("<FocusOut>", self.__submitB1Motion)
        #
        # buttonRelease1Frame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # buttonRelease1Frame.pack(fill=X, expand=TRUE)
        #
        # buttonRelease1Label = ttk.Label(buttonRelease1Frame, style="Foreground.TLabel")
        # buttonRelease1Label["anchor"] = E
        # buttonRelease1Label["text"] = "Button-1 Release"
        # buttonRelease1Label.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.buttonRelease1Text = ttk.Entry(buttonRelease1Frame, width=20)
        # self.buttonRelease1Text.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        # #self.actionText.bind("<KeyPress-Return>", self.__submitB1Motion)
        # #self.actionText.bind("<FocusOut>", self.__submitB1Motion)
        #
        # buttonDouble1Frame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # buttonDouble1Frame.pack(fill=X, expand=TRUE)
        #
        # buttonDouble1Label = ttk.Label(buttonDouble1Frame, style="Foreground.TLabel")
        # buttonDouble1Label["anchor"] = E
        # buttonDouble1Label["text"] = "Button-1 Double"
        # buttonDouble1Label.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.buttonDouble1Text = ttk.Entry(buttonDouble1Frame, width=20)
        # self.buttonDouble1Text.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        # #self.actionText.bind("<KeyPress-Return>", self.__submitB1Motion)
        # #self.actionText.bind("<FocusOut>", self.__submitB1Motion)
        #
        # # --- Button-2 events --- #
        # button2Frame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # button2Frame.pack(fill=X, expand=TRUE)
        #
        # button2Label = ttk.Label(button2Frame, style="Foreground.TLabel")
        # button2Label["anchor"] = E
        # button2Label["text"] = "Button-2 Press"
        # button2Label.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.button2Text = ttk.Entry(button2Frame, width=20)
        # self.button2Text.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        #
        # b2MotionFrame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # b2MotionFrame.pack(fill=X, expand=TRUE)
        #
        # b2MotionLabel = ttk.Label(b2MotionFrame, style="Foreground.TLabel")
        # b2MotionLabel["anchor"] = E
        # b2MotionLabel["text"] = "Button-2 Motion"
        # b2MotionLabel.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.b2MotionText = ttk.Entry(b2MotionFrame, width=20)
        # self.b2MotionText.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        # #self.actionText.bind("<KeyPress-Return>", self.__submitB1Motion)
        # #self.actionText.bind("<FocusOut>", self.__submitB1Motion)
        #
        # buttonRelease2Frame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # buttonRelease2Frame.pack(fill=X, expand=TRUE)
        #
        # buttonRelease2Label = ttk.Label(buttonRelease2Frame, style="Foreground.TLabel")
        # buttonRelease2Label["anchor"] = E
        # buttonRelease2Label["text"] = "Button-2 Release"
        # buttonRelease2Label.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.buttonRelease2Text = ttk.Entry(buttonRelease2Frame, width=20)
        # self.buttonRelease2Text.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        # #self.actionText.bind("<KeyPress-Return>", self.__submitB1Motion)
        # #self.actionText.bind("<FocusOut>", self.__submitB1Motion)
        #
        # buttonDouble2Frame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # buttonDouble2Frame.pack(fill=X, expand=TRUE)
        #
        # buttonDouble2Label = ttk.Label(buttonDouble2Frame, style="Foreground.TLabel")
        # buttonDouble2Label["anchor"] = E
        # buttonDouble2Label["text"] = "Button-2 Double"
        # buttonDouble2Label.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.buttonDouble2Text = ttk.Entry(buttonDouble2Frame, width=20)
        # self.buttonDouble2Text.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        # #self.actionText.bind("<KeyPress-Return>", self.__submitB1Motion)
        # #self.actionText.bind("<FocusOut>", self.__submitB1Motion)
        #
        #  # --- Button-3 events --- #
        # button3Frame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # button3Frame.pack(fill=X, expand=TRUE)
        #
        # button3Label = ttk.Label(button3Frame, style="Foreground.TLabel")
        # button3Label["anchor"] = E
        # button3Label["text"] = "Button-3 Press"
        # button3Label.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.button3Text = ttk.Entry(button3Frame, width=20)
        # self.button3Text.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        #
        # b3MotionFrame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # b3MotionFrame.pack(fill=X, expand=TRUE)
        #
        # b3MotionLabel = ttk.Label(b3MotionFrame, style="Foreground.TLabel")
        # b3MotionLabel["anchor"] = E
        # b3MotionLabel["text"] = "Button-3 Motion"
        # b3MotionLabel.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.b3MotionText = ttk.Entry(b3MotionFrame, width=20)
        # self.b3MotionText.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        # #self.actionText.bind("<KeyPress-Return>", self.__submitB1Motion)
        # #self.actionText.bind("<FocusOut>", self.__submitB1Motion)
        #
        # buttonRelease3Frame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # buttonRelease3Frame.pack(fill=X, expand=TRUE)
        #
        # buttonRelease3Label = ttk.Label(buttonRelease3Frame, style="Foreground.TLabel")
        # buttonRelease3Label["anchor"] = E
        # buttonRelease3Label["text"] = "Button-3 Release"
        # buttonRelease3Label.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.buttonRelease3Text = ttk.Entry(buttonRelease3Frame, width=20)
        # self.buttonRelease3Text.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        # #self.actionText.bind("<KeyPress-Return>", self.__submitB1Motion)
        # #self.actionText.bind("<FocusOut>", self.__submitB1Motion)
        #
        # buttonDouble3Frame = ttk.Frame(self.mainFrame, style="Foreground.TLabel")
        # buttonDouble3Frame.pack(fill=X, expand=TRUE)
        #
        # buttonDouble3Label = ttk.Label(buttonDouble3Frame, style="Foreground.TLabel")
        # buttonDouble3Label["anchor"] = E
        # buttonDouble3Label["text"] = "Button-3 Double"
        # buttonDouble3Label.pack(padx=paddingX, pady=paddingY, side=LEFT)
        #
        # self.buttonDouble3Text = ttk.Entry(buttonDouble3Frame, width=20)
        # self.buttonDouble3Text.pack(padx=paddingX, pady=paddingY, side=RIGHT)
        # #self.actionText.bind("<KeyPress-Return>", self.__submitB1Motion)
        # #self.actionText.bind("<FocusOut>", self.__submitB1Motion)

    @property
    def guiObj(self):
        return self._guiObj

    @guiObj.setter
    def guiObj(self, value):
        if self._guiObj is not None:
            self.submitFields()
        self._guiObj = value
        self.resetFields()

    def resetFields(self):
        # clear fields
        self.textText.delete(0, END)
        self.xText.delete(0, END)
        self.yText.delete(0, END)
        self.widthText.delete(0, END)
        self.heightText.delete(0, END)
        self.actionText.delete(0, END)
        self.nameText.delete(0, END)

        # set fields
        self.textText.insert(END, self.guiObj.text)
        if "text" not in self.guiObj.tkType().keys():
            self.textText["state"] = DISABLED
            self.textText["background"] = "#F5F5F5"
        else:
            self.textText["state"] = ACTIVE
            self.textText["background"] = None
        self.typeVar.set(OptionsWindow.__getTypeName(self.guiObj.tkType))
        self.xText.insert(END, self.guiObj.x)
        self.yText.insert(END, self.guiObj.y)
        self.widthText.insert(END, self.guiObj.width)
        self.heightText.insert(END, self.guiObj.height)
        self.actionText.insert(END, self.guiObj.action)
        self.nameText.insert(END, self.guiObj.name)

    def submitFields(self):
        self.__submitWidth(None)
        self.__submitHeight(None)
        self.__submitXPos(None)
        self.__submitYPos(None)
        self.__submitText(None)
        self.__submitAction(None)
        self.__submitNameText(None)

    def moveObj(self, guiObj):
        '''informs the OptionsWindow that the given guiObj has moved. The window will update it's self if it's focused on that object'''
        if guiObj is self.guiObj:
            self.resetFields()

    def resizeObj(self, guiObj):
        '''informs the OptionsWindow that the given guiObj has resized. The window will update it's self if it's focused on that object'''
        if guiObj is self.guiObj:
            self.resetFields()

    def __submitWidth(self, event):
        try:
            width = int(self.widthText.get())
            self.guiObj.width = width
            self.widthText["foreground"] = self.normalColor
        except:
            self.widthText["foreground"] = self.errorColor
        return "break"  # stops the event from going onto the text widget. prevents new lines.

    def __submitHeight(self, event):
        try:
            height = int(self.heightText.get())
            self.guiObj.height = height
            self.heightText["foreground"] = self.normalColor
        except:
            self.heightText["foreground"] = self.errorColor
        return "break"

    def __submitXPos(self, event):
        try:
            self.guiObj.x = int(self.xText.get())
            self.xText["foreground"] = self.normalColor
        except:
            self.xText["foreground"] = self.errorColor
        return "break"

    def __submitYPos(self, event):
        try:
            self.guiObj.y = int(self.yText.get())
            self.yText["foreground"] = self.normalColor
        except:
            self.yText["foreground"] = self.errorColor
        return "break"

    def __submitText(self, event):
        newText = self.textText.get()
        self.guiObj.text = newText
        return "break"

    def __submitType(self, event):
        self.guiObj.tkType = WidgetTypeHelper.typeNames[self.typeVar.get()]
        self.resetFields()

    def __submitAction(self, event):
        self.guiObj.action = self.actionText.get()
        return "break"

    def __submitNameText(self, event):
        self.guiObj.name = self.nameText.get()
        return "break"

    def __getTypeName(tkType):
        '''find the name of the given tkType in the typeNames dict'''
        for key in WidgetTypeHelper.typeNames.keys():
            if WidgetTypeHelper.typeNames[key] == tkType:
                return key
        return None
