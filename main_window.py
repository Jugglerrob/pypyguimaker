import GUIObj
import guiparser
import tkinter as tk
import tkinter.ttk as ttk
import colors

gui_objects = []

def initialize():
    root = tk.Tk()
    root.configure(background=colors.background)
    mainCanvas = tk.Canvas(root, bg=colors.white_primary)
    mainCanvas.pack()
    root.mainloop()

def load(self, filename):
    """
    loads the file with the given filename
    """
    pass

def load_initialize(self, file):
    """
    loads the guiobjs from the initialization function in the given file
    """
    tree = guiparser.get_tree(source)
    
initialize()
        
