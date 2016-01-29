"""
    parser.py
    Written by Robert Bofinger

    This file makes use of the ast module. The ast module allows for the creation of abstract syntax trees
    from python source code. Creating an abstract syntax tree is one of the steps for compiling a python
    program. An abstract syntax tree is a tree of nodes where each node represents a logical piece of the
    code. We can create an abstract syntax tree and then traverse and analyze the nodes in order to get an
    understanding of what is going on in the program. What we are interested in for parsing gui object creation
    is looking for specific objects and the calls and assignments that configure them. We are mostly interested
    in the initialization() method and then tkinter/ttk calls and assignments in that method.

    The tree can be created by calling ast.parse(source) on source code.
    Normally you would continue and find the initialization function node using get_initialize(tree).
    From there you could get specific object names and find the method calls and assignments that involve them.
    Then you have the important information on the creation of the object and can hopefuly reconstruct it
    
"""

import ast
import astpp


class MethodCall:
    """Represents a method call
    Contains information on the object being called, arguments, keywords, and the method called
    """
    def __init__(self, object_name="", method_name="", args=[], keywords={}):
        self.object_name = object_name
        self.method_name = method_name
        self.args = args
        self.keywords = keywords


class Assignment:
    """
    Represents an assignment call
    Contains information on the values and objects being assigned
    """
    def __init__(self, object_name="", value=""):
        self.object_name = object_name
        self.value = value


class SubscriptAssignment(Assignment):
    """
    Represtents an assignment to a subscript
    ex: name["foo"] = "bar"
    """
    def __init__(self, subscript="", **kwargs):
        super(SubscriptAssignment, self).__init__(**kwargs)
        self.subscript = subscript


class AttributeAssignment(Assignment):
    """
    Represents an assignment to an attribute
    ex: name.foo = "bar"
    """
    def __init__(self, attribute="", **kwargs):
        super(AttributeAssignment, self).__init__(**kwargs)
        self.attribute = attribute

class ObjectInstantiation:
    """
    Represents an object instantiaion
    ex: object_name = Type(arg1, arg2, kwarg=value)
    """
    def __init__(self, object_name="", object_type="", args=[], keywords={}):
        self.object_name = object_name
        self.object_type = object_type
        self.args = args
        self.keywords = keywords
        

def get_initialize(tree):
    """Gets the initialization function in a tree and returns its node"""
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
    """returns all global variable names declared in a given function node"""
    found_globals = []
    for node in ast.walk(function_node):
        if isinstance(node, ast.Global):
            found_globals.extend(node.names)
    return found_globals


def get_root_instantiation(function_node):
    """gets the instantiation and assignment node for the 'root' tkinter window"""
    for node in ast.walk(function_node):
        if isinstance(node, ast.Assign):
            if isinstance(node.targets[0], ast.Name):
                if node.targets[0].id == 'root':
                    return node

                
def get_object_method_calls(function_node, object_name):
    """returns a dictionary of calls and MethodCalls objects. The dictionary structure is useful for quickly finding the methods you are interested in
    If multiple method calls with the same method name are found, only the last one will be included in the Dict
    
    k -> methodname
    v -> MethodCall
    """
    calls = {}
    for node in ast.walk(function_node):
        # These series of if's check that the node is an assignment node that
        # follows the pattern:
        # object_name.attribute(arg, otherarg, finalarg, keyword=keywordarg, keyword2=otherkeywordarg)
        if isinstance(node, ast.Expr):
            expression = node
            if isinstance(expression.value, ast.Call):
                  call = expression.value
                  if isinstance(call.func, ast.Attribute):
                      attribute = call.func # this is a type not the name of the attribute
                      if isinstance(attribute.value, ast.Name):
                          name = attribute.value
                          if name.id == object_name:
                              attr = attribute.attr # attr is the actual atribute name the name of the method called
                              raw_args = call.args
                              args = []
                              for arg in raw_args:
                                  args.append(convert_literal_node(arg))

                              keyword_args = {}
                              keywords = call.keywords
                              for keyword in keywords:
                                  key = keyword.arg
                                  raw_value = keyword.value
                                  value = convert_literal_node(raw_value)
                                  keyword_args[key] = value

                              call = MethodCall(object_name=object_name, method_name=attr, args=args, keywords=keyword_args)
                                  
                              calls[attr] = call                     
    return calls


