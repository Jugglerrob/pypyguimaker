import tkinter as tk
import tkinter.ttk as ttk
import colors as colors
import re
import keyword
import builtins


update_time = 20


def any(name, alternates):
    "Return a named group pattern matching list of alternates."
    return "(?P<%s>" % name + "|".join(alternates) + ")"


def make_pat():
    kw = r"\b" + any("KEYWORD", keyword.kwlist) + r"\b"
    builtinlist = [str(name) for name in dir(builtins)
                                        if not name.startswith('_') and \
                                        name not in keyword.kwlist]
    # self.file = open("file") :
    # 1st 'file' colorized normal, 2nd as builtin, 3rd as string
    builtin = r"([^.'\"\\#]\b|^)" + any("BUILTIN", builtinlist) + r"\b"
    comment = any("COMMENT", [r"#[^\n]*"])
    stringprefix = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR|rb|rB|Rb|RB)?"
    sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
    dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
    dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
    string = any("STRING", [sq3string, dq3string, sqstring, dqstring])
    return kw + "|" + builtin + "|" + comment + "|" + string +\
           "|" + any("SYNC", [r"\n"])


prog = re.compile(make_pat(), re.S)
idprog = re.compile(r"\s+(\w+)", re.S)


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
        self.LoadTagDefs()
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

        return ln

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
        self.colorize()
        self.text.after(update_time, self.update_loop)

    def LoadTagDefs(self):
        #theme = idleConf.GetOption('main','Theme','name')
        self.tagdefs = {
            "COMMENT": {'background': "#ffffff", 'foreground': "#dd0000"},
            "KEYWORD": {'background': "#ffffff", 'foreground': "#ff7700"},
            "BUILTIN": {'background': "#ffffff", 'foreground': "#900090"},
            "STRING": {'background': "#ffffff", 'foreground': "#00aa00"},
            "DEFINITION": {'background': "#ffffff", 'foreground': "#0000ff"},
            "SYNC": {'background':None,'foreground':None},
            "TODO": {'background':None,'foreground':None},
            "ERROR": {'background': "#ff7777", 'foreground': "#000000"},
            # The following is used by ReplaceDialog:
            "hit": {'background': "black", 'foreground': "white"},
            }

        for tag in self.tagdefs:
            self.text.tag_config(tag, background=self.tagdefs[tag]["background"])
            self.text.tag_config(tag, foreground=self.tagdefs[tag]["foreground"])


    # This is taken from Python 3.5\Lib\idlelib\ColorDelegator.py
    def colorize(self):
        """
        Scan the text area and add color based on python syntax
        """
        self.text.tag_add("TODO", "1.0", tk.END)
        next = "1.0"
        while True:
            item = self.text.tag_nextrange("TODO", next)
            if not item:
                break
            head, tail = item
            self.text.tag_remove("SYNC", head, tail)
            item = self.text.tag_prevrange("SYNC", head)
            if item:
                head = item[1]
            else:
                head = "1.0"

            chars = ""
            next = head
            lines_to_get = 1
            ok = False
            while not ok:
                mark = next
                next = self.text.index(mark + "+%d lines linestart" % lines_to_get)
                #print("start: %s, end: %s" % (mark, next))
                lines_to_get = min(lines_to_get * 2, 100)
                ok = "SYNC" in self.text.tag_names(next + "-1c")
                line = self.text.get(mark, next)
                if not line:
                    #print("Line is empty, returning")
                    return
                for tag in self.tagdefs:
                    self.text.tag_remove(tag, mark, next)
                chars = chars + line
                #print(chars)
                m = prog.search(chars)
                while m:
                    for key, value in m.groupdict().items():
                        if value:
                            a, b = m.span(key)
                            #print("Found: " + str(key) + " " + value + " at " + str(a) + " to " + str(b))
                            self.text.tag_add(key,
                                         head + "+%dc" % a,
                                         head + "+%dc" % b)
                            if value in ("def", "class"):
                                m1 = idprog.match(chars, b)
                                if m1:
                                    a, b = m1.span(1)
                                    self.text.tag_add("DEFINITION",
                                                      head + "+%dc" % a,
                                                      head + "+%dc" % b)
                    m = prog.search(chars, m.end())
                if "SYNC" in self.text.tag_names(next + "-1c"):
                    head = next
                    chars = ""
                else:
                    ok = False
                if not ok:
                    # We're in an inconsistent state, and the call to
                    # update may tell us to stop.  It may also change
                    # the correct value for "next" (since this is a
                    # line.col string, not a true mark).  So leave a
                    # crumb telling the next invocation to resume here
                    # in case update tells us to leave.
                    self.text.tag_add("TODO", next)
                #self.update()
                #if self.stop_colorizing:
                #    if DEBUG: print("colorizing stopped")
                #    return


if __name__ == "__main__":
    root = tk.Tk()
    CodeEditor(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
