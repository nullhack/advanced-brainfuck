"""This module contains all classes and functions to run BrainFuck commands.

    Examples:

        >>> bf = BrainFuck()
        >>> bf.execute('++++++++++++++++++++++++++++++++++++++++++++++++++.')
        2
        >>> bf.execute('*')
        |50|
        >>> bf.execute('{toint}*')
        importing: bflib/toint.bf
        |2|
        >>> bf.execute('&')
        102 ++++++++++++++++++++++++++++++++++++++++++++++++++.*------------------------------------------------*&
        >>> BrainFuck.is_balanced('[[-][-][][{sum}+++.>]]')
        True
        >>> BrainFuck.is_balanced('[.[>>>[+++{sum]<<+++.]*]')
        False
        >>> BrainFuck.is_balanced('[.[>>>[+++[{sum}<<+++.]*]')
        False

"""

from __future__ import print_function
import os
import re
import sys
import argparse
import itertools

help_text =  """
BrainFuck Commands

    >         increment the data pointer.
    <         decrement the data pointer.
    +         increment the value at the data pointer.
    -         decrement the value at the data pointer.
    .         output the value at the data pointer.
    ,         accept one integer of inputer.
    [         jump if value is false.
    ]         continue if value is true.

Additional Commands

    {LIB}         import external brainfuck code to current process.
    *             output all the cells.
    &             output command history.
    help          show this help message."""

class BrainFuck:
    """BrainFuck language specification.

    This class implements all commands of the BrainFuck language and
    some advanced functions.

    This class also implements a full featured interpreter.

    You can run from python code or shell.

    Attributes:
        cells (Cells): Advanced structure to handle the language registers.
        pointer (int): Pointer to current cell position.
        cmd_history (str): String containing all the commands executed so far.
        _cmd_pointer (int): Pointer to current command to be executed.
        _jump (dict): A dict to handle last line of commands jump table.

    """

    def __init__(self):
        self.cells = Cells()
        self.pointer = 0
        self.cmd_history = ''
        self._cmd_pointer = 0
        self._jump = {}

    def _print_value(self):
        """Print current cell value.

        Note:
            If the value is 0, a new line is printed.
            If the value in ASCII table, It's printed as a char.
            Else, the value is printed as integer.
        """
        value = self.cells[self.pointer]
        if not value: print()
        elif value>0 and value<256: print(chr(value), end="")
        else: print(value, end="")

    def _read_value(self):
        """Read a value from input into current cell.

        Note:
            Executes until a valid input is read or a blank line inserted.
            
        """
        while True:
            ui = input('<< ')
            if not ui: break
            try:
                self.cells[self.pointer] = int(ui)
                break
            except:
                pass
            try:
                self.cells[self.pointer] = ord(ui)
                break
            except:
                print("Invalid value! Please try again:")

    def _move_right(self):
        """Execute '>' command by increasing pointer by 1."""
        self.pointer += 1

    def _move_left(self):
        """Execute '<' command by decreasing pointer by 1."""
        self.pointer -= 1

    def _add(self):
        """Execute '+' command by increasing cell by 1."""
        self.cells[self.pointer] += 1

    def _sub(self):
        """Execute '-' command by decreasing cell by 1."""
        self.cells[self.pointer] -= 1

    def _open_brackets(self):
        """Execute '[' command using _jump."""
        if not self.cells[self.pointer]:
            self._cmd_pointer = self._jump[self._cmd_pointer]

    def _close_brackets(self):
        """Execute ']' command using _jump."""
        if self.cells[self.pointer]:
            self._cmd_pointer = self._jump[self._cmd_pointer]

    def print_cells(self):
        """Print all cells."""
        print(self.cells.print_pos(self.pointer))

    def print_cmd_history(self):
        """Print all the commands executed so far."""
        print(len(self.cmd_history), self.cmd_history)

    @staticmethod
    def is_balanced(cmd_line):
        """Check if a given command line is balanced or not.

        Args:
            cmd_line: The line to be verified.

        Returns:
            True if cmd_line is balanced (False if not).

        """
        brackets = {'[':']','{':'}'}
        stack = []
        for cmd in cmd_line:
            d = brackets.get(cmd, None)
            if d: stack.append(d)
            elif cmd in brackets.values():
                if not stack or cmd != stack.pop():
                    return False
        return not stack

    @staticmethod
    def import_lib(cmds):
        """Import a set of external codes.

        Args:
            cmds: A line with one or more libs to import.

        Returns:
            import_dict (dict): A dictionary containing all the lib code.

        Raises:
            Exception: If could not import some of the external code.

        """
        BASE_LIB = 'bflib'
        BASE_DIR = os.path.join(os.path.dirname(__file__))
        EXT = ['.bf', '']
        import_dict = {}
        import_list = re.findall('\{([a-zA-Z0-9_\.\-\/]+)\}', cmds)
        path_ext = list(itertools.product([BASE_LIB, BASE_DIR], EXT))
        for lib in import_list:
            lib_path = ''
            for base, ext in path_ext:
                vpath = os.path.join(base, '{}{}'.format(lib, ext))
                if os.path.isfile(vpath):
                    lib_path = vpath
            if not lib_path:
                raise Exception('Could not import: {}'.format(lib))
            with open(lib_path) as flib:
                print('importing:', lib_path)
                bf = BrainFuck()
                istr = ''.join(flib.readlines())
                bf.execute(istr)
                import_dict[lib] = bf.cmd_history
        return import_dict

    def execute(self, cmd_line, MAX_RECURSION=10**5):
        """Execute a set of  BrainFuck commands.

        Args:
            cmd_line (str): A line with BrainFuck commands.
            MAX_RECURSION (Optional[float]): Max number of commands allowed
            to execute in current line of commands.

        Raises:
            Exception: If brackets are not balanced.

        """
        if not self.is_balanced(cmd_line):
            raise Exception("brackets not balanced!")

        cmds = {
            #BrainFuck commands
            '.':self._print_value,
            ',':self._read_value,
            '>':self._move_right,
            '<':self._move_left,
            '+':self._add,
            '-':self._sub,
            '[':self._open_brackets,
            ']':self._close_brackets,
            #Additional commands
            '*':self.print_cells,
            '&':self.print_cmd_history,
            }

        backup_history = self.cmd_history
        backup_cells = self.cells.backup()

        try: 
            import_dict = self.import_lib(cmd_line)
            for key, value in import_dict.items():
                cmd_line = cmd_line.replace('{{{}}}'.format(key), value)
        except Exception as e:
            cmd_line = ''
            print(e)

        #Clean the input, keeping only valid commands
        cmd_line = [c for c in cmd_line if c in cmds]

        #Prepare jump table
        pos = len(self.cmd_history)
        stack = []
        for cmd in cmd_line:
            self.cmd_history += cmd
            if cmd=='[':
                stack.append(pos)
            elif cmd==']':
                self._jump[pos] = stack.pop()
                self._jump[self._jump[pos]] = pos
            pos+=1

        #Execute commands, keeping track of num_commands executed
        rec_depth = 0
        while self._cmd_pointer<len(self.cmd_history):
            rec_depth += 1
            if rec_depth < MAX_RECURSION:
                cmds[self.cmd_history[self._cmd_pointer]]()
                self._cmd_pointer += 1
            else:
                print('MAX recursion reached!')
                self.cmd_history = backup_history
                self._cmd_pointer = len(backup_history)
                self.cells = backup_cells
                break

    def interpreter(self, MAX_RECURSION=10**5):
        """Run the Interpreter.

        Args:
            MAX_RECURSION (Optional[float]): Max number of commands allowed
            to execute in current line of commands.

        """
        while True:
            cmd_line = input('>> ')
            while not self.is_balanced(cmd_line):
                tmp = input('.. ')
                cmd_line = cmd_line+tmp if tmp else 'skip'
            if cmd_line=='help': print(help_text)
            elif not cmd_line: break
            else: self.execute(cmd_line, MAX_RECURSION)

