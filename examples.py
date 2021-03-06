from tkinter import *
from tkinter.ttk import *

def set_text(widget, newtext):
    try:
        if (widget).__name__ == 'ScrolledList':
            # have to do this because ScrolledList may not have been included
            widget.listbox.delete(0,END)
            if isinstance(newtext, list):
                for string in newtext:
                    widget.listbox.insert(END,string)
            elif isinstance(newtext, str):
                for string in newtext.split('\n'):
                    widget.listbox.insert(END,string)

        elif type(widget).__name__ == 'ScrolledText':
            # have to do this because ScrolledText may not have been included
            widget.text.delete('1.0', END)
            widget.text.insert('1.0', newtext)
            widget.text.mark_set(INSERT, '1.0')
    except:
        pass

    if isinstance(widget, Text):
        widget.delete('1.0', END)
        widget.insert('1.0', newtext)

    elif isinstance(widget, Entry):
        widget.delete(0,END)
        widget.insert(0,newtext)

    elif isinstance(widget, Label):
        widget['text'] = newtext

    elif isinstance(widget, Button):
        widget.config(text=newtext)

    elif isinstance(widget, Checkbutton):
        widget.config(text=newtext)

    elif isinstance(widget, Scale):
        widget['label'] = newtext

    elif isinstance(widget, Listbox):
        widget.delete(0,END)
        if isinstance(newtext, list):
            for string in newtext:
                widget.insert(END,string)
        elif isinstance(newtext, str):
            for string in newtext.split('\n'):
                widget.insert(END,string)

        elif isinstance(widget, Menubutton):
            widget['text'] = newtext

def get_text(widget):
    try:
        if type(widget).__name__ == 'ScrolledList':
            return list(widget.listbox.get(0,END))

        elif type(widget).__name__ == 'ScrolledText':
            return widget.text.get('1.0', END+'-1c')
    except:
        pass

    if isinstance(widget, Text):
        return widget.get('1.0', END+'-1c')

    elif isinstance(widget, Entry):
        return widget.get()

    elif isinstance(widget, Label):
        return widget.cget('text')

    elif isinstance(widget, Button):
        return widget['text']

    elif isinstance(widget, Checkbutton):
        return widget.cget('text')

    elif isinstance(widget, Scale):
        return widget['label']

    elif isinstance(widget, Listbox):
        return list(widget.get(0,END))

    elif isinstance(widget, Menubutton):
        return widget['text']

def append_text(widget, newtext):
    current_text = get_text(widget)
    set_text(widget, current_text + newtext)

def popup(msg):
    box.showinfo('msg', msg)

def ask_for_string(prompt):
    return simpledialog.askstring('request for input', prompt)

def ask_for_yes_no(prompt):
    return box.askquestion('request for yes/no', prompt)

def get_selected(somelistbox):
    if isinstance(somelistbox, Listbox):
        try:
            return somelistbox.get(somelistbox.curselection()[0])
        except:
            return ''
    else:
        return somelistbox.getselected()

def initialize():
    global root, Label1, Button1, Checkbutton1, Entry1, Entry2, Entry3, Text1, Canvas1
    
    root = Tk()
    root.title("")
    root.geometry("325x500")
    
    Label1 = Label(root)
    Label1["text"] = "Example Widgets"
    Label1.place(x=103, y=5, width=97, height=35)
    
    Button1 = Button(root)
    Button1["text"] = "Click Me!"
    Button1.place(x=8, y=50, width=79, height=38)
    
    Checkbutton1 = Checkbutton(root)
    Checkbutton1["text"] = "Check Me"
    Checkbutton1["takefocus"] = True
    Checkbutton1.place(x=111, y=50, width=82, height=20)
    
    Entry1 = Entry(root)
    Entry1.insert(0, "Place Holder Text")
    Entry1["justify"] = "left"
    Entry1.place(x=200, y=75, width=100, height=20)
    
    Entry2 = Entry(root)
    Entry2.insert(0, "")
    Entry2["justify"] = "left"
    Entry2.place(x=200, y=50, width=100, height=21)
    
    Entry3 = Entry(root)
    Entry3.insert(0, "password")
    Entry3["justify"] = "left"
    Entry3.place(x=200, y=100, width=100, height=20)
    
    Text1 = Text(root)
    Text1.place(x=15, y=125, width=300, height=158)
    
    Canvas1 = Canvas(root, bg="red")
    Canvas1.place(x=15, y=300, width=300, height=175)
    
    root.mainloop()
initialize()
