import ast
import astpp

source = """
from tkinter import *

def foo():
    print("some stuff")

def bar():
    print("Some other stuff")

def initialize():
    global button1, label5

    root = Tk()
    root.geometry('500x500')
    root.tile('Python application')
    
    button1 = Button(root, command=bar)
    button1["text"] = "foo button"
    button1.somethingstupid = 123
    button1.place(x=50, y=50, width=100, height=200)

    label5 = Label(root)
    label5['text'] = 'LABEL LABEL LABEL'
    label4.place(x=175, y=100, width=200, height=100)

    root.mainloop()

def foobar():
    print("So neat")
"""

tree = ast.parse(source)

def get_initialize(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "initialize":
                # check that there are no arguments
                if (len(node.args.args) == 0 and
                    len(node.args.kwonlyargs) == 0 and
                    len(node.args.kw_defaults) == 0 and
                    len(node.args.defaults) == 0 and
                    node.args.vararg is None and
                    node.args.kwarg is None
                    ): 
                    return node
                else:
                    raise Exception("Initialization function may not contain arguments")

def get_globals(function_node):
    found_globals = []
    for node in ast.walk(function_node):
        if isinstance(node, ast.Global):
            found_globals.extend(node.names)
    return found_globals

def get_root_instantiation(function_node):
    for node in ast.walk(function_node):
        if isinstance(node, ast.Assign):
            if isinstance(node.targets[0], ast.Name):
                if node.targets[0].id == 'root':
                    return node
                
def get_root_settings(function_node):
    settings = {}
    for node in ast.walk(function_node):
        if isinstance(node, ast.Expr):
            

initialize = get_initialize(tree)
initialize_globals = get_globals(initialize)
root_instantiation = get_root_instantiation(initialize)
astpp.parseprint(initialize)
print()
print(initialize_globals)
if root_instantiation == None:
    print("Could not find root instantiation")
else:
    print("Found root instantiation")

#print(get_initialize(tree).name)

#astpp.parseprint(source)