class Cells(dict):
    """Modifies a dict to act like a list and save space."""

    def __init__(self, **kwargs):
        super(Cells, self).__init__(**kwargs)

    def __getitem__(self, key):
        """Return 0 if key is not defined"""
        if key in self:
            return super(Cells, self).__getitem__(key)
        return 0

    def __setitem__(self, key, value):
        """Delete cells with value 0 to save space."""
        super(Cells, self).__setitem__(key, value)
        if not value: del self[key]

    def backup(self):
        """Return a copy of the cells."""
        cls = self.__class__
        new_cells = cls.__new__(cls)
        for key, value in self.items():
            new_cells[key] = value
        return new_cells

    def print_pos(self, pos):
        """Print all the cells and the pointer."""
        if self: m, M = min(min(self), pos), max(max(self), pos)
        else: m = M = pos
        print_list = [0 for _ in range(m, M+1)]
        for key,value in self.items():
            print_list[key-m] = value
        print_list[pos-m] = '|{}|'.format(print_list[pos-m])
        return ' '.join(map(str, print_list))

def main(args=[]):
    """Config parser and run command line options."""
    #Configure argparser
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        'cmd',
        nargs='?',
        default='',
        type=str,
        help='brainFuck commands',
    )
    arg_parser.add_argument(
        '-r', '--recursion',
        default=10**5,
        type=int,
        metavar='MAX_RECURSION',
        help='set MAX_RECURSION value',
    )
    arg_parser.add_argument(
        '-c', '--command-line',
        action='store_true',
        help='do not initialize shell, running commands from arguments only',
    )
    arguments = arg_parser.parse_args(args)

    #Execute input and run the interpreter
    bf = BrainFuck()
    bf.execute(arguments.cmd, arguments.recursion)
    if not arguments.command_line:
        bf.interpreter(arguments.recursion)

if __name__=="__main__":
    main(sys.argv[1:])
