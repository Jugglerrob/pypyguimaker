from tkinter import *
from tkinter.ttk import *

def initialize():
    """generated by pypyguimaker. creates the tkinter window"""
    global randName959606, randName951894
    root = Tk()
    root.geometry('500x500')
    root.title('Python application')

    randName959606 = Button(root, command=lambda:bar())
    randName959606['text'] = 'DEFAULT'
    randName959606.place(x=50, y=50, width=100, height=200)

    randName951894 = Button(root, command=bar)
    randName951894['text'] = 'DEFAULT'
    randName951894.place(x=175, y=100, width=200, height=100)

    randLabel = Label(root)
    randLabel['text'] = "I'M A LABEL :D"
    randLabel.place(x=10, y=10, width=85, height=20)

    root.mainloop()

def bar(event=None):
    pass

initialize()
