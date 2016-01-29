import tkinter as tk
import tkinter.ttk as ttk

class EditWindow:
    def __init__(self, parent):
        top = self.top = tk.Tk()
        top.title("PyPy Guimaker Extra Module Code")
        #top.geometry("1080x720")

        self.textarea = tk.Text(top)
        self.textarea.pack(padx=5)
        self.textarea.insert(tk.END, parent.extra_code)

        okB = ttk.Button(top, text="OK", command=self.ok)
        okB.pack(pady=5)
        cancelB = ttk.Button(top, text="Cancel", command=self.destroy)
        cancelB.pack(pady=5)
        self.parent = parent
        self.textarea.focus()

    def ok(self):
        retvalue = self.textarea.get('1.0',tk.END+'-1c')
        self.parent.extra_code = retvalue
        self.top.destroy()

    def destroy(self):
        self.top.destroy()


