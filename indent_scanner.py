import re

# The regexes in this file are taken from Python3.5\Lib\idlelib\PyParse.py
# This file is inspired by PyParse.py

class IndentScanner:
    def __init__(self, text):
        self.text = text
        self.lines = []
        self._load_lines(text)
    def _load_lines(self, text):
        for line in self.text.splitlines():
            self.lines.append(line)

    def get_new_indentation(self, index):
        """gets new indentation for a line based on previous lines"""
        # This works backwards to find the last non-comment line.
        # Once the non-comment line is found, use the context of that line to find the new indent.
        if index == 0:
            # The first line is allways indented at 0
            return 0
        i = index-1
        while i > 0:
            if match_comment(self.get_line(i)):
                i -= 1
            else:
                break
        line = self.get_line(i)
        if match_open_string("\n".join(self.lines[0:i+1])):
            # if the string is open then we let the indent level be 0
            return 0
        # We have to keep looking backwards for the last line that was not the end of a string
        # This can be done by removing the last line and checking if there is now an open string
        while i > 1:
            if match_open_string("\n".join(self.lines[0:i])):
                i -= 1
            else:
                break
        line = self.get_line(i)
        # now the index is gauranteed to be at a useful spot.
        if match_opener(line):
            # openers cause an indent level to be added
            return self.get_line_indent(i) + 4
        elif match_closer(line):
            # closers cause an indent level to be removed
            indent = self.get_line_indent(i)
            if indent >= 4:
                return indent - 4
            else:
                return 0
        # The last line was just a normal statement
        return self.get_line_indent(i)

    def get_line(self, index):
        return self.lines[index]

    def get_line_indent(self, index):
        line = self.get_line(index)
        return len(line) - len(line.lstrip(' '))

def match_comment(line):
    """returns True if line is a comment"""
    line = line.lstrip(' ')
    return line.startswith("#")

def match_opener(line):
    """return True if opening an indent block"""
    line = line.strip(' ')
    synchre = re.compile(r"""
        ^
        [ \t]*
        (?: while
        |   if
        |   else
        |   def
        |   return
        |   assert
        |   break
        |   class
        |   continue
        |   elif
        |   try
        |   except
        |   raise
        |   import
        |   yield
        )
        \b
    """, re.VERBOSE | re.MULTILINE).search
    is_opener = bool(synchre(line))
    return is_opener and line.endswith(':')

def match_junk(line):
    """returns True if line is comment or empty"""
    line = line.lstrip(' ')
    return line.startswith("#") or len(line) == 0

def match_closer(line):
    """returns True if closing an indent block"""
    line = line.lstrip(' ')
    closere = re.compile(r"""
        \s*
        (?: return
        |   break
        |   continue
        |   raise
        |   pass
        )
        \b
    """, re.VERBOSE).match
    return bool(closere(line))


def match_open_string(text):
    """returns True if a multiline string is opened and NOT closed"""
    quotes = ["'", '"']
    for quote in quotes:
        state = "ENTER"
        for char in text:
            if state == "ENTER":
                if char == quote:
                    state = "FIRST_OPEN_QUOTE"
                    continue
                elif char == '\\':
                    state = "OPENING_ESCAPED_CHAR"
                    continue
                elif char == '#':
                    state = "COMMENT"
                    continue
                else:
                    state = "ENTER"
                    continue
            elif state == "COMMENT":
                if char == '\n':
                    state = "ENTER"
                    continue
                else:
                    state = "COMMENT"
                    continue
            elif state == "FIRST_OPEN_QUOTE":
                if char == quote:
                    state = "SECOND_OPEN_QUOTE"
                    continue
                elif char == '\\':
                    state = "OPENING_ESCAPED_CHAR"
                    continue
                else:
                    state = "ENTER"
                    continue
            elif state == "SECOND_OPEN_QUOTE":
                if char == quote:
                    state = "INNER_QUOTE"
                    continue
                if char == '\\':
                    state = "OPENING_ESCAPED_CHAR"
                    continue
                if char == '#':
                    state = "COMMENT"
                    continue
                else:
                    state = "ENTER"
                    continue
            elif state == "OPENING_ESCAPED_CHAR":
                state = "ENTER"
                continue
            elif state == "INNER_QUOTE":
                if char == quote:
                    state = "FIRST_ENDING_QUOTE"
                    continue
                elif char == '\\':
                    state = "INNER_QUOTE_ESCAPED_CHAR"
                    continue
                else:
                    state = "INNER_QUOTE"
                    continue
            elif state == "INNER_QUOTE_ESCAPED_CHAR":
                state = "INNER_QUOTE"
                continue
            elif state == "FIRST_ENDING_QUOTE":
                if char == quote:
                    state = "SECOND_ENDING_QUOTE"
                    continue
                elif char == '\\':
                    state = "INNER_QUOTE_ESCAPED_CHAR"
                    continue
                else:
                    state = "INNER_QUOTE"
                    continue
            elif state == "SECOND_ENDING_QUOTE":
                if char == quote:
                    state = "ENTER"
                    continue
                if char == '\\':
                    state = "INNER_QUOTE_ESCAPED_CHAR"
                    continue
                else:
                    state = "INNER_QUOTE"
                    continue
        if state in ("INNER_QUOTE", "FIRST_ENDING_QUOTE", "SECOND_ENDING_QUOTE", "INNER_QUOTE_ESCAPED_CHAR"):
            return True
    return False
            
