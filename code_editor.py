import tkinter as tk
import tkinter.ttk as ttk
import colors as colors

class CodeEditor(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent)
        
        self.lineNumbers = ""
        self.linenums_text = tk.Text(self,
                                     width=4,
                                     takefocus=0,
                                     highlightthickness = 0,
                                     bd = 0,
                                     background = colors.white_primary,
                                     foreground = colors.lightblue_primary,
                                     state='disabled')
        self.linenums_text.pack(side=tk.LEFT, fill="y", padx=4)
        self.text = tk.Text(self, undo=True, highlightthickness = 0, bd = 0)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.update_loop()

    # This method is taken from http://tkinter.unpythonic.net/wiki/A_Text_Widget_with_Line_Numbers
    def getLineNumbers(self):
        x = 0
        line = '0'
        col= ''
        ln = ''
        
        # assume each line is at least 6 pixels high
        step = 6
        
        nl = '\n'
        lineMask = '    %s\n'
        indexMask = '@0,%d'
        
        for i in range(0, self.text.winfo_height(), step):
            
            ll, cc = self.text.index( indexMask % i).split('.')

            if line == ll:
                if col != cc:
                    col = cc
                    ln += nl
            else:
                line, col = ll, cc
                ln += (lineMask % line)[-5:]


    # This method is taken from http://tkinter.unpythonic.net/wiki/A_Text_Widget_with_Line_Numbers
    def updateLineNumbers(self):
        tt = self.linenums_text
        ln = self.getLineNumbers()
        if self.lineNumbers != ln:
            self.lineNumbers = ln
            tt.config(state="normal")
            tt.delete("1.0", tk.END)
            tt.insert("1.0", self.lineNumbers)
            tt.config(state="disabled")


    def update_loop(self):
        self.updateLineNumbers()
        self.text.after(50, self.update_loop)


    def 


if __name__ == "__main__":
    root = tk.Tk()
    CodeEditor(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