def get_object_assignments(function_node, object_name):
    """returns a list of Assignment objects for the given object_name in the given function_node"""

    # This only supports simple assignments such as "name.attr = value" or "name[index] = value". Other
    # assignments will either throw an exception or not return the correct thing.
    # This code could be modified to allow for more robust statements but I kept it simple because the
    # code should already be formatted for these conditions.
    assignments = []
    for node in ast.walk(function_node):
        if isinstance(node, ast.Assign):
            assign = node
            if isinstance(assign.targets[0], ast.Subscript):
                subscript = assign.targets[0]
                if isinstance(subscript.value, ast.Name):
                    name = subscript.value.id # This is the ast.Name related to the object_name
                    if name == object_name:
                        subscript_value = convert_literal_node(subscript.slice.value)
                        value = convert_literal_node(assign.value)
                        new_assignment = SubscriptAssignment(object_name=object_name, subscript=subscript_value, value=value)
                        assignments.append(new_assignment)
            elif isinstance(assign.targets[0], ast.Attribute):
                attribute = assign.targets[0]
                if isinstance(attribute.value, ast.Name):
                    name = attribute.value.id # This is the ast.Name related to the object_name
                    if name == object_name:
                        attribute_name = attribute.attr
                        attribute_value = convert_literal_node(assign.value)
                        new_assignment = AttributeAssignment(object_name=object_name, attribute=attribute_name, value=attribute_value)
                        assignments.append(new_assignment)
    return assignments


def get_objects(function_node):
    """
    returns a list of ObjectInstantiaions in order from first to last instantiated
    """

    objects = []

    # This simply looks for an assignment statement that assigns a call to a Name to a target of a Name
    for node in ast.walk(function_node):
        if isinstance(node, ast.Assign):
            assign = node
            if isinstance(assign.targets[0], ast.Name):
                target = assign.targets[0]
                object_name = target.id
                if isinstance(assign.value, ast.Call):
                    call = assign.value
                    if isinstance(call.func, ast.Name):
                        name = call.func # This refers to the ast.Name node, not the name of the object
                        object_type = name.id

                        raw_args = call.args
                        args = []
                        for arg in raw_args:
                            args.append(convert_literal_node(arg))

                        keyword_args = {}
                        keywords = call.keywords
                        for keyword in keywords:
                            key = keyword.arg
                            raw_value = keyword.value
                            value = convert_literal_node(raw_value)
                            keyword_args[key] = value
                        
                        new_object = ObjectInstantiation(object_name=object_name, object_type=object_type, args=args, keywords=keyword_args)
                        objects.append(new_object)
    return objects


def convert_literal_node(node):
    """converts literal ast node values into the python value. Returns the original value if it cannot be converted"""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.Str):
        return node.s
    if isinstance(node, ast.Bytes):
        return node.s
    if isinstance(node, ast.List) or isinstance(node, ast.Tuple) or isinstance(node, ast.Set):
        result = []
        for sub_node in node.elts:
            result.append(convert_literal_node(sub_node))
        return result
    if isinstance(node, ast.Dict):
        raise NotImplemented("Dict literals are not yet implement in the parser")
        # see https://greentreesnakes.readthedocs.org/en/latest/nodes.html#Dict
    if isinstance(node, ast.Ellipsis):
        raise NotIMplemented("Ellipsis literals not implemented in the parser")
        # I'm not even sure what these are...
        # see https://greentreesnakes.readthedocs.org/en/latest/nodes.html#Ellipsis
    if isinstance(node, ast.NameConstant):
        return node.value
    return node

if __name__ == "__main__":
    # Test code
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

    initialize = get_initialize(tree)
    initialize_globals = get_globals(initialize)
    root_instantiation = get_root_instantiation(initialize)
    root_method_calls = get_object_method_calls(initialize, "root")
    button1_method_calls = get_object_method_calls(initialize, "button1")
    button1_assignments = get_object_assignments(initialize, "button1")
    objects = get_objects(initialize)

    astpp.parseprint(initialize)
    print()
    print(initialize_globals)
    if root_instantiation == None:
        print("Could not find root instantiation")
    else:
        print("Found root instantiation")
    print()
    print("Objects found:")
    for instantiation in objects:
        print()
        print("Name:", instantiation.object_name)
        print("Type:", instantiation.object_type)
        print("args:", instantiation.args)
        print("keywords:", instantiation.keywords)
    print()
    print("root method calls")
    for call_key in root_method_calls:
        call = root_method_calls[call_key]
        print()
        print("method_name:", call.method_name)
        print("args:", call.args)
        print("keywords:", call.keywords)
    print()
    print("button1 method calls")
    for call_key in button1_method_calls:
        call = button1_method_calls[call_key]
        print()
        print("method_name:", call.method_name)
        print("args:", call.args)
        print("keywords:", call.keywords)
    print()
    print("button1 assignments")
    for call in button1_assignments:
        if isinstance(call, SubscriptAssignment):
            print()
            print("subscript:", call.subscript)
            print("value:", call.value)
        else:
            print()
            print("attribute:", call.attribute)
            print("value:", call.value)

    #print(get_initialize(tree).name)

    #astpp.parseprint(source)

