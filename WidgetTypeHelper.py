from tkinter import *


class WidgetTypeHelper:
    '''A class that provides methods to help with getting tkinter widget types'''
    # a list of abailable widget types
    typeNames = {"Button": Button,
                 "Label": Label,
                 "Text": Text,
                 "Entry": Entry,
                 "Check Button": Checkbutton,
                 "Radio Button": Radiobutton,
                 "Scroll Bar": Scrollbar
                 }

    @classmethod
    def convertToType(cls, stringType):
        if stringType in cls.typeNames.keys():
            return cls.typeNames[stringType]
        for value in cls.typeNames.values():
            if value.__name__ == stringType:
                return value
        return None