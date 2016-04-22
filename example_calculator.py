from tkinter import *
from tkinter.ttk import *

first_value = 0
second_value = 0
operator = None
current_value = 0

def display_value(value):
    Entry1.delete(0, 'end')
    Entry1.insert(0, str(value))

def press_1():
    global current_value
    current_value = current_value * 10 + 1    
    display_value(current_value)
    
def press_2():
    global current_value
    current_value = current_value * 10 + 2
    display_value(current_value)
    
def press_3():
    global current_value
    current_value = current_value * 10 + 3    
    display_value(current_value)
    
def press_4():
    global current_value
    current_value = current_value * 10 + 4 
    display_value(current_value)

def press_5():
    global current_value
    current_value = current_value * 10 + 5  
    display_value(current_value)

def press_6():
    global current_value
    current_value = current_value * 10 + 6  
    display_value(current_value)

def press_7():
    global current_value
    current_value = current_value * 10 + 7
    display_value(current_value)

def press_8():
    global current_value
    current_value = current_value * 10 + 8    
    display_value(current_value)

def press_9():
    global current_value
    current_value = current_value * 10 + 9  
    display_value(current_value)

def press_0():
    global current_value
    current_value = current_value * 10   
    display_value(current_value)

def calculate():
    if operator is not None:
        if operator = "+":
            current_value = first_value + current_value
        if operator = "-":
            current_value = first_value - current_value
        if operator = "/":
            current_value = first_value / current_value
        if operator = "*":
            current_value = first_value * current_value

def press_add():
    global operator, first_value, current_value
    if operator is None:
        operator = "+"
        first_value = current_value
        current_value = 0
    else:
            current_value = 
    

def press_subtract():
    global operator, first_value, current_value
    operator = "-"

def press_multiply():
    global operator, first_value, current_value
    operator = "*"

def press_divide():
    global operator, first_value, current_value
    operator = "/"
    
def initialize():
    global Entry1
    
    root = Tk()
    root.title("Python application")
    root.geometry("500x500")
    
    Label1 = Label(root)
    Label1["text"] = "Calculator"
    Label1.place(x=214, y=17, width=62, height=20)
    
    Button1 = Button(root, command=press_7)
    Button1["text"] = "7"
    Button1.place(x=90, y=75, width=50, height=50)
    
    Button2 = Button(root, command=press_8)
    Button2["text"] = "8"
    Button2.place(x=155, y=75, width=50, height=50)
    
    Button3 = Button(root, command=press_9)
    Button3["text"] = "9"
    Button3.place(x=220, y=75, width=50, height=50)
    
    Button4 = Button(root, command=press_4)
    Button4["text"] = "4"
    Button4.place(x=90, y=140, width=50, height=50)
    
    Button5 = Button(root, command=press_5)
    Button5["text"] = "5"
    Button5.place(x=155, y=140, width=50, height=50)
    
    Button6 = Button(root, command=press_6)
    Button6["text"] = "6"
    Button6.place(x=220, y=140, width=50, height=50)
    
    Button7 = Button(root, command=press_1)
    Button7["text"] = "1"
    Button7.place(x=90, y=205, width=50, height=50)
    
    Button8 = Button(root, command=press_2)
    Button8["text"] = "2"
    Button8.place(x=155, y=205, width=50, height=50)
    
    Button10 = Button(root)
    Button10["text"] = "/"
    Button10.place(x=285, y=75, width=50, height=50)
    
    Button11 = Button(root)
    Button11["text"] = "-"
    Button11.place(x=285, y=140, width=50, height=50)
    
    Button12 = Button(root)
    Button12["text"] = "*"
    Button12.place(x=350, y=75, width=50, height=50)
    
    Button13 = Button(root)
    Button13["text"] = "+"
    Button13.place(x=350, y=140, width=50, height=50)
    
    Button14 = Button(root, command=press_0)
    Button14["text"] = "0"
    Button14.place(x=90, y=270, width=180, height=50)
    
    Button15 = Button(root)
    Button15["text"] = "calculate"
    Button15.place(x=285, y=205, width=115, height=115)
    
    Entry1 = Entry(root)
    Entry1.insert(0, "")
    Entry1["justify"] = "left"
    Entry1.place(x=95, y=43, width=299, height=21)
    
    Button9 = Button(root, command=press_3)
    Button9["text"] = "3"
    Button9.place(x=220, y=205, width=50, height=50)
    
    root.mainloop()
initialize()
