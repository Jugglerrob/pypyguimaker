"""
styles.py

This fyle contains the custom ttk styles that are used by the widgets in this program.
Initialize() should be called immediately after when the main window is created.
"""

import tkinter.ttk as ttk
import colors

def initialize():
    # To have a disabled entry looked like an enabled entry we must make an entire new style
    # style code grabbed from: http://stackoverflow.com/a/17639955
    style = ttk.Style()

    style.configure('TFrame', background=colors.white_primary)
    style.configure('BackgroundFrame.TFrame', background=colors.background)
    style.configure('LightBluePrimaryNavLabel.TLabel', foreground=colors.background, background=colors.lightblue_primary)
    style.configure('WhiteDisabledNavLabel.TLabel', background=colors.white_disabled)
    style.configure('LightBluePrimaryFrame.TFrame', background=colors.lightblue_primary)
    
    style.element_create("plain.field", "from", "clam")
    style.layout("EntryStyle.TEntry",
                       [('Entry.plain.field', {'children': [(
                           'Entry.background', {'children': [(
                               'Entry.padding', {'children': [(
                                   'Entry.textarea', {'sticky': 'nswe'})],
                          'sticky': 'nswe'})], 'sticky': 'nswe'})],
                          'border':'2', 'sticky': 'nswe'})])
    style.configure("EntryStyle.TEntry",
                     background=colors.white_primary, # this is actually the background behind the whole widget
                     fieldbackground="white") # this is the background behind the text
    # end copied style code
    style.map("EntryStyle.TEntry",
              foreground = [("disabled", "black") ] # requried to make the text appear black instead of disabled
              )    

    # This style removes the focus indicator. When clicking it won't place a dashed line around the label
    # There would appear to be no way to disabled the hover color
    # One idea would be to create the checkbutton as a label but then it is not possible to set the check on or off
    style.layout('CheckbuttonStyle.Checkbutton',
                    [('Checkbutton.padding', {'sticky': 'nswe', 'children':
                        [('Checkbutton.indicator', {'sticky': '', 'side': 'left'}),
                         ('Checkbutton.label', {'sticky': 'nswe'})],               
                        'side': 'left'})]
                 )

    
