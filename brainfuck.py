import re
import sys
import argparse

class BrainFuck:

    def __init__(self):
        self.cells = Cells()
        self.pointer = 0
        self.cmd_history = ''
        self._cmd_pointer = 0
        self._jump = {}

    def _print_value(self):
        print(self.cells[self.pointer])

    def _read_value(self):
        while True:
            try:
                ui = int(input('<< '))
                self.cells[self.pointer] = ui
            except:
                print("Invalid integer!")
                continue
            else:
                break

    def _move_right(self):
        self.pointer += 1

    def _move_left(self):
        self.pointer -= 1

    def _add(self):
        self.cells[self.pointer] += 1

    def _sub(self):
        self.cells[self.pointer] -= 1

    def _open_brackets(self):
        if not self.cells[self.pointer]:
            self._cmd_pointer = self._jump[self._cmd_pointer]

    def _close_brackets(self):
        if self.cells[self.pointer]:
            self._cmd_pointer = self._jump[self._cmd_pointer]

    def print_cells(self):
        print(self.cells.print_pos(self.pointer))

    def print_cmd_history(self):
        print(self._cmd_pointer, self.cmd_history)

    @staticmethod
    def is_balanced(cmd_line):
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
    def import_lib(cmd_line):        
        import_list = re.findall('{([a-zA-Z0-9_\-\/]+)\}', cmd_line)
        import_dict = {}
        for lib in import_list:
            try:
                with open('{}.bf'.format(lib)) as flib:
                    bf = BrainFuck()
                    istr = ''.join(flib.readlines())
                    bf.execute(istr)
                    import_dict[lib] = bf.cmd_history
                print('importing:', lib)
            except:
                import_dict[lib] = ''
                print('Could not import: ', lib)
        return import_dict

    def execute(self, cmd_line):
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
        pos = len(self.cmd_history)
        stack = []
        try:
            import_dict = self.import_lib(cmd_line)
            cmd_line = cmd_line.format(**import_dict)
        except:
            print("Lib must be an string without dots, numbers or extensions")
            cmd_line = ''
        #clean the input, keeping only valid commands
        cmd_line = [c for c in cmd_line if c in cmds]
        for cmd in cmd_line:
            self.cmd_history += cmd
            if cmd=='[':
                stack.append(pos)
            elif cmd==']':
                self._jump[pos] = stack.pop()
                self._jump[self._jump[pos]] = pos
            pos+=1
        while self._cmd_pointer<len(self.cmd_history):
            cmds[self.cmd_history[self._cmd_pointer]]()
            self._cmd_pointer += 1

    def interpreter(self):
        while True:
            cmd_line = input('>> ')
            while not self.is_balanced(cmd_line):
                tmp = input('.. ')
                cmd_line = cmd_line+tmp if tmp else 'skip'
            if cmd_line=='help':
                print(help_text)
            elif not cmd_line: break
            else:
                self.execute(cmd_line)

class Cells(dict):
    def __init__(self, **kwargs):
        self[0]=0
        super(Cells, self).__init__(**kwargs)

    def __getitem__(self, key):
        if key in self:
            return super(Cells, self).__getitem__(key)
        return 0

    def print_pos(self, pos):
        k = [v for v in self.keys()]+[pos]
        m = min(k)
        M = max(k)
        print_list = [0 for _ in range(m, M+1)]
        for key,value in self.items():
            print_list[key-m] = value
        print_list[pos-m] = '|{}|'.format(print_list[pos-m])
        return ' '.join(map(str, print_list))

help_text = """
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


def main():
    #Configure argparser
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        'cmd',
        nargs='?',
        default='',
        type=str,
        help='BrainFuck commands',
    )

    arg_parser.add_argument(
        '-s', '--shell',
        action='store_true',
        help='Initialize as shell, and accept new commands',
    )

    arguments = arg_parser.parse_args(sys.argv[1:])

    #Execute input and run the interpreter
    bf = BrainFuck()
    bf.execute(arguments.cmd)
    if arguments.shell:
        bf.interpreter()

if __name__=="__main__":
    main()
